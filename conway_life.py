### conway's life CA simulation
# TODO (simple) cycle detection

import serial
import time
import curses
import random
import math

from flipdot_display import FlipdotDisplay

use_serial = True
show_debug = True

panel_width = 28
display_width = panel_width * 2
display_height = 7

if use_serial: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

disp = FlipdotDisplay(display_width, display_height, panel_width)

def init():
	for j in range(disp.display_height):
		for i in range(disp.display_width):
			if random.random() < 0.25:
				disp.display_array[j][i] = 1
	# ### glider
	# disp.display_array[3][2] = 1
	# disp.display_array[3][3] = 1
	# disp.display_array[3][4] = 1
	# disp.display_array[2][4] = 1
	# disp.display_array[1][3] = 1
	# ### blinker
	# disp.display_array[3][2] = 1
	# disp.display_array[3][3] = 1
	# disp.display_array[3][4] = 1

def count_neighbors(row, col):
	n = 0
	for i in range(-1, 2):
		for j in range(-1, 2):
			n += disp.display_array[(row - i + disp.display_height) % disp.display_height][(col - j + display_width) % disp.display_width]
	n -= disp.display_array[row][col]
	return n

def ca_step():
	to_change  = {}
	for j in range(disp.display_height):
		for i in range(disp.display_width):
			n = count_neighbors(j, i)
			state = disp.display_array[j][i]
			if state > 0:
				# cell lives
				if not (n == 2 or n == 3):
					to_change[(j, i)] = 0
			else:
				if n == 3:
					to_change[(j, i)] = 1
	for k, v in to_change.items():
		disp.display_array[k[0]][k[1]] = v
	return len(to_change)

def add_random():
	for i in range(10):
		disp.display_array[random.randint(0, disp.display_height-1)][random.randint(0, disp.display_width-1)] = 1

init()
frame = 0
while True:
	# disp.clear()

	disp.print()
	disp.send_to_display(ser)
	changes = ca_step()

	if changes < 8 or frame > 200:
		frame = 0
		disp.clear()
		disp.print()
		disp.send_to_display(ser)
		time.sleep(1)
		init()

	time.sleep(0.15)
	frame += 1

if show_debug:
	curses.endwin()

if use_serial: 
	ser.close()
