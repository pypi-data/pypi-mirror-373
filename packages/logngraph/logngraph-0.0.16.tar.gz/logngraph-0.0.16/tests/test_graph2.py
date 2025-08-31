from logngraph.graph import *
from time import sleep

w = Window("Windows 12", 900, 900, True)

while w.running:
    w.handle_events()
    w.fill("#999999")

    w.translate(500, 500)
    w.rotate(45)

    w.rect((0, 0), (50, 150), color="#ffffff")
    w.line((0, 0), (150, 50), color="#000000")
    w.polygon((0, 0), (150, 50), (500, 10), color="#ffffff")

    w.rotate(-45)
    w.write((0, 0), "Hello, World!", "#000000", size=32)

    w.update()
    sleep(0.05)

