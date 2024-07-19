from pytermgui import Container, Button, boxes, Splitter
from time import sleep
from shift.ui import UserInterface
from shift.ui.keyboard_window import KeyboardWindow


def confirm(
    title,
    message,
    ui: UserInterface = None,
    callback: callable = None,
    wait=0.5,
    stop=False,
):
    ui = ui if ui else UserInterface()

    def confirm(btn=None):
        callback()

    def reject(btn=None):
        if stop:
            window.close()
            sleep(wait)
            ui.stop()

    def handle_key(key: str):
        if key == "y":
            confirm()
            return True
        elif key == "n":
            reject()
            return True
        return False

    yes = Button("Yes (y)", confirm)
    no = Button("No (n)", reject)
    container = Container(
        message,
        "",
        Splitter("", yes, no, "").center().set_char("separator", " "),
        box=boxes.Box(["     ", "  x  ", "     "]),
    )
    window = (
        KeyboardWindow(container, handle_key=handle_key, box="ROUNDED", width=80)
        .set_title(title)
        .center()
    )
    ui.show(window)
    if not ui._is_running:
        ui.run()
