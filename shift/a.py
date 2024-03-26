import pytermgui as ptg
import time
class B:
    def __init__(self) -> None:
        self.proccessed: int = 40
        self.valid: int = 12
        self.transfer_size: int = 125723
        self.total_size: int = 283749824
    
def macro_time(fmt: str) -> str:
    return time.strftime(fmt)

def main():
    ptg.tim.define("!time", macro_time)

    with ptg.WindowManager() as manager:
        manager.layout.add_slot("Body")
        manager.add(
            ptg.Window("[bold]The current time is:[/]\n\n[!time 75]%c", box="EMPTY")
        )

if __name__ == "__main__":
    main()