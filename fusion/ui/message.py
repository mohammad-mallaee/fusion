from fusion.ui import UserInterface
from pytermgui import Window, Container, Button, boxes


def show_message(
    title,
    message,
    button_label="OK",
    ui: UserInterface = None,
    callback: callable = None,
    wait=0.5,
    stop=False,
):
    ui = ui if ui else UserInterface()

    def on_click(_):
        if stop:
            ui.animate_stop(wait)
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
