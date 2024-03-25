import time
from pytermgui import Container, tim, palette

palette.regenerate(primary="lightgreen")
container = Container(
    "[bold accent]This is my example",
    "",
    "[surface+1 dim italic]It is very cool, you see",
    "",
    {"My first label": ["Some button"]},
    {"My second label": [True]},
    "",
    ("Left side", "Middle", "Right side"),
    "",
    ["Submit button"]
)

for line in container.get_lines():
    tim.print(line)
