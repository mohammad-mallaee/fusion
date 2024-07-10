from shift.ui import UserInterface
from pytermgui import Window, WindowManager, Container, Button, boxes
from time import sleep


def show_message(
    title,
    message,
    button_label="OK",
    ui: UserInterface = None,
    callback: callable = None,
    wait=0,
    stop=False,
):
    ui = ui if ui else WindowManager()

    def on_click(_):
        window.close()
        sleep(wait)
        if stop:
            ui.stop()
        elif callback:
            callback()

    button = Button(button_label, on_click)
    container = Container(
        message, "", button, box=boxes.Box(["     ", "  x  ", "     "])
    )
    window = Window(container, box="ROUNDED", width=80).set_title(title).center()
    ui.show(window)
    if not ui._is_running:
        ui.run()
