"""
Markdown-Flow Core Business Logic

Refactored MarkdownFlow class with built-in LLM processing capabilities and unified process interface.
"""

import re
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from .constants import (
    BLOCK_SEPARATOR,
    BLOCK_INDEX_OUT_OF_RANGE_ERROR,
    BUTTONS_WITH_TEXT_VALIDATION_TEMPLATE,
    COMPILED_BRACKETS_CLEANUP_REGEX,
    COMPILED_INTERACTION_CONTENT_RECONSTRUCT_REGEX,
    COMPILED_VARIABLE_REFERENCE_CLEANUP_REGEX,
    COMPILED_WHITESPACE_CLEANUP_REGEX,
    DEFAULT_INTERACTION_ERROR_PROMPT,
    DEFAULT_INTERACTION_PROMPT,
    DEFAULT_VALIDATION_SYSTEM_MESSAGE,
    INPUT_EMPTY_ERROR,
    INTERACTION_ERROR_RENDER_INSTRUCTIONS,
    INTERACTION_PARSE_ERROR,
    INTERACTION_PATTERN_NON_CAPTURING,
    INTERACTION_PATTERN_SPLIT,
    INTERACTION_RENDER_INSTRUCTIONS,
    LLM_PROVIDER_REQUIRED_ERROR,
    OPTION_SELECTION_ERROR_TEMPLATE,
    UNSUPPORTED_PROMPT_TYPE_ERROR,
)
from .enums import BlockType
from .exceptions import BlockIndexError
from .llm import LLMProvider, LLMResult, ProcessMode
from .models import Block, InteractionValidationConfig
from .utils import (
    InteractionParser,
    InteractionType,
    extract_interaction_question,
    extract_preserved_content,
    extract_variables_from_text,
    is_preserved_content_block,
    parse_validation_response,
    process_output_instructions,
    replace_variables_in_text,
)


