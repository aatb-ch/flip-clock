import serial
import time
import curses
import itertools
import random
import math

from flipdot_display import FlipdotDisplay

use_serial = True
show_debug = True
max_perc = 0.8
period = 10 # secs

panel_width = 28
display_width = panel_width * 2
display_height = 7

def pdf(x, mu=0.0, sigma=1.0):     ### gaussian distribution - not normalized - ie always up to 1
    xn = float(x - mu) / sigma
    return math.exp(-xn*xn/2.0) ### / math.sqrt(2.0*math.pi) / sigma

if use_serial: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

disp = FlipdotDisplay(display_width, display_height, panel_width)

def approximate_prob(p, arr):
	ntries = 10
	for k in range(ntries):
		pcurr = sum(arr) / len(arr)
		if pcurr - p > 1/len(arr)/2:
			# need to remove
			for n in range(ntries):
				ind = random.randint(0, len(arr)-1)
				if arr[ind] > 0:
					arr[ind] = 0
				break
		elif p - pcurr > 1/len(arr)/2:
			# need to add
			for n in range(ntries):
				ind = random.randint(0, len(arr)-1)
				if arr[ind] < 0.001:
					arr[ind] = 1
				break
	return arr

start = time.time()
while True:
	# disp.clear()

	# perm = list(itertools.product(range(disp.display_width), range(disp.display_height)))

	t = time.time() - start

	strength = (math.sin(t / period * 2 * math.pi) + 1) / 2    # going from 0 to 1
	mu = disp.display_width/2
	sigma = 3.0 + 18.0 * strength
	scaler = 0.1 + strength * 0.9 

	for i in range(disp.display_width):
		arr = [disp.display_array[j][i] for j in range(disp.display_height)]
		prob = pdf(i, mu, sigma)
		arr = approximate_prob(prob * scaler, arr)
		for j in range(disp.display_height):
			disp.display_array[j][i] = arr[j]

	# strength = (math.sin(t / period * 2 * math.pi) + 1) / 2    # going from 0 to 1
	# mu = disp.display_width/2
	# sigma = 3.0 + 15.0 * strength
	# scaler = 0.2 + strength *0.8
	# bytes = []
	# for i in range(disp.display_width):
	# 	prob = pdf(i, mu, sigma)
	# 	for j in range(disp.display_height):
	# 		if random.random() < prob:
	# 			disp.display_array[j][i] = 1

	disp.print()

	time.sleep(0.1)

if show_debug:
	curses.endwin()

if use_serial: 
	ser.close()
