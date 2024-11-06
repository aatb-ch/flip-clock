import turtle

TURTLE_TILE = 40
TURTLE_DOTSIZE = 35
WIDTH = 56
HEIGHT = 7
TURTLE_SCREEN_WIDTH = WIDTH * TURTLE_TILE
TURTLE_SCREEN_HEIGHT = HEIGHT * TURTLE_TILE
MARGIN = TURTLE_TILE
TURTLE_BGCOLOR = '#111111'
TURTLE_FGCOLOR = '#fafafa'

window_offset = 10

def goto(t, col, row):
    y = (row + 0.5) * TURTLE_TILE - TURTLE_SCREEN_HEIGHT * 0.5
    x = (col + 0.5) * TURTLE_TILE - TURTLE_SCREEN_WIDTH * 0.5
    t.goto(x, y)

screen = turtle.Screen()
screen.bgcolor(TURTLE_BGCOLOR)
screen.setup(WIDTH * TURTLE_TILE + MARGIN, HEIGHT * TURTLE_TILE + MARGIN, startx=window_offset, starty=window_offset)

t = turtle.Turtle(visible=False)
t.penup()
t.color(TURTLE_FGCOLOR)
turtle.tracer(False)

for j in range(HEIGHT):
    for i in range(WIDTH):
        goto(t, i, j)
        t.dot(TURTLE_DOTSIZE)

turtle.done()
screen.exitonclick()