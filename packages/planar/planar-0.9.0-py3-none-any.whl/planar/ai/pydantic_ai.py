import base64
import json
import os
import re
import textwrap
from typing import Any, Type, cast

from pydantic import BaseModel, ValidationError
from pydantic_ai import BinaryContent
from pydantic_ai._output import OutputObjectDefinition, OutputToolset
from pydantic_ai.direct import model_request_stream
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelRequestPart,
    ModelResponse,
    ModelResponsePart,
    PartDeltaEvent,
    PartStartEvent,
    RetryPromptPart,
    SystemPromptPart,
    TextPart,
    TextPartDelta,
    ThinkingPart,
    ThinkingPartDelta,
    ToolCallPart,
    ToolCallPartDelta,
    ToolReturnPart,
    UserContent,
    UserPromptPart,
)
from pydantic_ai.models import KnownModelName, Model, ModelRequestParameters
from pydantic_ai.settings import ModelSettings
from pydantic_ai.tools import ToolDefinition
from pydantic_core import ErrorDetails

from planar.ai import models as m
from planar.files.models import PlanarFile
from planar.logging import get_logger
from planar.utils import partition

logger = get_logger(__name__)

OUTPUT_TOOL_NAME = "send_final_response"
OUTPUT_TOOL_DESCRIPTION = """Called to provide the final response which ends this conversation.
Call it with the final JSON response!"""

NATIVE_STRUCTURED_OUTPUT_MODELS = re.compile(
    r"""
      gpt-4o
    """,
    re.VERBOSE | re.IGNORECASE,
)


def format_validation_errors(errors: list[ErrorDetails], function: bool) -> str:
    lines = [
        f"You called {OUTPUT_TOOL_NAME} with JSON that doesn't pass validation:"
        if function
        else "You returned JSON that did not pass validation:",
        "",
    ]
    for error in errors:
        msg = error["msg"]
        field_path = ".".join([str(loc) for loc in error["loc"]])
        input = error["input"]
        lines.append(f"- {field_path}: {msg} (input: {json.dumps(input)})")

    return "\n".join(lines)


async def openai_try_upload_file(
    model: KnownModelName | Model, file: PlanarFile
) -> m.FileIdContent | None:
    # Currently pydanticAI doesn't support passing file_ids, but leaving the
    # implementation here for when they add support.
    return None

    if file.content_type != "application/pdf":
        # old implementation only does this for pdf files, so keep the behavior for now
        return None

    if isinstance(model, str) and not model.startswith("openai:"):
        # not using openai provider
        return None

    try:
        # make this code work with openai as optional dependency
        from pydantic_ai.models.openai import OpenAIModel
    except ImportError:
        return None

    if os.getenv("OPENAI_BASE_URL", None) is not None:
        # cannot use OpenAI file upload if using a custom base url
        return None

    if (
        isinstance(model, OpenAIModel)
        and model.client.base_url.host != "api.openai.com"
    ):
        # same as above
        return None

    logger.debug("uploading pdf file to openai", filename=file.filename)

    # use a separate AsyncClient instance since the model might be provided as a string
    from openai import AsyncClient

    client = AsyncClient()

    # upload the file to the provider
    openai_file = await client.files.create(
        file=(
            file.filename,
            await file.get_content(),
            file.content_type,
        ),
        purpose="user_data",
    )
    logger.info(
        "uploaded pdf file to openai",
        filename=file.filename,
        openai_file_id=openai_file.id,
    )
    return m.FileIdContent(content=openai_file.id)


async def build_file_map(
    model: KnownModelName | Model, messages: list[m.ModelMessage]
) -> m.FileMap:
    logger.debug("building file map", num_messages=len(messages))
    file_dict = {}

    for message_idx, message in enumerate(messages):
        if isinstance(message, m.UserMessage) and message.files:
            logger.debug(
                "processing files in message",
                num_files=len(message.files),
                message_index=message_idx,
            )
            for file_idx, file in enumerate(message.files):
                logger.debug(
                    "processing file",
                    file_index=file_idx,
                    file_id=file.id,
                    content_type=file.content_type,
                )

                file_content_id = await openai_try_upload_file(model, file)
                # TODO: add more `try_upload_file` implementations for other providers that support
                if file_content_id is not None:
                    file_dict[str(file.id)] = file_content_id
                    continue

                # For now we are not using uploaded files with Gemini, so convert all to base64
                if file.content_type.startswith(
                    ("image/", "audio/", "video/", "application/pdf")
                ):
                    logger.debug(
                        "encoding file to base64",
                        filename=file.filename,
                        content_type=file.content_type,
                    )
                    file_dict[str(file.id)] = m.Base64Content(
                        content=base64.b64encode(await file.get_content()).decode(
                            "utf-8"
                        ),
                        content_type=file.content_type,
                    )
                else:
                    raise ValueError(f"Unsupported file type: {file.content_type}")

    return m.FileMap(mapping=file_dict)


