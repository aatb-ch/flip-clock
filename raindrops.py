### raindrop simulation

import serial
import time
import curses
import itertools
import random
import math
from wave_simulation.simulation import Simulation, Drop

from flipdot_display import FlipdotDisplay

use_serial = False
show_debug = True

panel_width = 28
display_width = panel_width * 2
display_height = 7

def add_random_drop():
	if random.random() < 0.02:
		simulation.drops.append(Drop(position=[random.randint(0, disp.display_width-1), random.randint(0, disp. display_height-1)], startframe=simulation.frame))

if use_serial: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

disp = FlipdotDisplay(display_width, display_height, panel_width)

simulation = Simulation()
while True:
	disp.clear()

	simulation.step()

	add_random_drop()

	for j in range(disp.display_height):
		for i in range(disp.display_width):
			p = simulation.pressure[j][i]
			if p > 0.05:
				if random.random() < 10 * p:
					disp.display_array[j][i] = 1

	disp.print()

	time.sleep(0.1)

if show_debug:
	curses.endwin()

if use_serial: 
	ser.close()
