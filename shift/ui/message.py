from shift.ui import UserInterface
from pytermgui import Window, WindowManager, Container, Button, boxes


def show_message(
    title,
    message,
    button_label="OK",
    manager: UserInterface | WindowManager = None,
    callback: callable = None,
):
    manager = manager if manager is not None else WindowManager()

    def on_click(btn):
        callback() if callback else manager.stop()

    button = Button(button_label, on_click)
    container = Container(
        message, "", button, box=boxes.Box(["     ", "  x  ", "     "])
    )
    window = Window(container, box="EMPTY_VERTICAL", width=80).set_title(title)
    manager.add(window)
    if not manager._is_running:
        manager.run()
