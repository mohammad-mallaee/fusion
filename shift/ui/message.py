from shift.ui import UserInterface
from pytermgui import Window, WindowManager, Container, Button, boxes
from time import sleep


def show_message(
    title,
    message,
    button_label="OK",
    manager: UserInterface | WindowManager = None,
    callback: callable = None,
    wait=0,
    stop=False,
):
    manager = manager if manager else WindowManager()

    def on_click(_):
        window.close()
        sleep(wait)
        if stop:
            manager.stop()
        elif callback:
            callback()

    button = Button(button_label, on_click)
    container = Container(
        message, "", button, box=boxes.Box(["     ", "  x  ", "     "])
    )
    window = Window(container, box="ROUNDED", width=80).set_title(title).center()
    manager.add(window)
    if not manager._is_running:
        manager.run()
