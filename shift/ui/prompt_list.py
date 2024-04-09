from pytermgui import Container, boxes, keys, WindowManager
from shift.ui.keyboard_window import KeyboardWindow


class PromptList(Container):
    def __init__(self, choices: list, title = None, callback: callable = None) -> None:
        super().__init__(box=boxes.Box(["     ", "  x  ", "     "]))
        self.choices = choices
        self.set_widgets([""] * len(choices))
        self.choice_index = 0
        self.set_choice_list()
        self.callback = callback
        self.window = KeyboardWindow(
            self, handle_key=self.handle_key, box="EMPTY_VERTICAL", width=80
        ).set_title(title)
        with WindowManager() as manager:
            self.mananger = manager
            manager.add(self.window)

    def set_choice_list(self):
        choices_text = ["> " + choice for choice in self.choices]
        choices_text[self.choice_index] = "[blue]" + choices_text[self.choice_index]
        self.set_widgets(choices_text)

    def handle_key(self, key: str) -> bool:
        if super().handle_key(key):
            return True

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

        return False
