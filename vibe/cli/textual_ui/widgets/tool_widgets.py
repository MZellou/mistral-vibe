from __future__ import annotations

from collections.abc import Awaitable, Callable

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.events import Key
from textual.widgets import Markdown, Static


class ToolApprovalWidget(Vertical):
    def __init__(self, data: dict) -> None:
        super().__init__()
        self.data = data
        self.add_class("tool-approval-widget")

    def compose(self) -> ComposeResult:
        MAX_APPROVAL_MSG_SIZE = 150

        for key, value in self.data.items():
            value_str = str(value)
            if len(value_str) > MAX_APPROVAL_MSG_SIZE:
                hidden = len(value_str) - MAX_APPROVAL_MSG_SIZE
                value_str = (
                    value_str[:MAX_APPROVAL_MSG_SIZE] + f"… ({hidden} more characters)"
                )
            yield Static(
                f"{key}: {value_str}", markup=False, classes="approval-description"
            )


class ToolResultWidget(Static):
    def __init__(self, data: dict, collapsed: bool = True) -> None:
        super().__init__()
        self.data = data
        self.collapsed = collapsed
        self.add_class("tool-result-widget")

    def compose(self) -> ComposeResult:
        message = self.data.get("message", "")

        if self.collapsed:
            yield Static(f"{message} (ctrl+o to expand.)", markup=False)
        else:
            yield Static(message, markup=False)

        if not self.collapsed and (details := self.data.get("details")):
            for key, value in details.items():
                if value:
                    yield Static(
                        f"{key}: {value}", markup=False, classes="tool-result-detail"
                    )


class BashApprovalWidget(ToolApprovalWidget):
    def compose(self) -> ComposeResult:
        command = self.data.get("command", "")
        description = self.data.get("description", "")

        if description:
            yield Static(description, markup=False, classes="approval-description")
            yield Static("")

        yield Markdown(f"```bash\n{command}\n```")


class BashResultWidget(ToolResultWidget):
    def compose(self) -> ComposeResult:
        message = self.data.get("message", "")

        if self.collapsed:
            yield Static(f"{message} (ctrl+o to expand.)", markup=False)
        else:
            yield Static(message, markup=False)

        if not self.collapsed and (details := self.data.get("details")):
            for key, value in details.items():
                if value:
                    yield Static(
                        f"{key}: {value}", markup=False, classes="tool-result-detail"
                    )


class WriteFileApprovalWidget(ToolApprovalWidget):
    def compose(self) -> ComposeResult:
        path = self.data.get("path", "")
        content = self.data.get("content", "")
        file_extension = self.data.get("file_extension", "text")

        yield Static(f"File: {path}", markup=False, classes="approval-description")
        yield Static("")

        yield Markdown(f"```{file_extension}\n{content}\n```")


class WriteFileResultWidget(ToolResultWidget):
    def compose(self) -> ComposeResult:
        MAX_LINES = 10
        message = self.data.get("message", "")

        if self.collapsed:
            yield Static(f"{message} (ctrl+o to expand.)", markup=False)
        else:
            yield Static(message, markup=False)

        if not self.collapsed:
            if path := self.data.get("path"):
                yield Static(
                    f"Path: {path}", markup=False, classes="tool-result-detail"
                )

            if bytes_written := self.data.get("bytes_written"):
                yield Static(
                    f"Bytes: {bytes_written}",
                    markup=False,
                    classes="tool-result-detail",
                )

            if content := self.data.get("content"):
                yield Static("")
                file_extension = self.data.get("file_extension", "text")

                lines = content.split("\n")
                total_lines = len(lines)

                if total_lines > MAX_LINES:
                    shown_lines = lines[:MAX_LINES]
                    remaining = total_lines - MAX_LINES
                    truncated_content = "\n".join(
                        shown_lines + [f"… ({remaining} more lines)"]
                    )
                    yield Markdown(f"```{file_extension}\n{truncated_content}\n```")
                else:
                    yield Markdown(f"```{file_extension}\n{content}\n```")


class SearchReplaceApprovalWidget(ToolApprovalWidget):
    def compose(self) -> ComposeResult:
        file_path = self.data.get("file_path", "")
        diff_lines = self.data.get("diff_lines", [])

        yield Static(f"File: {file_path}", markup=False, classes="approval-description")
        yield Static("")

        if diff_lines:
            for line in diff_lines:
                if line.startswith("---") or line.startswith("+++"):
                    yield Static(line, markup=False, classes="diff-header")
                elif line.startswith("-"):
                    yield Static(line, markup=False, classes="diff-removed")
                elif line.startswith("+"):
                    yield Static(line, markup=False, classes="diff-added")
                elif line.startswith("@@"):
                    yield Static(line, markup=False, classes="diff-range")
                else:
                    yield Static(line, markup=False, classes="diff-context")


