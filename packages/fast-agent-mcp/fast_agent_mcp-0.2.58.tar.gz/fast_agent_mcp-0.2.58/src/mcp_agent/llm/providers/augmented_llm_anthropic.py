import json
from typing import TYPE_CHECKING, Any, List, Tuple, Type

from mcp.types import TextContent

from mcp_agent.core.prompt import Prompt
from mcp_agent.event_progress import ProgressAction
from mcp_agent.llm.provider_types import Provider
from mcp_agent.llm.providers.multipart_converter_anthropic import (
    AnthropicConverter,
)
from mcp_agent.llm.providers.sampling_converter_anthropic import (
    AnthropicSamplingConverter,
)
from mcp_agent.llm.usage_tracking import TurnUsage
from mcp_agent.mcp.interfaces import ModelT
from mcp_agent.mcp.prompt_message_multipart import PromptMessageMultipart

if TYPE_CHECKING:
    from mcp import ListToolsResult


from anthropic import AsyncAnthropic, AuthenticationError
from anthropic.lib.streaming import AsyncMessageStream
from anthropic.types import (
    Message,
    MessageParam,
    TextBlock,
    TextBlockParam,
    ToolParam,
    ToolUseBlockParam,
    Usage,
)
from mcp.types import (
    CallToolRequest,
    CallToolRequestParams,
    CallToolResult,
    ContentBlock,
)
from rich.text import Text

from mcp_agent.core.exceptions import ProviderKeyError
from mcp_agent.llm.augmented_llm import (
    AugmentedLLM,
    RequestParams,
)
from mcp_agent.logging.logger import get_logger

DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-0"