async def prepare_messages(
    model: KnownModelName | Model, messages: list[m.ModelMessage]
) -> list[Any]:
    """Prepare messages from Planar representations into the format expected by PydanticAI.

    Args:
        messages: List of structured messages.
        file_map: Optional file map for file content.

    Returns:
        List of messages in PydanticAI format
    """
    pydantic_messages: list[ModelMessage] = []
    file_map = await build_file_map(model, messages)

    def append_request_part(part: ModelRequestPart):
        last = (
            pydantic_messages[-1]
            if pydantic_messages and isinstance(pydantic_messages[-1], ModelRequest)
            else None
        )
        if not last:
            last = ModelRequest(parts=[])
            pydantic_messages.append(last)
        last.parts.append(part)

    def append_response_part(part: ModelResponsePart):
        last = (
            pydantic_messages[-1]
            if pydantic_messages and isinstance(pydantic_messages[-1], ModelResponse)
            else None
        )
        if not last:
            last = ModelResponse(parts=[])
            pydantic_messages.append(last)
        last.parts.append(part)

    for message in messages:
        if isinstance(message, m.SystemMessage):
            append_request_part(SystemPromptPart(content=message.content or ""))
        elif isinstance(message, m.UserMessage):
            user_content: list[UserContent] = []
            files: list[m.FileContent] = []
            if message.files:
                if not file_map:
                    raise ValueError("File map empty while user message has files.")
                for file in message.files:
                    if str(file.id) not in file_map.mapping:
                        raise ValueError(
                            f"File {file} not found in file map {file_map}."
                        )
                    files.append(file_map.mapping[str(file.id)])
            for file in files:
                match file:
                    case m.Base64Content():
                        user_content.append(
                            BinaryContent(
                                data=base64.b64decode(file.content),
                                media_type=file.content_type,
                            )
                        )
                    case m.FileIdContent():
                        raise Exception(
                            "file id handling not implemented yet for PydanticAI"
                        )
            if message.content is not None:
                user_content.append(message.content)
            append_request_part(UserPromptPart(content=user_content))
        elif isinstance(message, m.ToolMessage):
            append_request_part(
                ToolReturnPart(
                    tool_name="unknown",  # FIXME: Planar's ToolMessage doesn't include tool name
                    content=message.content,
                    tool_call_id=message.tool_call_id,
                )
            )
        elif isinstance(message, m.AssistantMessage):
            if message.content:
                append_response_part(TextPart(content=message.content or ""))
            if message.tool_calls:
                for tc in message.tool_calls:
                    append_response_part(
                        ToolCallPart(
                            tool_call_id=str(tc.id),
                            tool_name=tc.name,
                            args=tc.arguments,
                        )
                    )

    return pydantic_messages


def setup_native_structured_output(
    request_params: ModelRequestParameters,
    output_type: Type[BaseModel],
):
    schema_name = output_type.__name__
    if not re.match(r"^[a-zA-Z0-9_-]+$", output_type.__name__):
        schema_name = re.sub(r"[^a-zA-Z0-9_-]", "_", output_type.__name__)
    json_schema = output_type.model_json_schema()
    request_params.output_object = OutputObjectDefinition(
        name=schema_name,
        description=output_type.__doc__ or "",
        json_schema=json_schema,
    )
    request_params.output_mode = "native"


def setup_tool_structured_output(
    request_params: ModelRequestParameters,
    output_type: Type[BaseModel],
    messages: list[ModelMessage],
):
    request_params.output_mode = "tool"
    toolset = OutputToolset.build(
        [output_type],
        name=OUTPUT_TOOL_NAME,
        description=OUTPUT_TOOL_DESCRIPTION,
    )
    assert toolset
    output_tool_defs = toolset._tool_defs
    assert len(output_tool_defs) == 1, "Only one output tool is expected"
    output_tool_defs[0].strict = True
    request_params.output_tools = output_tool_defs

    if not len(messages):
        return

    # Some weaker models might not understand that they need to call a function
    # to return the final response. Add a reminder to the end of the system
    # prompt.
    first_request = messages[0]
    first_part = first_request.parts[0]
    if not isinstance(first_part, SystemPromptPart):
        return
    extra_system = textwrap.dedent(
        f"""\n
        WHEN you have a final JSON response, you MUST call the "{OUTPUT_TOOL_NAME}" function/tool with the response to return it. DO NOT RETURN the JSON response directly!!!
        """
    )
    first_part.content += extra_system


