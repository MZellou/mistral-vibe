from __future__ import annotations

from textual.widgets import Static

from vibe.acp.utils import VibeSessionMode


class ModeIndicator(Static):
    def __init__(
        self, mode: VibeSessionMode = VibeSessionMode.APPROVAL_REQUIRED
    ) -> None:
        super().__init__()
        self.can_focus = False
        self._mode = mode
        self._update_display()

    def _update_display(self) -> None:
        match self._mode:
            case VibeSessionMode.AUTO_APPROVE:
                self.update("⏵⏵ auto-approve (shift+tab to cycle)")
                self.set_classes("mode-on")
            case VibeSessionMode.PLAN:
                self.update("⏸ plan mode (shift+tab to cycle)")
                self.set_classes("mode-plan")
            case VibeSessionMode.APPROVAL_REQUIRED:
                self.update("⏵ auto-approve off (shift+tab to cycle)")
                self.set_classes("mode-off")

    def set_mode(self, mode: VibeSessionMode) -> None:
        self._mode = mode
        self._update_display()

    # Backward compatibility
    def set_auto_approve(self, enabled: bool) -> None:
        self._mode = (
            VibeSessionMode.AUTO_APPROVE
            if enabled
            else VibeSessionMode.APPROVAL_REQUIRED
        )
        self._update_display()
