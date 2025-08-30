# pyright: reportPrivateUsage=false

import asyncio
import logging
import types
from pydantic_ai.models import Model
from typing_extensions import override
from eval_protocol.models import EvaluationRow, Message
from eval_protocol.pytest.rollout_processor import RolloutProcessor
from eval_protocol.pytest.types import RolloutProcessorConfig
from openai.types.chat import ChatCompletion, ChatCompletionMessage, ChatCompletionMessageParam
from openai.types.chat.chat_completion import Choice as ChatCompletionChoice
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.google import GoogleModel
from pydantic import TypeAdapter
from pydantic_ai.messages import ModelMessage
from pydantic_ai._utils import generate_tool_call_id
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelRequest,
    SystemPromptPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.providers.openai import OpenAIProvider

logger = logging.getLogger(__name__)


class PydanticAgentRolloutProcessor(RolloutProcessor):
    """Rollout processor for Pydantic AI agents. Mainly converts
    EvaluationRow.messages to and from Pydantic AI ModelMessage format."""

    def __init__(self):
        # dummy model used for its helper functions for processing messages
        self.util: OpenAIModel = OpenAIModel("dummy-model", provider=OpenAIProvider(api_key="dummy"))

    @override
    def __call__(self, rows: list[EvaluationRow], config: RolloutProcessorConfig) -> list[asyncio.Task[EvaluationRow]]:
        """Create agent rollout tasks and return them for external handling."""

        max_concurrent = getattr(config, "max_concurrent_rollouts", 8) or 8
        semaphore = asyncio.Semaphore(max_concurrent)

        # validate that the "agent" field is present with a valid Pydantic AI Agent instance in the completion_params dict
        if "agent" not in config.kwargs:
            raise ValueError("kwargs must contain an 'agent' field with a valid Pydantic AI Agent instance")
        if not isinstance(config.kwargs["agent"], Agent) and not isinstance(
            config.kwargs["agent"], types.FunctionType
        ):
            raise ValueError(
                "kwargs['agent'] must be a valid Pydantic AI Agent instance or a function that returns an Agent"
            )

        if isinstance(config.kwargs["agent"], types.FunctionType):
            setup_agent = config.kwargs["agent"]
            if not isinstance(config.completion_params["model"], dict):
                raise ValueError(
                    "completion_params['model'] must be a dict mapping agent argument names to model config dicts (with 'model' and 'provider' keys)"
                )
            kwargs: dict[str, Model] = {}
            for k, v in config.completion_params["model"].items():  # pyright: ignore[reportUnknownVariableType]
                if v["model"] and v["model"].startswith("anthropic:"):  # pyright: ignore[reportUnknownMemberType]
                    kwargs[k] = AnthropicModel(
                        v["model"].removeprefix("anthropic:"),  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                    )
                elif v["model"] and v["model"].startswith("google:"):  # pyright: ignore[reportUnknownMemberType]
                    kwargs[k] = GoogleModel(
                        v["model"].removeprefix("google:"),  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                    )
                else:
                    kwargs[k] = OpenAIModel(
                        v["model"],  # pyright: ignore[reportUnknownArgumentType]
                        provider=v["provider"],  # pyright: ignore[reportUnknownArgumentType]
                    )
            agent_instance: Agent = setup_agent(**kwargs)  # pyright: ignore[reportAny]
            model = None
        else:
            agent_instance = config.kwargs["agent"]  # pyright: ignore[reportAssignmentType]
            model = OpenAIModel(
                config.completion_params["model"],  # pyright: ignore[reportAny]
                provider=config.completion_params["provider"],  # pyright: ignore[reportAny]
            )

        async def process_row(row: EvaluationRow) -> EvaluationRow:
            """Process a single row with agent rollout."""
            model_messages = [self.convert_ep_message_to_pyd_message(m, row) for m in row.messages]
            response = await agent_instance.run(
                message_history=model_messages, model=model, usage_limits=config.kwargs.get("usage_limits")
            )
            row.messages = await self.convert_pyd_message_to_ep_message(response.all_messages())
            return row

        async def _sem_wrapper(r: EvaluationRow) -> EvaluationRow:
            async with semaphore:
                result = await process_row(r)
                return result

        # Create and return tasks for external handling
        tasks = [asyncio.create_task(_sem_wrapper(row)) for row in rows]
        return tasks

    async def convert_pyd_message_to_ep_message(self, messages: list[ModelMessage]) -> list[Message]:
        oai_messages: list[ChatCompletionMessageParam] = await self.util._map_messages(messages)
        return [Message(**m) for m in oai_messages]  # pyright: ignore[reportArgumentType]

    def convert_ep_message_to_pyd_message(self, message: Message, row: EvaluationRow) -> ModelMessage:
        if message.role == "assistant":
            type_adapter = TypeAdapter(ChatCompletionMessage)
            oai_message = type_adapter.validate_python(message)
            # Fix: Provide required finish_reason and index, and ensure created is int (timestamp)
            return self.util._process_response(
                ChatCompletion(
                    choices=[ChatCompletionChoice(message=oai_message, finish_reason="stop", index=0)],
                    object="chat.completion",
                    model="",
                    id="",
                    created=int(row.created_at.timestamp()),
                )
            )
        elif message.role == "user":
            if isinstance(message.content, str):
                return ModelRequest(parts=[UserPromptPart(content=message.content)])
            elif isinstance(message.content, list):
                return ModelRequest(parts=[UserPromptPart(content=message.content[0].text)])
            else:
                raise ValueError(f"Unsupported content type for user message: {type(message.content)}")
        elif message.role == "system":
            if isinstance(message.content, str):
                return ModelRequest(parts=[SystemPromptPart(content=message.content)])
            elif isinstance(message.content, list):
                return ModelRequest(parts=[SystemPromptPart(content=message.content[0].text)])
            else:
                raise ValueError(f"Unsupported content type for system message: {type(message.content)}")
        elif message.role == "tool":
            return ModelRequest(
                parts=[
                    ToolReturnPart(
                        content=message.content,
                        tool_name="",
                        tool_call_id=message.tool_call_id or generate_tool_call_id(),
                    )
                ]
            )
        else:
            raise ValueError(f"Unknown role: {message.role}")