class SearchReplaceResultWidget(ToolResultWidget):
    def compose(self) -> ComposeResult:
        message = self.data.get("message", "")

        if self.collapsed:
            yield Static(f"{message} (ctrl+o to expand.)", markup=False)
        else:
            yield Static(message, markup=False)

        if not self.collapsed and (diff_lines := self.data.get("diff_lines")):
            yield Static("")
            for line in diff_lines:
                if line.startswith("---") or line.startswith("+++"):
                    yield Static(line, markup=False, classes="diff-header")
                elif line.startswith("-"):
                    yield Static(line, markup=False, classes="diff-removed")
                elif line.startswith("+"):
                    yield Static(line, markup=False, classes="diff-added")
                elif line.startswith("@@"):
                    yield Static(line, markup=False, classes="diff-range")
                else:
                    yield Static(line, markup=False, classes="diff-context")


class TodoApprovalWidget(ToolApprovalWidget):
    def compose(self) -> ComposeResult:
        description = self.data.get("description", "")
        if description:
            yield Static(description, markup=False, classes="approval-description")


class TodoResultWidget(ToolResultWidget):
    def compose(self) -> ComposeResult:
        message = self.data.get("message", "")

        if self.collapsed:
            yield Static(message, markup=False)
        else:
            yield Static(message, markup=False)
            yield Static("")

            by_status = self.data.get("todos_by_status", {})
            if not any(by_status.values()):
                yield Static("No todos", markup=False, classes="todo-empty")
                return

            for status in ["in_progress", "pending", "completed", "cancelled"]:
                todos = by_status.get(status, [])
                for todo in todos:
                    content = todo.get("content", "")
                    icon = self._get_status_icon(status)
                    yield Static(
                        f"{icon} {content}", markup=False, classes=f"todo-{status}"
                    )

    def _get_status_icon(self, status: str) -> str:
        icons = {"pending": "☐", "in_progress": "☐", "completed": "☑", "cancelled": "☒"}
        return icons.get(status, "☐")


class ReadFileApprovalWidget(ToolApprovalWidget):
    def compose(self) -> ComposeResult:
        for key, value in self.data.items():
            if value:
                yield Static(
                    f"{key}: {value}", markup=False, classes="approval-description"
                )


class ReadFileResultWidget(ToolResultWidget):
    def compose(self) -> ComposeResult:
        MAX_LINES = 10
        message = self.data.get("message", "")

        if self.collapsed:
            yield Static(f"{message} (ctrl+o to expand.)", markup=False)
        else:
            yield Static(message, markup=False)

        if self.collapsed:
            return

        if path := self.data.get("path"):
            yield Static(f"Path: {path}", markup=False, classes="tool-result-detail")

        if warnings := self.data.get("warnings"):
            for warning in warnings:
                yield Static(
                    f"⚠ {warning}", markup=False, classes="tool-result-warning"
                )

        if content := self.data.get("content"):
            yield Static("")
            file_extension = self.data.get("file_extension", "text")

            lines = content.split("\n")
            total_lines = len(lines)

            if total_lines > MAX_LINES:
                shown_lines = lines[:MAX_LINES]
                remaining = total_lines - MAX_LINES
                truncated_content = "\n".join(
                    shown_lines + [f"… ({remaining} more lines)"]
                )
                yield Markdown(f"```{file_extension}\n{truncated_content}\n```")
            else:
                yield Markdown(f"```{file_extension}\n{content}\n```")


class GrepApprovalWidget(ToolApprovalWidget):
    def compose(self) -> ComposeResult:
        for key, value in self.data.items():
            if value:
                yield Static(
                    f"{key}: {value!s}", classes="approval-description", markup=False
                )


