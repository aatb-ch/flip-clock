### simple binary clock

import serial
import datetime
import time
import math
import curses
import json

from flipdot_display import FlipdotDisplay

use_serial = True
show_debug = True

panel_width = 28
display_width = panel_width * 2
display_height = 7

## geometry
x_grid = 9 # horizontal spacing
x_start = round((56 - 6 * x_grid) / 2)
x_width = 8
y_hour = 4 # vertical size hour
y_mins = 2 # vertical size mins
y_secs = 1 # vertical size secs

if use_serial: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

disp = FlipdotDisplay(display_width, display_height, panel_width)

while True:
	disp.clear()

	now = datetime.datetime.now()
	hour = now.hour
	mins = now.minute
	secs = now.second
	hour_bits = [int(digit) for digit in f'{hour:06b}']
	mins_bits = [int(digit) for digit in f'{mins:06b}']
	secs_bits = [int(digit) for digit in f'{secs:06b}']

	# hours
	y_curr = 0
	for ib, b in enumerate(hour_bits):
		if b == 0: continue
		for i in range(x_width):
			for j in range(y_hour):
				x = x_start + ib * x_grid + i
				y = y_curr + j
				disp.display_array[y][x] = 1

	# mins
	y_curr += y_hour
	for ib, b in enumerate(mins_bits):
		if b == 0: continue
		for i in range(x_width):
			for j in range(y_mins):
				x = x_start + ib * x_grid + i
				y = y_curr + j
				disp.display_array[y][x] = 1

	# secs
	y_curr += y_mins
	for ib, b in enumerate(secs_bits):
		if b == 0: continue
		for i in range(x_width):
			for j in range(y_secs):
				x = x_start + ib * x_grid + i
				y = y_curr + j
				disp.display_array[y][x] = 1

	if show_debug: 
		disp.print()

	if use_serial:
		disp.send_to_display(ser)

	time.sleep(1.0)

if show_debug:
	curses.endwin()

if use_serial: 
	ser.close()
