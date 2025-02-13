## fire simulation

import serial
import time
import curses
import random
from copy import deepcopy

from flipdot_display import FlipdotDisplay

use_flipdot = True
use_graphical = False
use_text = False

panel_width = 28
display_width = panel_width * 2
display_height = 7 # display_width # 7

max_time_burning = -7
max_time_burnt = 17
prob_spreading = 0.4
prob_new_spark = 0.05
prob_burning_sparkle = 0.7

if use_flipdot: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

disp = FlipdotDisplay(display_width, display_height, panel_width, graphical=use_graphical)

# state array of same size as display: burning < 0 counting up to 0, free = 0 , burnt > 0 counting down to 0
state_space = []
for j in range(display_height):
	row = [0] * display_width
	state_space.append(row)

def random_spark(state_space):
	j, i = random.randint(0, display_height-1), random.randint(0, display_width-1)
	if state_space[j][i] == 0:
		state_space[j][i] = max_time_burning
	return state_space

def neighbor_indices(i, j):
	neighbors = (((i-1)%display_width, j), ((i+1)%display_width, j), 
			  (i, (j-1)%display_height), (i, (j+1)%display_height))
	return neighbors

# initial spark
random_spark(state_space)

frame = 0
while True:
	frame += 1
	disp.clear()

	# let the fire spread
	prev_state_space = deepcopy(state_space)
	for j in range(display_height):
		for i in range(display_width):
			state = prev_state_space[j][i]
			if state < 0: # burning
				# spread
				for x,y in neighbor_indices(i, j):
					neighbor_state = prev_state_space[y][x]
					if neighbor_state == 0 and random.random() < prob_spreading:
						state_space[y][x] = max_time_burning
				# turn to burnt
				if state == -1:   # end of burning has come
					state_space[j][i] = max_time_burnt
				else:
					state_space[j][i] += 1		# burning counter
			elif state > 0: # burnt
				# repair
				state_space[j][i] -= 1
			# else:   # free - nothing to do
			# 	pass
	
	# occasionally a new spark
	if random.random() < prob_new_spark:
		random_spark(state_space)
				
	# set display from state_space
	for j in range(display_height):
		for i in range(display_width):
			state = state_space[j][i]
			if state >= 0:
				disp.display_array[j][i] = 0
			else:
				# disp.display_array[j][i] = (-state) % 2   # alternating
				disp.display_array[j][i] =  1 if random.random() < prob_burning_sparkle else 0  # randomized

	if use_text: 
		disp.print()

	if use_flipdot:
		disp.send_to_display(ser)

	if use_graphical:
		disp.send_to_graphical()

	time.sleep(0.1)

if use_text:
	curses.endwin()

if use_flipdot: 
	ser.close()
