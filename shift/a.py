import pytermgui as ptg
import random

from dataclasses import dataclass
from threading import Thread
from time import sleep

from pytermgui import Container, StyleManager


@dataclass
class WeatherData:
    state: str
    wind: str
    clouds: str


class Weather(Container):
    # We want to retain the Container styles, so we merge in some new ones
    styles = StyleManager.merge(
        Container.styles,
        sunny="yellow",
        cloudy="grey",
        rainy="darkblue",
        snowy="snow",
        detail="245",
    )

    # Same story as above; unpacking into sets allows us to merge 2 dicts!
    chars = {
        **Container.chars,
        **{
            "sunny": "☀",
            "cloudy": "☁",
            "rainy": "☂",
            "snowy": "☃",
        },
    }

    def __init__(self, location: str, timeout: int, **attrs) -> None:
        super().__init__(**attrs)

        self.location = location
        self.timeout = timeout
        self.data = self._request_data()


    def _request_data(self) -> WeatherData:
        return WeatherData(
            state=random.choice(["sunny", "cloudy", "rainy"]),
            wind=f"{random.randint(12, 23)}kph N/W",
            clouds=random.choice(["scattered", "broken", "overcast"]),
        )

    def update_content(self) -> None:
        state = self.data.state

        style = self.styles[state]
        char = self._get_char(state)
        icon = style(char)

        self.set_widgets(
            [
                f"{icon} It is currently {state} in {self.location}. {icon}",
                "",
                f"{self.styles.detail('Wind')}: {self.data.wind}",
                f"{self.styles.detail('Clouds')}: {self.data.clouds}",
            ]
        )


class B(ptg.Widget):
    def __init__(self, **attrs: ptg.Any) -> None:
        super().__init__(**attrs)
        self.valid = 0
        self.proccessed = 0
    def update(self, is_valid=True):
        self.valid += 1
        self.proccessed += 1

    def get_lines(self) -> list[str]:
        return [f"transferring {self.valid} / {self.proccessed} files"]


def list(ads: Weather):
    while True:
        ads.data = ads._request_data()
        ads.update_content()
        sleep(0.2)


def main():
    b = Weather("Isfahan", 1)

    with ptg.WindowManager() as manager:
        manager.layout.add_slot("Body")
        manager.add(ptg.Window(b))
        Thread(target=manager.run, daemon=True).start()
        list(b)


if __name__ == "__main__":
    main()