def return_native_structured_output[TOutput: BaseModel](
    output_type: Type[TOutput],
    final_tool_calls: list[m.ToolCall],
    content: str,
    thinking: str | None = None,
) -> m.CompletionResponse[TOutput]:
    try:
        result = m.CompletionResponse(
            content=output_type.model_validate_json(content),
            tool_calls=final_tool_calls,
            text_content=content,
            reasoning_content=thinking,
        )
        logger.info(
            "model run completed with structured output",
            content=result.content,
            reasoning_content=result.reasoning_content,
            text_content=content,
            tool_calls=result.tool_calls,
        )
        return result
    except Exception:
        logger.exception(
            "model output parse failure",
            content=content,
            output_model=output_type,
        )
        raise


def return_tool_structured_output[TOutput: BaseModel](
    output_type: Type[TOutput],
    tool_calls: list[m.ToolCall],
    final_result_tc: m.ToolCall,
    content: str,
    thinking: str | None = None,
) -> m.CompletionResponse[TOutput]:
    try:
        result = m.CompletionResponse(
            content=output_type.model_validate(final_result_tc.arguments),
            tool_calls=tool_calls,
            text_content=content,
            reasoning_content=thinking,
        )
        logger.info(
            "model run completed with structured output",
            content=result.content,
            reasoning_content=result.reasoning_content,
            tool_calls=result.tool_calls,
        )
        return result
    except Exception:
        logger.exception(
            "model output parse failure",
            content=content,
            output_model=output_type,
        )
        raise


class ModelRunResponse[TOutput: BaseModel | str](BaseModel):
    response: m.CompletionResponse[TOutput]
    extra_turns_used: int


