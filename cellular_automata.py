### show the development of a 1d cellular automaton

import serial
import time
import curses
import random
import math

from flipdot_display import FlipdotDisplay

use_serial = False
show_debug = True
use_graphical = True

period = 10 # secs

panel_width = 28
display_width = panel_width * 2
display_height = 7

if use_serial: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

disp = FlipdotDisplay(display_width, display_height, panel_width, graphical=use_graphical)

# CA_RULE = 30 # class 3
# CA_SIZE = 256 # 56 for the rules with 'holes'
# CA_START_BIT = round(disp.display_width/2)

# CA_RULE = 90 # sierpinski
# CA_SIZE = 56 # 56 for the rules with 'holes'
# CA_START_BIT = round(disp.display_width/2)

CA_RULE = 110 # class 4
CA_SIZE = 256 # 56 for the rules with 'holes'
CA_START_BIT = round(disp.display_width-1)

# CA_RULE = 184 # 'majority rule'
# CA_SIZE = 56 # 56 for the rules with 'holes'
# CA_START_BIT = -1    # to signal random start

def expand_rule(rule):
    bits = [int(digit) for digit in f'{rule:08b}']
    bits.reverse()
    ruleset = dict()
    for i in range(8):
        ibits = tuple(int(digit) for digit in f'{i:03b}')
        ruleset[ibits] = bits[i]
        # print(i, ibits)
    return ruleset

def init():
    if CA_START_BIT >= 0:
        curr_state = [0] * CA_SIZE
        curr_state[CA_START_BIT] = 1
    else:
        curr_state = [0 if random.random() > 0.5 else 1 for i in range(CA_SIZE)]
    return curr_state

def evolve(curr):
    new_state = []
    for i in range(0, CA_SIZE):
        window = (curr[(i-1)%CA_SIZE], curr[i], curr[(i+1)%CA_SIZE])
        new_state.append(rule_set[window])
    return new_state

rule_set = expand_rule(CA_RULE)
curr_state = init()

ca_frame = 0
while True:
      
	# map curr_state to disp
	for i in range(disp.display_width):
		disp.display_array[ca_frame] = curr_state[:disp.display_width]
      
	if show_debug: disp.print()
	if use_serial: disp.send_to_display(ser)
	if use_graphical: disp.send_to_graphical()
   
    # evolve
	curr_state = evolve(curr_state)

    # scroll if required
	ca_frame += 1
	if ca_frame >= disp.display_height:
		disp.scroll_up()
		ca_frame = disp.display_height -1

	time.sleep(0.25)

if show_debug:
	curses.endwin()

if use_serial: 
	ser.close()
