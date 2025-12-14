from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, Field

from vibe.core.tools.base import BaseTool, BaseToolConfig, BaseToolState, ToolPermission
from vibe.core.tools.ui import ToolCallDisplay, ToolResultDisplay, ToolUIData
from vibe.core.types import ToolCallEvent, ToolResultEvent


class AskUserArgs(BaseModel):
    question: str = Field(description="The question to ask the user")
    options: list[str] | None = Field(
        default=None, description="Optional list of choices to present (2-4 options)"
    )


class AskUserResult(BaseModel):
    question: str
    options: list[str] | None = None
    user_response: str | None = None
    message: str = "Question asked. Waiting for user response."


class AskUserConfig(BaseToolConfig):
    permission: ToolPermission = ToolPermission.ALWAYS
    interaction_callback: Callable[[str, list[str] | None], Awaitable[str]] | None = (
        None
    )


class AskUser(
    BaseTool[AskUserArgs, AskUserResult, AskUserConfig, BaseToolState],
    ToolUIData[AskUserArgs, AskUserResult],
):
    """Tool for asking the user clarifying questions."""

    description: ClassVar[str] = (
        "Ask the user a clarifying question when you need input on approach, "
        "requirements, or preferences before proceeding."
    )
    prompt_path: ClassVar[Path | None] = (
        Path(__file__).parent / "prompts" / "ask_user.md"
    )

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        if not isinstance(event.args, AskUserArgs):
            return ToolCallDisplay(summary="Invalid arguments")

        args = event.args
        details: dict[str, str | list[str]] = {"question": args.question}
        if args.options:
            details["options"] = args.options

        return ToolCallDisplay(summary="Asking user", details=details)

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        if not isinstance(event.result, AskUserResult):
            return ToolResultDisplay(success=True, message="Question asked")

        result = event.result
        details: dict[str, str | list[str]] = {"question": result.question}
        if result.options:
            details["options"] = result.options
        if result.user_response:
            details["user_response"] = result.user_response

        return ToolResultDisplay(success=True, message=result.message, details=details)

    @classmethod
    def get_status_text(cls) -> str:
        return "Asking user"

    async def run(self, args: AskUserArgs) -> AskUserResult:
        # If we have an interactive callback (TUI mode), use it
        if self.config.interaction_callback:
            user_response = await self.config.interaction_callback(
                args.question, args.options
            )
            return AskUserResult(
                question=args.question,
                options=args.options,
                user_response=user_response,
                message=f"User answered: {user_response}",
            )

        # Non-interactive mode (ACP or programmatic use)
        return AskUserResult(
            question=args.question,
            options=args.options,
            user_response=None,
            message=f"Question: {args.question}"
            + (f"\nOptions: {', '.join(args.options)}" if args.options else ""),
        )