async def model_run[TOutput: BaseModel | str](
    model: Model | KnownModelName,
    max_extra_turns: int,
    model_settings: dict[str, Any] | None = None,
    messages: list[m.ModelMessage] = [],
    tools: list[m.ToolDefinition] = [],
    event_handler: m.AgentEventEmitter | None = None,
    output_type: Type[TOutput] = str,
) -> ModelRunResponse[TOutput]:
    # assert that the caller doesn't provide a tool called "final_result"
    if any(tool.name == OUTPUT_TOOL_NAME for tool in tools):
        raise ValueError(
            f'Tool named "{OUTPUT_TOOL_NAME}" is reserved and should not be provided.'
        )

    extra_turns_used = 0
    model_name = model.model_name if isinstance(model, Model) else model
    # Only enable native structured output for models that support it
    supports_native_structured_output = bool(
        NATIVE_STRUCTURED_OUTPUT_MODELS.search(model_name)
    )

    request_params = ModelRequestParameters(
        function_tools=[
            ToolDefinition(
                name=tool.name,
                description=tool.description,
                parameters_json_schema=tool.parameters,
                strict=True,
            )
            for tool in tools
        ]
    )

    structured_output = issubclass(output_type, BaseModel)

    def emit(event_type: m.AgentEventType, content: str):
        if event_handler:
            event_handler.emit(event_type, content)

    history = await prepare_messages(model, messages=messages)

    if structured_output:
        if supports_native_structured_output:
            setup_native_structured_output(request_params, output_type)
        else:
            setup_tool_structured_output(request_params, output_type, history)

    while True:
        think_buffer = []
        text_buffer = []
        current_tool_call = None
        current_tool_args_buffer = []
        current_tool_call_id = None
        tool_calls = []

        response_parts: list[ModelResponsePart] = []

        async with model_request_stream(
            model=model,
            messages=history,
            model_request_parameters=request_params,
            model_settings=cast(ModelSettings, model_settings),
        ) as stream:
            async for event in stream:
                match event:
                    case PartStartEvent(part=part):
                        response_parts.append(part)
                        if isinstance(part, TextPart):
                            emit(m.AgentEventType.TEXT, part.content)
                            text_buffer.append(part.content)
                        elif isinstance(part, ThinkingPart):
                            emit(m.AgentEventType.THINK, part.content)
                            think_buffer.append(part.content)
                        elif isinstance(part, ToolCallPart):
                            if current_tool_call is not None:
                                # If we already have a tool call, emit the previous one
                                tool_calls.append(
                                    dict(
                                        name=current_tool_call,
                                        arg_str="".join(current_tool_args_buffer),
                                        id=current_tool_call_id,
                                    )
                                )
                            current_tool_call = part.tool_name
                            current_tool_call_id = part.tool_call_id
                            current_tool_args_buffer = []
                            if part.args:
                                if isinstance(part.args, dict):
                                    current_tool_args_buffer.append(
                                        json.dumps(part.args)
                                    )
                                else:
                                    current_tool_args_buffer.append(part.args)
                    case PartDeltaEvent(delta=delta):
                        current = response_parts[-1]
                        if isinstance(delta, TextPartDelta):
                            assert isinstance(current, TextPart)
                            emit(m.AgentEventType.TEXT, delta.content_delta)
                            text_buffer.append(delta.content_delta)
                            current.content += delta.content_delta
                        elif (
                            isinstance(delta, ThinkingPartDelta) and delta.content_delta
                        ):
                            assert isinstance(current, ThinkingPart)
                            emit(m.AgentEventType.THINK, delta.content_delta)
                            think_buffer.append(delta.content_delta)
                            current.content += delta.content_delta
                        elif isinstance(delta, ToolCallPartDelta):
                            assert isinstance(current, ToolCallPart)
                            assert current_tool_call is not None
                            assert current_tool_call_id == delta.tool_call_id
                            current_tool_args_buffer.append(delta.args_delta)
                            if delta.tool_name_delta:
                                current.tool_name += delta.tool_name_delta
                            if isinstance(delta.args_delta, str):
                                if current.args is None:
                                    current.args = ""
                                assert isinstance(current.args, str)
                                current.args += delta.args_delta

        if current_tool_call is not None:
            tool_calls.append(
                dict(
                    name=current_tool_call,
                    arg_str="".join(current_tool_args_buffer),
                    id=current_tool_call_id,
                )
            )

        content = "".join(text_buffer)
        thinking = "".join(think_buffer)

        logger.debug(
            "model run completed",
            content=content,
            thinking=thinking,
            tool_calls=tool_calls,
        )

        try:
            calls = [
                m.ToolCall(
                    id=tc["id"],
                    name=tc["name"],
                    arguments=json.loads(tc["arg_str"]),
                )
                for tc in tool_calls
            ]

            def is_output_tool(tc):
                return tc.name == OUTPUT_TOOL_NAME

            final_tool_calls, final_result_tool_calls = partition(is_output_tool, calls)
        except json.JSONDecodeError:
            logger.exception(
                "tool call json parse failure",
                tool_calls=tool_calls,
            )
            raise

        if final_tool_calls:
            return ModelRunResponse(
                response=m.CompletionResponse(
                    tool_calls=final_tool_calls,
                    text_content=content,
                    reasoning_content=thinking,
                ),
                extra_turns_used=extra_turns_used,
            )

        if final_result_tool_calls:
            # only 1 final result tool call is expected
            assert len(final_result_tool_calls) == 1

        if structured_output:
            try:
                if supports_native_structured_output:
                    return ModelRunResponse(
                        response=return_native_structured_output(
                            output_type, final_tool_calls, content, thinking
                        ),
                        extra_turns_used=extra_turns_used,
                    )
                elif final_result_tool_calls:
                    return ModelRunResponse(
                        response=return_tool_structured_output(
                            output_type,
                            final_tool_calls,
                            final_result_tool_calls[0],
                            content,
                            thinking,
                        ),
                        extra_turns_used=extra_turns_used,
                    )
            except ValidationError as e:
                if extra_turns_used >= max_extra_turns:
                    raise
                # retry passing the validation error to the LLM
                # first, append the collected response parts to the history
                history.append(ModelResponse(parts=response_parts))
                # now append the ToolResponse with the validation errors

                retry_part = RetryPromptPart(
                    content=format_validation_errors(
                        e.errors(), function=len(final_result_tool_calls) > 0
                    )
                )
                if final_result_tool_calls:
                    retry_part.tool_name = OUTPUT_TOOL_NAME
                    retry_part.tool_call_id = cast(str, final_result_tool_calls[0].id)

                request_parts: list[ModelRequestPart] = [retry_part]
                history.append(ModelRequest(parts=request_parts))
                extra_turns_used += 1
                continue

        if output_type is not str:
            if extra_turns_used >= max_extra_turns:
                raise ValueError(
                    "Model did not return structured output, and no turns left to retry."
                )
            # We can only reach this point if the model did not call send_final_response
            # To return structured output. Report the error back to the LLM and retry
            history.append(ModelResponse(parts=response_parts))
            history.append(
                ModelRequest(
                    parts=[
                        UserPromptPart(
                            content=f'Error processing response. You MUST pass the final JSON response to the "{OUTPUT_TOOL_NAME}" tool/function. DO NOT RETURN the JSON directly!!!'
                        )
                    ]
                )
            )
            extra_turns_used += 1
            continue

        result = cast(
            m.CompletionResponse[TOutput],
            m.CompletionResponse(
                content=content,
                tool_calls=final_tool_calls,
                text_content=content,
                reasoning_content=thinking,
            ),
        )
        logger.info(
            "model run completed with string output",
            content=result.content,
            reasoning_content=result.reasoning_content,
            tool_calls=result.tool_calls,
        )
        return ModelRunResponse(
            response=result,
            extra_turns_used=extra_turns_used,
        )