class GrepResultWidget(ToolResultWidget):
    def compose(self) -> ComposeResult:
        MAX_LINES = 30
        message = self.data.get("message", "")

        if self.collapsed:
            yield Static(f"{message} (ctrl+o to expand.)", markup=False)
        else:
            yield Static(message, markup=False)

        if self.collapsed:
            return

        if warnings := self.data.get("warnings"):
            for warning in warnings:
                yield Static(
                    f"⚠ {warning}", classes="tool-result-warning", markup=False
                )

        if matches := self.data.get("matches"):
            yield Static("")

            lines = matches.split("\n")
            total_lines = len(lines)

            if total_lines > MAX_LINES:
                shown_lines = lines[:MAX_LINES]
                remaining = total_lines - MAX_LINES
                truncated_content = "\n".join(
                    shown_lines + [f"… ({remaining} more lines)"]
                )
                yield Markdown(f"```\n{truncated_content}\n```")
            else:
                yield Markdown(f"```\n{matches}\n```")


class AskUserApprovalWidget(ToolApprovalWidget):
    def compose(self) -> ComposeResult:
        question = self.data.get("question", "")
        options = self.data.get("options", [])

        yield Static("🤖 AI Question:", classes="ask-user-header", markup=False)
        yield Static("")
        yield Static(question, classes="ask-user-question", markup=False)

        if options:
            yield Static("")
            yield Static("Options:", classes="ask-user-options-header", markup=False)
            # Add "Type something" option
            all_options = options + ["Type something..."]
            for i, option in enumerate(all_options, 1):
                yield Static(f"{i}. {option}", classes="ask-user-option", markup=False)


class AskUserResultWidget(ToolResultWidget):
    def compose(self) -> ComposeResult:
        question = self.data.get("question", "")
        options = self.data.get("options", [])
        message = self.data.get("message", "")
        user_response = self.data.get("user_response")

        if self.collapsed:
            yield Static(
                f"Question asked: {question[:50]}... (ctrl+o to expand.)", markup=False
            )
        else:
            yield Static("🤖 AI Question:", classes="ask-user-header", markup=False)
            yield Static("")
            yield Static(question, classes="ask-user-question", markup=False)

            if options:
                yield Static("")
                yield Static(
                    "Options:", classes="ask-user-options-header", markup=False
                )
                for i, option in enumerate(options, 1):
                    yield Static(
                        f"{i}. {option}", classes="ask-user-option", markup=False
                    )

            if user_response:
                yield Static("")
                yield Static(
                    "✓ User Response:", classes="ask-user-response-header", markup=False
                )
                yield Static(user_response, classes="ask-user-response", markup=False)

            if message:
                yield Static("")
                yield Static(message, classes="ask-user-message", markup=False)


class InteractiveAskUserWidget(ToolApprovalWidget):
    """Interactive widget for ask_user with keyboard navigation and free-text input."""

    def __init__(
        self,
        question: str,
        options: list[str],
        on_select: Callable[[str], Awaitable[None]],
    ) -> None:
        super().__init__(data={"question": question, "options": options})
        self.question = question
        self.options = options + ["Type something..."]  # Add free-text option
        self.selected_index = 0
        self.on_select = on_select
        self.add_class("interactive-ask-user")

    def compose(self) -> ComposeResult:
        yield Static("🤖 AI Question:", classes="ask-user-header", markup=False)
        yield Static("")
        yield Static(self.question, classes="ask-user-question", markup=False)
        yield Static("")
        yield Static("Options:", classes="ask-user-options-header", markup=False)

        # Create option widgets
        for i, option in enumerate(self.options):
            option_widget = Static(
                f"{i + 1}. {option}", classes="ask-user-option", markup=False
            )
            if i == self.selected_index:
                option_widget.add_class("ask-user-option-selected")
            setattr(self, f"option_{i}", option_widget)
            yield option_widget

    async def on_key(self, event: Key) -> None:
        if event.key == "up":
            self._select_previous()
            event.prevent_default()
        elif event.key == "down":
            self._select_next()
            event.prevent_default()
        elif event.key == "enter":
            await self._handle_selection()
            event.prevent_default()

    def _select_previous(self) -> None:
        if self.selected_index > 0:
            self.selected_index -= 1
            self._update_selection()

    def _select_next(self) -> None:
        if self.selected_index < len(self.options) - 1:
            self.selected_index += 1
            self._update_selection()

    def _update_selection(self) -> None:
        for i, _option in enumerate(self.options):
            option_widget = getattr(self, f"option_{i}")
            option_widget.remove_class("ask-user-option-selected")
            if i == self.selected_index:
                option_widget.add_class("ask-user-option-selected")

    async def _handle_selection(self) -> None:
        selected_option = self.options[self.selected_index]
        if selected_option == "Type something...":
            # Handle free-text input
            await self.on_select("free_text")
        else:
            await self.on_select(selected_option)
