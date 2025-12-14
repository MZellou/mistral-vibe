from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel, Field

from vibe.core.llm.backend.factory import BACKEND_FACTORY
from vibe.core.tools.base import (
    BaseTool,
    BaseToolConfig,
    BaseToolState,
    ToolError,
    ToolPermission,
)
from vibe.core.tools.ui import ToolCallDisplay, ToolResultDisplay, ToolUIData
from vibe.core.types import LLMMessage, Role, ToolCallEvent, ToolResultEvent

if TYPE_CHECKING:
    from vibe.core.config import VibeConfig


class ThinkArgs(BaseModel):
    task: str = Field(
        description="The complex task or question requiring deep reasoning"
    )
    context: str | None = Field(
        default=None,
        description="Additional context to help with the reasoning (code snippets, requirements, etc.)",
    )


class ThinkResult(BaseModel):
    task: str
    reasoning: str
    conclusion: str


class ThinkConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ALWAYS
    model: str | None = Field(
        default=None,
        description="Model alias to use for deep thinking (e.g., 'devstral-2'). "
        "If not set, uses the active model.",
    )
    timeout: float = Field(
        default=120.0, description="Timeout in seconds for the thinking request"
    )
    max_tokens: int = Field(
        default=32768, description="Maximum tokens for the response"
    )


THINK_SYSTEM_PROMPT = """You are a deep reasoning assistant. Your role is to carefully analyze complex problems and provide thorough, well-structured responses.

When given a task:
1. Break down the problem into components
2. Consider multiple approaches
3. Evaluate trade-offs
4. Provide a clear recommendation

Be thorough but concise. Focus on actionable insights."""


class Think(
    BaseTool[ThinkArgs, ThinkResult, ThinkConfig, BaseToolState],
    ToolUIData[ThinkArgs, ThinkResult],
):
    """Delegate complex reasoning to a more capable model.

    Use this tool when you need deeper analysis, architectural decisions,
    or multi-step problem solving that benefits from more powerful reasoning.
    """

    description: ClassVar[str] = (
        "Delegate complex reasoning tasks to a more capable model. "
        "Use for architectural decisions, complex analysis, or multi-step planning."
    )
    prompt_path: ClassVar[Path | None] = Path(__file__).parent / "prompts" / "think.md"

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        if not isinstance(event.args, ThinkArgs):
            return ToolCallDisplay(summary="Invalid arguments")

        MAX_TASK_PREVIEW_LENGTH = 100
        task_preview = (
            event.args.task[:MAX_TASK_PREVIEW_LENGTH] + "..."
            if len(event.args.task) > MAX_TASK_PREVIEW_LENGTH
            else event.args.task
        )
        return ToolCallDisplay(summary="Deep thinking", details={"task": task_preview})

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        if not isinstance(event.result, ThinkResult):
            return ToolResultDisplay(success=False, message="Invalid result")

        return ToolResultDisplay(
            success=True,
            message="Reasoning complete",
            details={"conclusion": event.result.conclusion[:200]},
        )

    @classmethod
    def get_status_text(cls) -> str:
        return "Thinking deeply..."

    def _get_vibe_config(self) -> VibeConfig:
        """Get the injected VibeConfig or raise an error."""
        if self.config.vibe_config is None:
            raise ToolError(
                "Think tool requires VibeConfig to be injected. "
                "This is a bug - please report it."
            )
        return self.config.vibe_config

    async def run(self, args: ThinkArgs) -> ThinkResult:
        vibe_config = self._get_vibe_config()

        # Determine which model to use
        if self.config.model:
            try:
                model_config = vibe_config.get_model_by_alias(self.config.model)
            except ValueError:
                # Try by name
                model_config = vibe_config.get_model_by_name(self.config.model)
        else:
            model_config = vibe_config.get_active_model()

        provider = vibe_config.get_provider_for_model(model_config)

        # Create backend
        backend_cls = BACKEND_FACTORY[provider.backend]
        backend = backend_cls(provider=provider, timeout=self.config.timeout)

        # Build the prompt
        user_content = f"Task: {args.task}"
        if args.context:
            user_content += f"\n\nContext:\n{args.context}"

        messages = [
            LLMMessage(role=Role.system, content=THINK_SYSTEM_PROMPT),
            LLMMessage(role=Role.user, content=user_content),
        ]

        # Make the completion call
        async with backend as b:
            result = await b.complete(
                model=model_config,
                messages=messages,
                temperature=model_config.temperature,
                tools=None,
                tool_choice=None,
                extra_headers={},
                max_tokens=self.config.max_tokens,
            )

        response_content = result.message.content or ""

        # Parse the response - try to extract structured parts
        conclusion = response_content
        reasoning = ""

        # Simple heuristic: if response has multiple paragraphs, first is reasoning
        paragraphs = [p.strip() for p in response_content.split("\n\n") if p.strip()]
        if len(paragraphs) > 1:
            reasoning = "\n\n".join(paragraphs[:-1])
            conclusion = paragraphs[-1]

        return ThinkResult(task=args.task, reasoning=reasoning, conclusion=conclusion)
