from __future__ import annotations

from typing import ClassVar

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container, Vertical
from textual.message import Message
from textual.widgets import Input, Static


class AskUserApp(Container):
    """Interactive app for ask_user tool that captures user responses."""

    can_focus = True
    can_focus_children = False

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("up", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("enter", "select", "Select", show=False),
    ]

    class ResponseSubmitted(Message):
        """Posted when user submits their response."""

        def __init__(self, response: str) -> None:
            super().__init__()
            self.response = response

    def __init__(self, question: str, options: list[str] | None = None) -> None:
        super().__init__(id="ask-user-app")
        self.question = question
        self.options = options or []

        # Add "Type something..." if we have options
        if self.options:
            self.all_options = self.options + ["Type something..."]
        else:
            # No options means free text only
            self.all_options = []

        self.selected_option = 0
        self.in_text_mode = not self.options  # Start in text mode if no options

        self.title_widget: Static | None = None
        self.question_widget: Static | None = None
        self.option_widgets: list[Static] = []
        self.text_input: Input | None = None
        self.help_widget: Static | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="ask-user-content"):
            self.title_widget = Static(
                "🤖 AI Question", classes="ask-user-app-title"
            )
            yield self.title_widget

            yield Static("")

            self.question_widget = Static(
                self.question, classes="ask-user-app-question"
            )
            yield self.question_widget

            yield Static("")

            if self.all_options:
                yield Static("Options:", classes="ask-user-app-options-header")

                for idx, option in enumerate(self.all_options):
                    widget = Static(
                        f"  {idx + 1}. {option}", classes="ask-user-app-option"
                    )
                    self.option_widgets.append(widget)
                    yield widget

                yield Static("")

            # Text input (shown when "Type something..." is selected or no options)
            self.text_input = Input(
                placeholder="Type your answer here...",
                classes="ask-user-app-input",
            )
            if not self.in_text_mode:
                self.text_input.display = False
            yield self.text_input

            yield Static("")

            self.help_widget = Static(
                "↑↓ navigate  Enter select/submit  ESC cancel",
                classes="ask-user-app-help",
            )
            yield self.help_widget

    async def on_mount(self) -> None:
        self._update_selection()
        if self.in_text_mode and self.text_input:
            self.text_input.focus()
        else:
            self.focus()

    def _update_selection(self) -> None:
        """Update visual selection state."""
        for idx, widget in enumerate(self.option_widgets):
            is_selected = idx == self.selected_option and not self.in_text_mode

            cursor = "› " if is_selected else "  "
            option_text = f"{cursor}{idx + 1}. {self.all_options[idx]}"
            widget.update(option_text)

            widget.remove_class("ask-user-app-option-selected")
            if is_selected:
                widget.add_class("ask-user-app-option-selected")

        # Show/hide text input based on selection
        if self.text_input:
            if self.in_text_mode:
                self.text_input.display = True
                self.text_input.focus()
            else:
                self.text_input.display = False

    def action_move_up(self) -> None:
        if not self.in_text_mode and len(self.all_options) > 0:
            self.selected_option = (self.selected_option - 1) % len(self.all_options)
            self._update_selection()

    def action_move_down(self) -> None:
        if not self.in_text_mode and len(self.all_options) > 0:
            self.selected_option = (self.selected_option + 1) % len(self.all_options)
            self._update_selection()

    def action_select(self) -> None:
        """Handle enter key - either select option or submit text."""
        if self.in_text_mode:
            # Submit text input
            if self.text_input:
                response = self.text_input.value.strip()
                if response:
                    self.post_message(self.ResponseSubmitted(response))
        # Check if "Type something..." was selected
        elif self.all_options[self.selected_option] == "Type something...":
            self.in_text_mode = True
            self._update_selection()
        else:
            # Submit the selected option
            response = self.all_options[self.selected_option]
            self.post_message(self.ResponseSubmitted(response))

    def on_blur(self, event: events.Blur) -> None:
        """Keep focus on this app."""
        if not self.in_text_mode:
            self.call_after_refresh(self.focus)