class MarkdownFlow:
    """
    Refactored Markdown-Flow core class.

    Integrates all document processing and LLM interaction capabilities with a unified process interface.
    """

    def __init__(
        self,
        document: str,
        llm_provider: Optional[LLMProvider] = None,
        document_prompt: Optional[str] = None,
        interaction_prompt: Optional[str] = None,
        interaction_error_prompt: Optional[str] = None,
    ):
        """
        Initialize MarkdownFlow instance.

        Args:
            document: Markdown document content
            llm_provider: LLM provider, if None only PROMPT_ONLY mode is available
            document_prompt: Document-level system prompt
            interaction_prompt: Interaction content rendering prompt
            interaction_error_prompt: Interaction error rendering prompt
        """
        self._document = document
        self._llm_provider = llm_provider
        self._document_prompt = document_prompt
        self._interaction_prompt = interaction_prompt or DEFAULT_INTERACTION_PROMPT
        self._interaction_error_prompt = (
            interaction_error_prompt or DEFAULT_INTERACTION_ERROR_PROMPT
        )
        self._blocks = None
        self._interaction_configs: Dict[int, InteractionValidationConfig] = {}

    def set_llm_provider(self, provider: LLMProvider) -> None:
        """Set LLM provider."""
        self._llm_provider = provider

    def set_prompt(self, prompt_type: str, value: Optional[str]) -> None:
        """
        Set prompt template.

        Args:
            prompt_type: Prompt type ('document', 'interaction', 'interaction_error')
            value: Prompt content
        """
        if prompt_type == "document":
            self._document_prompt = value
        elif prompt_type == "interaction":
            self._interaction_prompt = value or DEFAULT_INTERACTION_PROMPT
        elif prompt_type == "interaction_error":
            self._interaction_error_prompt = value or DEFAULT_INTERACTION_ERROR_PROMPT
        else:
            raise ValueError(UNSUPPORTED_PROMPT_TYPE_ERROR.format(prompt_type=prompt_type))

    @property
    def document(self) -> str:
        """Get document content."""
        return self._document

    @property
    def block_count(self) -> int:
        """Get total number of blocks."""
        return len(self.get_all_blocks())

    def get_all_blocks(self) -> List[Block]:
        """Parse document and get all blocks."""
        if self._blocks is not None:
            return self._blocks

        content = self._document.strip()
        segments = re.split(BLOCK_SEPARATOR, content)
        final_blocks = []

        for segment in segments:
            # Use dedicated split pattern to avoid duplicate blocks from capturing groups
            parts = re.split(INTERACTION_PATTERN_SPLIT, segment)

            for part in parts:
                part = part.strip()
                if part:
                    # Use non-capturing pattern for matching
                    if re.match(INTERACTION_PATTERN_NON_CAPTURING, part):
                        block = Block(
                            content=part,
                            block_type=BlockType.INTERACTION,
                            index=len(final_blocks),
                        )
                        final_blocks.append(block)
                    else:
                        if is_preserved_content_block(part):
                            block_type = BlockType.PRESERVED_CONTENT
                        else:
                            block_type = BlockType.CONTENT

                        block = Block(
                            content=part, block_type=block_type, index=len(final_blocks)
                        )
                        final_blocks.append(block)

        self._blocks = final_blocks
        return self._blocks

    def get_block(self, index: int) -> Block:
        """Get block at specified index."""
        blocks = self.get_all_blocks()
        if index < 0 or index >= len(blocks):
            raise BlockIndexError(BLOCK_INDEX_OUT_OF_RANGE_ERROR.format(index=index, len=len(blocks)))
        return blocks[index]

    def extract_variables(self) -> List[str]:
        """Extract all variable names from the document."""
        return extract_variables_from_text(self._document)

    def set_interaction_validation_config(
        self, block_index: int, config: InteractionValidationConfig
    ) -> None:
        """Set validation config for specified interaction block."""
        self._interaction_configs[block_index] = config

    def get_interaction_validation_config(
        self, block_index: int
    ) -> Optional[InteractionValidationConfig]:
        """Get validation config for specified interaction block."""
        return self._interaction_configs.get(block_index)

    # Core unified interface

    async def process(
        self,
        block_index: int,
        mode: ProcessMode = ProcessMode.COMPLETE,
        context: Optional[List[Dict[str, str]]] = None,
        variables: Optional[Dict[str, str]] = None,
        user_input: Optional[str] = None,
    ) -> Union[LLMResult, AsyncGenerator[LLMResult, None]]:
        """
        Unified block processing interface.

        Args:
            block_index: Block index
            mode: Processing mode
            context: Context message list
            variables: Variable mappings
            user_input: User input (for interaction blocks)

        Returns:
            LLMResult or AsyncGenerator[LLMResult, None]
        """
        # Process document_prompt variable replacement
        if self._document_prompt:
            self._document_prompt = replace_variables_in_text(
                self._document_prompt, variables or {}
            )

        block = self.get_block(block_index)

        if block.block_type == BlockType.CONTENT:
            return await self._process_content(block_index, mode, context, variables)

        elif block.block_type == BlockType.INTERACTION:
            if user_input is None:
                # Render interaction content
                return await self._process_interaction_render(block_index, mode)
            else:
                # Process user input
                return await self._process_interaction_input(
                    block_index, user_input, mode, context
                )

        elif block.block_type == BlockType.PRESERVED_CONTENT:
            # Preserved content output as-is, no LLM call
            return await self._process_preserved_content(block_index, variables)

        else:
            # Handle other types as content
            return await self._process_content(block_index, mode, context, variables)

    # Internal processing methods

    async def _process_content(
        self,
        block_index: int,
        mode: ProcessMode,
        context: Optional[List[Dict[str, str]]],
        variables: Optional[Dict[str, str]],
    ) -> Union[LLMResult, AsyncGenerator[LLMResult, None]]:
        """Process content block."""
        # Build messages
        messages = self._build_content_messages(block_index, variables)

        if mode == ProcessMode.PROMPT_ONLY:
            return LLMResult(
                prompt=messages[-1]["content"], metadata={"messages": messages}
            )

        elif mode == ProcessMode.COMPLETE:
            if not self._llm_provider:
                raise ValueError(LLM_PROVIDER_REQUIRED_ERROR)

            content = await self._llm_provider.complete(messages)
            return LLMResult(content=content, prompt=messages[-1]["content"])

        elif mode == ProcessMode.STREAM:
            if not self._llm_provider:
                raise ValueError(LLM_PROVIDER_REQUIRED_ERROR)

            async def stream_generator():
                async for chunk in self._llm_provider.stream(messages):
                    yield LLMResult(content=chunk, prompt=messages[-1]["content"])

            return stream_generator()

    async def _process_preserved_content(
        self, block_index: int, variables: Optional[Dict[str, str]]
    ) -> LLMResult:
        """Process preserved content block, output as-is without LLM call."""
        block = self.get_block(block_index)

        # Extract preserved content (remove === markers)
        content = extract_preserved_content(block.content)

        # Replace variables
        content = replace_variables_in_text(
            content, variables or {}
        )

        return LLMResult(content=content)

    async def _process_interaction_render(
        self, block_index: int, mode: ProcessMode
    ) -> Union[LLMResult, AsyncGenerator[LLMResult, None]]:
        """Process interaction content rendering."""
        block = self.get_block(block_index)

        # Extract question text
        question_text = extract_interaction_question(block.content)
        if not question_text:
            # Unable to extract, return original content
            return LLMResult(content=block.content)

        # Build render messages
        messages = self._build_interaction_render_messages(question_text)

        if mode == ProcessMode.PROMPT_ONLY:
            return LLMResult(
                prompt=messages[-1]["content"],
                metadata={
                    "original_content": block.content,
                    "question_text": question_text,
                },
            )

        elif mode == ProcessMode.COMPLETE:
            if not self._llm_provider:
                return LLMResult(content=block.content)  # Fallback processing

            rendered_question = await self._llm_provider.complete(messages)
            rendered_content = self._reconstruct_interaction_content(
                block.content, rendered_question
            )

            return LLMResult(
                content=rendered_content,
                prompt=messages[-1]["content"],
                metadata={
                    "original_question": question_text,
                    "rendered_question": rendered_question,
                },
            )

        elif mode == ProcessMode.STREAM:
            if not self._llm_provider:
                # For interaction blocks, return reconstructed content (one-time output)
                rendered_content = self._reconstruct_interaction_content(
                    block.content, question_text or ""
                )

                async def stream_generator():
                    yield LLMResult(
                        content=rendered_content,
                        prompt=messages[-1]["content"],
                    )

                return stream_generator()

            # With LLM provider, collect full response then return once
            async def stream_generator():
                full_response = ""
                async for chunk in self._llm_provider.stream(messages):
                    full_response += chunk

                # Reconstruct final interaction content
                rendered_content = self._reconstruct_interaction_content(
                    block.content, full_response
                )

                # Return complete content at once, not incrementally
                yield LLMResult(
                    content=rendered_content,
                    prompt=messages[-1]["content"],
                )

            return stream_generator()

    async def _process_interaction_input(
        self,
        block_index: int,
        user_input: str,
        mode: ProcessMode,
        context: Optional[List[Dict[str, str]]],
    ) -> Union[LLMResult, AsyncGenerator[LLMResult, None]]:
        """Process interaction user input."""
        block = self.get_block(block_index)
        target_variable = block.variables[0] if block.variables else "user_input"

        # Basic validation
        if not user_input.strip():
            error_msg = INPUT_EMPTY_ERROR
            return await self._render_error(error_msg, mode)

        # Parse interaction format
        parser = InteractionParser()
        parse_result = parser.parse(block.content)

        if 'error' in parse_result:
            error_msg = INTERACTION_PARSE_ERROR.format(error=parse_result['error'])
            return await self._render_error(error_msg, mode)

        interaction_type = parse_result.get('type')

        # Process user input based on interaction type
        if interaction_type == InteractionType.BUTTONS_ONLY:
            # Button-only: ?[%{{var}} A|B] or ?[%{{var}} A//1|B//2]
            return await self._process_button_validation(
                parse_result, user_input, target_variable, mode,
                block_index, allow_text_input=False
            )

        elif interaction_type == InteractionType.BUTTONS_WITH_TEXT:
            # Buttons with text: ?[%{{var}} A|B|...question]
            return await self._process_button_validation(
                parse_result, user_input, target_variable, mode,
                block_index, allow_text_input=True
            )

        elif interaction_type == InteractionType.NON_ASSIGNMENT_BUTTON:
            # Non-assignment buttons: ?[Continue] or ?[Continue|Cancel]
            buttons = parse_result.get("buttons", [])
            user_input_stripped = user_input.strip()

            # Check if user input matches any button (display or actual value)
            for button in buttons:
                if user_input_stripped in [button["display"], button["value"]]:
                    return LLMResult(
                        content="",  # Empty content indicates interaction complete
                        variables={},  # Non-assignment buttons don't set variables
                        metadata={
                            "interaction_type": "non_assignment_button",
                            "button_clicked": button,
                            "user_input": user_input_stripped,
                        }
                    )

            # User input doesn't match any button
            button_displays = [btn["display"] for btn in buttons]
            error_msg = OPTION_SELECTION_ERROR_TEMPLATE.format(options=', '.join(button_displays))
            return await self._render_error(error_msg, mode)

        else:
            # Text-only input type: ?[%{{sys_user_nickname}}...question]
            # Check if LLM validation is needed
            validation_config = self.get_interaction_validation_config(block_index)

            if validation_config and not validation_config.enable_custom_validation:
                # Custom validation explicitly disabled, return variables directly
                return LLMResult(
                    content="",  # Empty content indicates successful variable extraction
                    variables={target_variable: user_input.strip()},
                )
            else:
                # Default enable LLM validation (even without configuration)
                return await self._process_llm_validation(
                    block_index, user_input, target_variable, mode
                )

    async def _process_llm_validation(
        self,
        block_index: int,
        user_input: str,
        target_variable: str,
        mode: ProcessMode,
    ) -> Union[LLMResult, AsyncGenerator[LLMResult, None]]:
        """Process LLM validation."""
        # Build validation messages
        messages = self._build_validation_messages(
            block_index, user_input, target_variable
        )

        if mode == ProcessMode.PROMPT_ONLY:
            return LLMResult(
                prompt=messages[-1]["content"],
                metadata={
                    "validation_target": user_input,
                    "target_variable": target_variable,
                },
            )

        elif mode == ProcessMode.COMPLETE:
            if not self._llm_provider:
                # Fallback processing, return variables directly
                return LLMResult(
                    content="", variables={target_variable: user_input.strip()}
                )

            llm_response = await self._llm_provider.complete(messages)

            # Parse validation response and convert to LLMResult
            parsed_result = parse_validation_response(
                llm_response, user_input, target_variable
            )
            return LLMResult(
                content=parsed_result["content"], variables=parsed_result["variables"]
            )

        elif mode == ProcessMode.STREAM:
            if not self._llm_provider:
                return LLMResult(
                    content="", variables={target_variable: user_input.strip()}
                )

            async def stream_generator():
                full_response = ""
                async for chunk in self._llm_provider.stream(messages):
                    full_response += chunk

                # Parse complete response and convert to LLMResult
                parsed_result = parse_validation_response(
                    full_response, user_input, target_variable
                )
                yield LLMResult(
                    content=parsed_result["content"],
                    variables=parsed_result["variables"],
                )

            return stream_generator()

    async def _process_button_validation(
        self,
        parse_result: Dict[str, Any],
        user_input: str,
        target_variable: str,
        mode: ProcessMode,
        block_index: int,
        allow_text_input: bool = False
    ) -> Union[LLMResult, AsyncGenerator[LLMResult, None]]:
        """
        Process button validation logic with display/value separation support.

        Args:
            parse_result: InteractionParser result containing buttons list
            user_input: User input
            target_variable: Target variable name  
            mode: Processing mode
            block_index: Block index
            allow_text_input: Whether to allow text input (buttons+text mode)
        """
        buttons = parse_result.get("buttons", [])
        user_input_stripped = user_input.strip()

        # First check if user input matches any button
        for button in buttons:
            # Check display value and actual value
            if user_input_stripped in [button["display"], button["value"]]:
                # Use actual value as variable value
                return LLMResult(
                    content="",  # Empty content indicates successful variable extraction
                    variables={target_variable: button["value"]},
                    metadata={
                        "button_clicked": button,
                        "user_input_display": button["display"],
                        "user_input_value": button["value"],
                    }
                )

        # User input doesn't match any button
        if not allow_text_input:
            # Pure button mode, return error
            button_displays = [btn["display"] for btn in buttons]
            error_msg = OPTION_SELECTION_ERROR_TEMPLATE.format(options=', '.join(button_displays))
            return await self._render_error(error_msg, mode)
        else:
            # Button+text mode, use LLM to process text input
            button_options = [btn["display"] for btn in buttons]
            return await self._process_llm_validation_with_options(
                block_index,
                user_input,
                target_variable,
                button_options,  # Pass display values for LLM understanding
                parse_result.get("question", ""),
                mode,
            )

    async def _process_llm_validation_with_options(
        self,
        block_index: int,
        user_input: str,
        target_variable: str,
        options: List[str],
        question: str,
        mode: ProcessMode,
    ) -> Union[LLMResult, AsyncGenerator[LLMResult, None]]:
        """Process LLM validation with button options (third case)."""
        # Build special validation messages containing button option information
        messages = self._build_validation_messages_with_options(
            user_input, target_variable, options, question
        )

        if mode == ProcessMode.PROMPT_ONLY:
            return LLMResult(
                prompt=messages[-1]["content"],
                metadata={
                    "validation_target": user_input,
                    "target_variable": target_variable,
                    "options": options,
                    "question": question,
                },
            )

        elif mode == ProcessMode.COMPLETE:
            if not self._llm_provider:
                # Fallback processing, return variables directly
                return LLMResult(
                    content="", variables={target_variable: user_input.strip()}
                )

            llm_response = await self._llm_provider.complete(messages)

            # Parse validation response and convert to LLMResult
            parsed_result = parse_validation_response(
                llm_response, user_input, target_variable
            )
            return LLMResult(
                content=parsed_result["content"], variables=parsed_result["variables"]
            )

        elif mode == ProcessMode.STREAM:
            if not self._llm_provider:
                return LLMResult(
                    content="", variables={target_variable: user_input.strip()}
                )

            async def stream_generator():
                full_response = ""
                async for chunk in self._llm_provider.stream(messages):
                    full_response += chunk
                    # For validation scenario, don't output chunks in real-time, only final result

                # Process final response
                parsed_result = parse_validation_response(
                    full_response, user_input, target_variable
                )

                # Return only final parsing result
                yield LLMResult(
                    content=parsed_result["content"],
                    variables=parsed_result["variables"],
                )

            return stream_generator()

    async def _render_error(
        self, error_message: str, mode: ProcessMode
    ) -> Union[LLMResult, AsyncGenerator[LLMResult, None]]:
        """Render user-friendly error message."""
        messages = self._build_error_render_messages(error_message)

        if mode == ProcessMode.PROMPT_ONLY:
            return LLMResult(
                prompt=messages[-1]["content"],
                metadata={"original_error": error_message},
            )

        elif mode == ProcessMode.COMPLETE:
            if not self._llm_provider:
                return LLMResult(content=error_message)  # Fallback processing

            friendly_error = await self._llm_provider.complete(messages)
            return LLMResult(content=friendly_error, prompt=messages[-1]["content"])

        elif mode == ProcessMode.STREAM:
            if not self._llm_provider:
                return LLMResult(content=error_message)

            async def stream_generator():
                async for chunk in self._llm_provider.stream(messages):
                    yield LLMResult(content=chunk, prompt=messages[-1]["content"])

            return stream_generator()

    # Message building helpers

    def _build_content_messages(
        self,
        block_index: int,
        variables: Optional[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        """Build content block messages."""
        block = self.get_block(block_index)
        block_content = block.content

        # Process output instructions
        block_content = process_output_instructions(block_content)

        # Replace variables
        block_content = replace_variables_in_text(
            block_content, variables or {}
        )

        # Build message array
        messages = []

        # Add document prompt
        if self._document_prompt:
            messages.append({"role": "system", "content": self._document_prompt})

        # For most content blocks, historical conversation context is not needed
        # because each document block is an independent instruction
        # If future specific scenarios need context, logic can be added here
        # if context:
        #     messages.extend(context)

        # Add processed content as user message (as instruction to LLM)
        messages.append({"role": "user", "content": block_content})

        return messages

    def _build_interaction_render_messages(
        self, question_text: str
    ) -> List[Dict[str, str]]:
        """Build interaction rendering messages."""
        # Check if using custom interaction prompt
        if self._interaction_prompt != DEFAULT_INTERACTION_PROMPT:
            # User custom prompt + mandatory direction protection
            render_prompt = f"""{self._interaction_prompt}"""
        else:
            # Use default prompt and instructions
            render_prompt = f"""{self._interaction_prompt}
{INTERACTION_RENDER_INSTRUCTIONS}"""

        messages = []

        messages.append({"role": "system", "content": render_prompt})
        messages.append({"role": "user", "content": question_text})

        return messages

    def _build_validation_messages(
        self, block_index: int, user_input: str, target_variable: str
    ) -> List[Dict[str, str]]:
        """Build validation messages."""
        block = self.get_block(block_index)
        config = self.get_interaction_validation_config(block_index)

        if config and config.validation_template:
            # Use custom validation template
            validation_prompt = config.validation_template
            validation_prompt = validation_prompt.replace(
                "{sys_user_input}", user_input
            )
            validation_prompt = validation_prompt.replace(
                "{block_content}", block.content
            )
            validation_prompt = validation_prompt.replace(
                "{target_variable}", target_variable
            )
            system_message = DEFAULT_VALIDATION_SYSTEM_MESSAGE
        else:
            # Use smart default validation template
            from .utils import (
                extract_interaction_question,
                generate_smart_validation_template,
            )

            # Extract interaction question
            interaction_question = extract_interaction_question(block.content)

            # Generate smart validation template
            validation_template = generate_smart_validation_template(
                target_variable,
                context=None,  # Could consider passing context here
                interaction_question=interaction_question,
            )

            # Replace template variables
            validation_prompt = validation_template.replace(
                "{sys_user_input}", user_input
            )
            validation_prompt = validation_prompt.replace(
                "{block_content}", block.content
            )
            validation_prompt = validation_prompt.replace(
                "{target_variable}", target_variable
            )
            system_message = DEFAULT_VALIDATION_SYSTEM_MESSAGE

        messages = []

        messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": validation_prompt})

        return messages

    def _build_validation_messages_with_options(
        self,
        user_input: str,
        target_variable: str,
        options: List[str],
        question: str,
    ) -> List[Dict[str, str]]:
        """Build validation messages with button options (third case)."""
        # Use validation template from constants
        validation_prompt = BUTTONS_WITH_TEXT_VALIDATION_TEMPLATE.format(
            question=question,
            options=", ".join(options),
            user_input=user_input,
            target_variable=target_variable,
        )

        messages = []
        if self._document_prompt:
            messages.append({"role": "system", "content": self._document_prompt})

        messages.append(
            {"role": "system", "content": DEFAULT_VALIDATION_SYSTEM_MESSAGE}
        )
        messages.append({"role": "user", "content": validation_prompt})

        return messages

    def _build_error_render_messages(self, error_message: str) -> List[Dict[str, str]]:
        """Build error rendering messages."""
        render_prompt = f"""{self._interaction_error_prompt}

Original Error: {error_message}

{INTERACTION_ERROR_RENDER_INSTRUCTIONS}"""

        messages = []
        if self._document_prompt:
            messages.append({"role": "system", "content": self._document_prompt})

        messages.append({"role": "system", "content": render_prompt})
        messages.append({"role": "user", "content": error_message})

        return messages

    # Helper methods

    def _reconstruct_interaction_content(
        self, original_content: str, rendered_question: str
    ) -> str:
        """Reconstruct interaction content."""
        cleaned_question = rendered_question.strip()
        # Use pre-compiled regex for improved performance
        cleaned_question = COMPILED_BRACKETS_CLEANUP_REGEX.sub("", cleaned_question)
        cleaned_question = COMPILED_VARIABLE_REFERENCE_CLEANUP_REGEX.sub(
            "", cleaned_question
        )
        cleaned_question = COMPILED_WHITESPACE_CLEANUP_REGEX.sub(
            " ", cleaned_question
        ).strip()

        match = COMPILED_INTERACTION_CONTENT_RECONSTRUCT_REGEX.search(original_content)

        if match:
            prefix = match.group(1)
            suffix = match.group(2)
            return f"{prefix}{cleaned_question}{suffix}"
        else:
            return original_content
