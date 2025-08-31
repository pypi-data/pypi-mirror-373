from logngraph.graph import *
from time import sleep

w = Window("Windows 12", 900, 900, True)

while w.running:
    w.handle_events()
    w.fill("#00ff00")
    w.translate(515, 150)
    w.rotate(90)
    w.circle((0, 0), 150, color="#999999")
    w.rect((150, 50), (200, 150), color="#ffffff")
    w.ellipse((250, 250), (300, 500), color="#ffff00")
    w.line((0, 0), (800, 900), color="#0000ff")
    w.polygon((750, 750), (800, 400), (35, 600), color="#ff0000")
    w.write((60, 150), text="Hello, World!", color="#ffffff", bg_color="#000000", antialias=True, size=32, font="font.ttf")
    w.update()
    sleep(0.05)