class AnthropicAugmentedLLM(AugmentedLLM[MessageParam, Message]):
    """
    The basic building block of agentic systems is an LLM enhanced with augmentations
    such as retrieval, tools, and memory provided from a collection of MCP servers.
    Our current models can actively use these capabilities—generating their own search queries,
    selecting appropriate tools, and determining what information to retain.
    """

    # Anthropic-specific parameter exclusions
    ANTHROPIC_EXCLUDE_FIELDS = {
        AugmentedLLM.PARAM_MESSAGES,
        AugmentedLLM.PARAM_MODEL,
        AugmentedLLM.PARAM_SYSTEM_PROMPT,
        AugmentedLLM.PARAM_STOP_SEQUENCES,
        AugmentedLLM.PARAM_MAX_TOKENS,
        AugmentedLLM.PARAM_METADATA,
        AugmentedLLM.PARAM_USE_HISTORY,
        AugmentedLLM.PARAM_MAX_ITERATIONS,
        AugmentedLLM.PARAM_PARALLEL_TOOL_CALLS,
        AugmentedLLM.PARAM_TEMPLATE_VARS,
        AugmentedLLM.PARAM_MCP_METADATA,
    }

    def __init__(self, *args, **kwargs) -> None:
        # Initialize logger - keep it simple without name reference
        self.logger = get_logger(__name__)

        super().__init__(
            *args, provider=Provider.ANTHROPIC, type_converter=AnthropicSamplingConverter, **kwargs
        )

    def _initialize_default_params(self, kwargs: dict) -> RequestParams:
        """Initialize Anthropic-specific default parameters"""
        # Get base defaults from parent (includes ModelDatabase lookup)
        base_params = super()._initialize_default_params(kwargs)

        # Override with Anthropic-specific settings
        chosen_model = kwargs.get("model", DEFAULT_ANTHROPIC_MODEL)
        base_params.model = chosen_model

        return base_params

    def _base_url(self) -> str | None:
        assert self.context.config
        return self.context.config.anthropic.base_url if self.context.config.anthropic else None

    def _get_cache_mode(self) -> str:
        """Get the cache mode configuration."""
        cache_mode = "auto"  # Default to auto
        if self.context.config and self.context.config.anthropic:
            cache_mode = self.context.config.anthropic.cache_mode
        return cache_mode

    async def _prepare_tools(self, structured_model: Type[ModelT] | None = None) -> List[ToolParam]:
        """Prepare tools based on whether we're in structured output mode."""
        if structured_model:
            # JSON mode - create a single tool for structured output
            return [
                ToolParam(
                    name="return_structured_output",
                    description="Return the response in the required JSON format",
                    input_schema=structured_model.model_json_schema(),
                )
            ]
        else:
            # Regular mode - use tools from aggregator
            tool_list: ListToolsResult = await self.aggregator.list_tools()
            return [
                ToolParam(
                    name=tool.name,
                    description=tool.description or "",
                    input_schema=tool.inputSchema,
                )
                for tool in tool_list.tools
            ]

    def _apply_system_cache(self, base_args: dict, cache_mode: str) -> None:
        """Apply cache control to system prompt if cache mode allows it."""
        if cache_mode != "off" and base_args["system"]:
            if isinstance(base_args["system"], str):
                base_args["system"] = [
                    {
                        "type": "text",
                        "text": base_args["system"],
                        "cache_control": {"type": "ephemeral"},
                    }
                ]
                self.logger.debug(
                    "Applied cache_control to system prompt (caches tools+system in one block)"
                )
            else:
                self.logger.debug(f"System prompt is not a string: {type(base_args['system'])}")

    async def _apply_conversation_cache(self, messages: List[MessageParam], cache_mode: str) -> int:
        """Apply conversation caching if in auto mode. Returns number of cache blocks applied."""
        applied_count = 0
        if cache_mode == "auto" and self.history.should_apply_conversation_cache():
            cache_updates = self.history.get_conversation_cache_updates()

            # Remove cache control from old positions
            if cache_updates["remove"]:
                self.history.remove_cache_control_from_messages(messages, cache_updates["remove"])
                self.logger.debug(
                    f"Removed conversation cache_control from positions {cache_updates['remove']}"
                )

            # Add cache control to new positions
            if cache_updates["add"]:
                applied_count = self.history.add_cache_control_to_messages(
                    messages, cache_updates["add"]
                )
                if applied_count > 0:
                    self.history.apply_conversation_cache_updates(cache_updates)
                    self.logger.debug(
                        f"Applied conversation cache_control to positions {cache_updates['add']} ({applied_count} blocks)"
                    )
                else:
                    self.logger.debug(
                        f"Failed to apply conversation cache_control to positions {cache_updates['add']}"
                    )

        return applied_count

    async def _process_structured_output(
        self,
        content_block: Any,
    ) -> Tuple[str, CallToolResult, TextContent]:
        """
        Process a structured output tool call from Anthropic.

        This handles the special case where Anthropic's model was forced to use
        a 'return_structured_output' tool via tool_choice. The tool input contains
        the JSON data we want, so we extract it and format it for display.

        Even though we don't call an external tool, we must create a CallToolResult
        to satisfy Anthropic's API requirement that every tool_use has a corresponding
        tool_result in the next message.

        Returns:
            Tuple of (tool_use_id, tool_result, content_block) for the structured data
        """
        tool_args = content_block.input
        tool_use_id = content_block.id

        # Show the formatted JSON response to the user
        json_response = json.dumps(tool_args, indent=2)
        await self.show_assistant_message(json_response)

        # Create the content for responses
        structured_content = TextContent(type="text", text=json.dumps(tool_args))

        # Create a CallToolResult to satisfy Anthropic's API requirements
        # This represents the "result" of our structured output "tool"
        tool_result = CallToolResult(isError=False, content=[structured_content])

        return tool_use_id, tool_result, structured_content

    async def _process_regular_tool_call(
        self,
        content_block: Any,
        available_tools: List[ToolParam],
        is_first_tool: bool,
        message_text: str | Text,
    ) -> Tuple[str, CallToolResult]:
        """
        Process a regular MCP tool call.

        This handles actual tool execution via the MCP aggregator.
        """
        tool_name = content_block.name
        tool_args = content_block.input
        tool_use_id = content_block.id

        if is_first_tool:
            await self.show_assistant_message(message_text, tool_name)

        self.show_tool_call(available_tools, tool_name, tool_args)
        tool_call_request = CallToolRequest(
            method="tools/call",
            params=CallToolRequestParams(name=tool_name, arguments=tool_args),
        )
        result = await self.call_tool(request=tool_call_request, tool_call_id=tool_use_id)
        self.show_tool_result(result)
        return tool_use_id, result

    async def _process_tool_calls(
        self,
        tool_uses: List[Any],
        available_tools: List[ToolParam],
        message_text: str | Text,
        structured_model: Type[ModelT] | None = None,
    ) -> Tuple[List[Tuple[str, CallToolResult]], List[ContentBlock]]:
        """
        Process tool calls, handling both structured output and regular MCP tools.

        For structured output mode:
        - Extracts JSON data from the forced 'return_structured_output' tool
        - Does NOT create fake CallToolResults
        - Returns the JSON content directly

        For regular tools:
        - Calls actual MCP tools via the aggregator
        - Returns real CallToolResults
        """
        tool_results = []
        responses = []

        for tool_idx, content_block in enumerate(tool_uses):
            tool_name = content_block.name
            is_first_tool = tool_idx == 0

            if tool_name == "return_structured_output" and structured_model:
                # Structured output: extract JSON, don't call external tools
                (
                    tool_use_id,
                    tool_result,
                    structured_content,
                ) = await self._process_structured_output(content_block)
                responses.append(structured_content)
                # Add to tool_results to satisfy Anthropic's API requirement for tool_result messages
                tool_results.append((tool_use_id, tool_result))
            else:
                # Regular tool: call external MCP tool
                tool_use_id, tool_result = await self._process_regular_tool_call(
                    content_block, available_tools, is_first_tool, message_text
                )
                tool_results.append((tool_use_id, tool_result))
                responses.extend(tool_result.content)

        return tool_results, responses

    async def _process_stream(self, stream: AsyncMessageStream, model: str) -> Message:
        """Process the streaming response and display real-time token usage."""
        # Track estimated output tokens by counting text chunks
        estimated_tokens = 0

        # Process the raw event stream to get token counts
        async for event in stream:
            # Count tokens in real-time from content_block_delta events
            if (
                event.type == "content_block_delta"
                and hasattr(event, "delta")
                and event.delta.type == "text_delta"
            ):
                # Use base class method for token estimation and progress emission
                estimated_tokens = self._update_streaming_progress(
                    event.delta.text, model, estimated_tokens
                )

            # Also check for final message_delta events with actual usage info
            elif (
                event.type == "message_delta"
                and hasattr(event, "usage")
                and event.usage.output_tokens
            ):
                actual_tokens = event.usage.output_tokens
                # Emit final progress with actual token count
                token_str = str(actual_tokens).rjust(5)
                data = {
                    "progress_action": ProgressAction.STREAMING,
                    "model": model,
                    "agent_name": self.name,
                    "chat_turn": self.chat_turn(),
                    "details": token_str.strip(),
                }
                self.logger.info("Streaming progress", data=data)

        # Get the final message with complete usage data
        message = await stream.get_final_message()

        # Log final usage information
        if hasattr(message, "usage") and message.usage:
            self.logger.info(
                f"Streaming complete - Model: {model}, Input tokens: {message.usage.input_tokens}, Output tokens: {message.usage.output_tokens}"
            )

        return message

    async def _anthropic_completion(
        self,
        message_param,
        request_params: RequestParams | None = None,
        structured_model: Type[ModelT] | None = None,
    ) -> list[ContentBlock]:
        """
        Process a query using an LLM and available tools.
        Override this method to use a different LLM.
        """

        api_key = self._api_key()
        base_url = self._base_url()
        if base_url and base_url.endswith("/v1"):
            base_url = base_url.rstrip("/v1")

        try:
            anthropic = AsyncAnthropic(api_key=api_key, base_url=base_url)
            messages: List[MessageParam] = []
            params = self.get_request_params(request_params)
        except AuthenticationError as e:
            raise ProviderKeyError(
                "Invalid Anthropic API key",
                "The configured Anthropic API key was rejected.\nPlease check that your API key is valid and not expired.",
            ) from e

        # Always include prompt messages, but only include conversation history
        # if use_history is True
        messages.extend(self.history.get(include_completion_history=params.use_history))

        messages.append(message_param)  # message_param is the current user turn

        # Get cache mode configuration
        cache_mode = self._get_cache_mode()
        self.logger.debug(f"Anthropic cache_mode: {cache_mode}")

        available_tools = await self._prepare_tools(structured_model)

        responses: List[ContentBlock] = []

        model = self.default_request_params.model

        # Note: We'll cache tools+system together by putting cache_control only on system prompt

        for i in range(params.max_iterations):
            self._log_chat_progress(self.chat_turn(), model=model)

            # Create base arguments dictionary
            base_args = {
                "model": model,
                "messages": messages,
                "system": self.instruction or params.systemPrompt,
                "stop_sequences": params.stopSequences,
                "tools": available_tools,
            }

            # Add tool_choice for structured output mode
            if structured_model:
                base_args["tool_choice"] = {"type": "tool", "name": "return_structured_output"}

            # Apply cache control to system prompt
            self._apply_system_cache(base_args, cache_mode)

            # Apply conversation caching
            applied_count = await self._apply_conversation_cache(messages, cache_mode)

            # Verify we don't exceed Anthropic's 4 cache block limit
            if applied_count > 0:
                total_cache_blocks = applied_count
                if cache_mode != "off" and base_args["system"]:
                    total_cache_blocks += 1  # tools+system cache block
                if total_cache_blocks > 4:
                    self.logger.warning(
                        f"Total cache blocks ({total_cache_blocks}) exceeds Anthropic limit of 4"
                    )

            if params.maxTokens is not None:
                base_args["max_tokens"] = params.maxTokens

            # Use the base class method to prepare all arguments with Anthropic-specific exclusions
            arguments = self.prepare_provider_arguments(
                base_args, params, self.ANTHROPIC_EXCLUDE_FIELDS
            )

            self.logger.debug(f"{arguments}")

            # Use streaming API with helper
            async with anthropic.messages.stream(**arguments) as stream:
                # Process the stream
                response = await self._process_stream(stream, model)

            # Track usage if response is valid and has usage data
            if (
                hasattr(response, "usage")
                and response.usage
                and not isinstance(response, BaseException)
            ):
                try:
                    turn_usage = TurnUsage.from_anthropic(
                        response.usage, model or DEFAULT_ANTHROPIC_MODEL
                    )
                    self._finalize_turn_usage(turn_usage)
                #                    self._show_usage(response.usage, turn_usage)
                except Exception as e:
                    self.logger.warning(f"Failed to track usage: {e}")

            if isinstance(response, AuthenticationError):
                raise ProviderKeyError(
                    "Invalid Anthropic API key",
                    "The configured Anthropic API key was rejected.\nPlease check that your API key is valid and not expired.",
                ) from response
            elif isinstance(response, BaseException):
                error_details = str(response)
                self.logger.error(f"Error: {error_details}", data=BaseException)

                # Try to extract more useful information for API errors
                if hasattr(response, "status_code") and hasattr(response, "response"):
                    try:
                        error_json = response.response.json()
                        error_details = f"Error code: {response.status_code} - {error_json}"
                    except:  # noqa: E722
                        error_details = f"Error code: {response.status_code} - {str(response)}"

                # Convert other errors to text response
                error_message = f"Error during generation: {error_details}"
                response = Message(
                    id="error",
                    model="error",
                    role="assistant",
                    type="message",
                    content=[TextBlock(type="text", text=error_message)],
                    stop_reason="end_turn",
                    usage=Usage(input_tokens=0, output_tokens=0),
                )

            self.logger.debug(
                f"{model} response:",
                data=response,
            )

            response_as_message = self.convert_message_to_message_param(response)
            messages.append(response_as_message)
            if response.content and response.content[0].type == "text":
                responses.append(TextContent(type="text", text=response.content[0].text))

            if response.stop_reason == "end_turn":
                message_text = ""
                for block in response_as_message["content"]:
                    if isinstance(block, dict) and block.get("type") == "text":
                        message_text += block.get("text", "")
                    elif hasattr(block, "type") and block.type == "text":
                        message_text += block.text

                await self.show_assistant_message(message_text)

                self.logger.debug(f"Iteration {i}: Stopping because finish_reason is 'end_turn'")
                break
            elif response.stop_reason == "stop_sequence":
                # We have reached a stop sequence
                self.logger.debug(
                    f"Iteration {i}: Stopping because finish_reason is 'stop_sequence'"
                )
                break
            elif response.stop_reason == "max_tokens":
                # We have reached the max tokens limit

                self.logger.debug(f"Iteration {i}: Stopping because finish_reason is 'max_tokens'")
                if params.maxTokens is not None:
                    message_text = Text(
                        f"the assistant has reached the maximum token limit ({params.maxTokens})",
                        style="dim green italic",
                    )
                else:
                    message_text = Text(
                        "the assistant has reached the maximum token limit",
                        style="dim green italic",
                    )

                await self.show_assistant_message(message_text)

                break
            else:
                message_text = ""
                for block in response_as_message["content"]:
                    if isinstance(block, dict) and block.get("type") == "text":
                        message_text += block.get("text", "")
                    elif hasattr(block, "type") and block.type == "text":
                        message_text += block.text

                # response.stop_reason == "tool_use":
                # First, collect all tool uses in this turn
                tool_uses = [c for c in response.content if c.type == "tool_use"]

                if tool_uses:
                    if message_text == "":
                        message_text = Text(
                            "the assistant requested tool calls",
                            style="dim green italic",
                        )

                    # Process all tool calls using the helper method
                    tool_results, tool_responses = await self._process_tool_calls(
                        tool_uses, available_tools, message_text, structured_model
                    )
                    responses.extend(tool_responses)

                    # Always add tool_results_message first (required by Anthropic API)
                    messages.append(AnthropicConverter.create_tool_results_message(tool_results))

                    # For structured output, we have our result and should exit after sending tool_result
                    if structured_model and any(
                        tool.name == "return_structured_output" for tool in tool_uses
                    ):
                        self.logger.debug("Structured output received, breaking iteration loop")
                        break

        # Only save the new conversation messages to history if use_history is true
        # Keep the prompt messages separate
        if params.use_history:
            # Get current prompt messages
            prompt_messages = self.history.get(include_completion_history=False)
            new_messages = messages[len(prompt_messages) :]
            self.history.set(new_messages)

        self._log_chat_finished(model=model)

        return responses

    async def generate_messages(
        self,
        message_param,
        request_params: RequestParams | None = None,
    ) -> PromptMessageMultipart:
        """
        Process a query using an LLM and available tools.
        The default implementation uses Claude as the LLM.
        Override this method to use a different LLM.

        """
        # Reset tool call counter for new turn
        self._reset_turn_tool_calls()

        res = await self._anthropic_completion(
            message_param=message_param,
            request_params=request_params,
        )
        return Prompt.assistant(*res)

    async def _apply_prompt_provider_specific(
        self,
        multipart_messages: List["PromptMessageMultipart"],
        request_params: RequestParams | None = None,
        is_template: bool = False,
    ) -> PromptMessageMultipart:
        # Check the last message role
        last_message = multipart_messages[-1]

        # Add all previous messages to history (or all messages if last is from assistant)
        messages_to_add = (
            multipart_messages[:-1] if last_message.role == "user" else multipart_messages
        )
        converted = []

        # Get cache mode configuration
        cache_mode = self._get_cache_mode()

        for msg in messages_to_add:
            anthropic_msg = AnthropicConverter.convert_to_anthropic(msg)

            # Apply caching to template messages if cache_mode is "prompt" or "auto"
            if is_template and cache_mode in ["prompt", "auto"] and anthropic_msg.get("content"):
                content_list = anthropic_msg["content"]
                if isinstance(content_list, list) and content_list:
                    # Apply cache control to the last content block
                    last_block = content_list[-1]
                    if isinstance(last_block, dict):
                        last_block["cache_control"] = {"type": "ephemeral"}
                        self.logger.debug(
                            f"Applied cache_control to template message with role {anthropic_msg.get('role')}"
                        )

            converted.append(anthropic_msg)

        self.history.extend(converted, is_prompt=is_template)

        if last_message.role == "user":
            self.logger.debug("Last message in prompt is from user, generating assistant response")
            message_param = AnthropicConverter.convert_to_anthropic(last_message)
            return await self.generate_messages(message_param, request_params)
        else:
            # For assistant messages: Return the last message content as text
            self.logger.debug("Last message in prompt is from assistant, returning it directly")
            return last_message

    async def _apply_prompt_provider_specific_structured(
        self,
        multipart_messages: List[PromptMessageMultipart],
        model: Type[ModelT],
        request_params: RequestParams | None = None,
    ) -> Tuple[ModelT | None, PromptMessageMultipart]:  # noqa: F821
        request_params = self.get_request_params(request_params)

        # Check the last message role
        last_message = multipart_messages[-1]

        # Add all previous messages to history (or all messages if last is from assistant)
        messages_to_add = (
            multipart_messages[:-1] if last_message.role == "user" else multipart_messages
        )
        converted = []

        for msg in messages_to_add:
            anthropic_msg = AnthropicConverter.convert_to_anthropic(msg)
            converted.append(anthropic_msg)

        self.history.extend(converted, is_prompt=False)

        if last_message.role == "user":
            self.logger.debug("Last message in prompt is from user, generating structured response")
            message_param = AnthropicConverter.convert_to_anthropic(last_message)

            # Call _anthropic_completion with the structured model
            response_content = await self._anthropic_completion(
                message_param, request_params, structured_model=model
            )

            # Extract the structured data from the response
            for content in response_content:
                if content.type == "text":
                    try:
                        # Parse the JSON response from the tool
                        data = json.loads(content.text)
                        parsed_model = model(**data)
                        # Create assistant response
                        assistant_response = Prompt.assistant(content)
                        return parsed_model, assistant_response
                    except (json.JSONDecodeError, ValueError) as e:
                        self.logger.error(f"Failed to parse structured output: {e}")
                        assistant_response = Prompt.assistant(content)
                        return None, assistant_response

            # If no valid response found
            return None, Prompt.assistant()
        else:
            # For assistant messages: Return the last message content
            self.logger.debug("Last message in prompt is from assistant, returning it directly")
            return None, last_message

    def _show_usage(self, raw_usage: Usage, turn_usage: TurnUsage) -> None:
        # Print raw usage for debugging
        print(f"\n=== USAGE DEBUG ({turn_usage.model}) ===")
        print(f"Raw usage: {raw_usage}")
        print(
            f"Turn usage: input={turn_usage.input_tokens}, output={turn_usage.output_tokens}, current_context={turn_usage.current_context_tokens}"
        )
        print(
            f"Cache: read={turn_usage.cache_usage.cache_read_tokens}, write={turn_usage.cache_usage.cache_write_tokens}"
        )
        print(f"Effective input: {turn_usage.effective_input_tokens}")
        print(
            f"Accumulator: total_turns={self.usage_accumulator.turn_count}, cumulative_billing={self.usage_accumulator.cumulative_billing_tokens}, current_context={self.usage_accumulator.current_context_tokens}"
        )
        if self.usage_accumulator.context_usage_percentage:
            print(
                f"Context usage: {self.usage_accumulator.context_usage_percentage:.1f}% of {self.usage_accumulator.context_window_size}"
            )
        if self.usage_accumulator.cache_hit_rate:
            print(f"Cache hit rate: {self.usage_accumulator.cache_hit_rate:.1f}%")
        print("===========================\n")

    @classmethod
    def convert_message_to_message_param(cls, message: Message, **kwargs) -> MessageParam:
        """Convert a response object to an input parameter object to allow LLM calls to be chained."""
        content = []

        for content_block in message.content:
            if content_block.type == "text":
                content.append(TextBlockParam(type="text", text=content_block.text))
            elif content_block.type == "tool_use":
                content.append(
                    ToolUseBlockParam(
                        type="tool_use",
                        name=content_block.name,
                        input=content_block.input,
                        id=content_block.id,
                    )
                )

        return MessageParam(role="assistant", content=content, **kwargs)
