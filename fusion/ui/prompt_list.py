from pytermgui import boxes, keys
from fusion.ui.keyboard_window import KeyboardWindow
from fusion.ui.container import AlignedContainer


class PromptList(AlignedContainer):
    def __init__(
        self, ui, choices: list, title=None, callback: callable = None
    ) -> None:
        super().__init__(box=boxes.Box(["     ", "x", "     "]))
        self.choices = choices
        self.set_widgets([""] * len(choices))
        self.choice_index = 0
        self.set_choice_list()
        self.callback = callback
        self.window = (
            KeyboardWindow(self, handle_key=self.handle_key, box="ROUNDED", width=80)
            .set_title(title)
            .center()
        )
        ui.show(self.window)

    def set_choice_list(self):
        choices_text = ["> " + choice for choice in self.choices]
        choices_text[self.choice_index] = "[#00eaff]" + choices_text[self.choice_index]
        self.set_widgets(choices_text)

    def handle_key(self, key: str) -> bool:
        if key == keys.DOWN and self.choice_index < len(self.choices) - 1:
            self.choice_index += 1
            self.set_choice_list()
            return True

        if key == keys.UP and self.choice_index > 0:
            self.choice_index -= 1
            self.set_choice_list()
            return True

        if key == keys.RETURN or key == keys.ENTER:
            self.callback(self.choice_index)
            return True

        return False
