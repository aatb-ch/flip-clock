## display perlin noise

import serial
import time
import curses
import random
from copy import deepcopy
from perlin import perlin

from flipdot_display import FlipdotDisplay

use_flipdot = False
use_graphical = True
use_text = False

panel_width = 28
display_width = panel_width * 2
display_height = 7

flicker_max = 10
scale_frame = 1/15.0 / flicker_max
scale_x = 1/10.0
scale_y = 1/5.0
threshold = 0.55

if use_flipdot: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

disp = FlipdotDisplay(display_width, display_height, panel_width, graphical=use_graphical)

perl = perlin.PerlinNoiseFactory(3)

frame = 0
flicker = {}
disp_prev = deepcopy(disp.display_array)
while True:
	disp.clear()
	frame += 1

	update = (frame % flicker_max) == 0

	if update:
		disp_prev = deepcopy(disp.display_array)
		for j in range(display_height):
			for i in range(display_width):
				v = (perl(i * scale_x, j * scale_y, frame * scale_frame) * perl.scale_factor + 1) * 0.5
				if v > threshold:
					disp.display_array[j][i] = 1
				else:
					disp.display_array[j][i] = 0
				if disp_prev[j][i] != disp.display_array[j][i]:
					flicker[(i, j)] = flicker_max
	else:
		disp.display_array = disp_prev
		# print(frame, len(list(filter(lambda v: v > 0, flicker.values()))))
		print(frame, len(flicker.keys()))
		for j in range(display_height):
			for i in range(display_width):
				if (i, j) in flicker.keys():
					if flicker[(i,j)] > 0:
						# just flip in this case ... with some probability
						# if random.random() > 0.5:
						disp.display_array[j][i] = 1 - disp.display_array[j][i]
						flicker[(i,j)] -= 1
					else:
						del flicker[(i, j)]
	
	if use_text: 
		disp.print()

	if use_flipdot:
		disp.send_to_display(ser)

	if use_graphical:
		disp.send_to_graphical()

	time.sleep(0.2)

if use_text:
	curses.endwin()

if use_flipdot: 
	ser.close()
