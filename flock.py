### flock simulation

import serial
import time
import curses
import random
import math
from dataclasses import dataclass

@dataclass
class Blop:
	position: list
	direction: tuple 
	speed: float
	protect: int = 0
	_view_cone = (#(1, 0), (1, 1), (1, -1), 
			    #(2, 0), 
				(2, 1), (2, -1),
			    (3, 0), (3, 1), (3, -1),
			    (4, 0), (4, 1), (4, -1),
				(5, 0), (5, 1), (5, -1), 
				(5, 2), (5, -2)
				)
	
	def look_ahead(self, arr):
		v = self.direction
		vperp = (-self.direction[1], self.direction[0])
		pix_sum = 0
		cone_pix = []
		for n in self._view_cone:
			delta = (n[0] * v[0] + n[1] * vperp[0], n[0] * v[1] + n[1] * vperp[1])
			# pix = (math.floor(self.position[0] + delta[0]) % display_width, math.floor(self.position[1] + delta[1]) % display_height)
			pix = (round(self.position[0] + delta[0]) % display_width, round(self.position[1] + delta[1]) % display_height)
			cone_pix.append(delta)
			pix_sum += arr[pix[1]][pix[0]]
		return pix_sum
	
	def find_closest(self, blops):
		# identify the blop that is closest (in any direction as easiest)
		for b in blops:
			if b == self: continue
			dist = math.sqrt((self.position[0] - b.position[0])**2 + (self.position[1] - b.position[1])**2)
			if dist <= 3:
				return b
		return None
	
	@staticmethod
	def random_direction():
		return random.choice(directions)
	
	@staticmethod
	def random_speed():
		return random.random() * 1.2 + 0.5

	def update_velocity(self, size_x, size_y, arr, blobs):
		# change direction if something ahead
		if self.protect > 0:
			return
		if self.look_ahead(arr) > 0:
			# self.direction = self.random_direction()
			# self.speed =  #### keep speed the same
			### try set to velocity of other
			b_closest = self.find_closest(blops)
			if b_closest:
				self.direction = b_closest.direction
				self.speed = self.speed + (b_closest.speed - self.speed) * beta
				b_closest.protect = protect_max
				self.protect = protect_max

		# change direction with some probability
		if random.random() < rand_change_prob:
			self.direction = self.random_direction()
			self.speed = self.random_speed()

	def update(self, size_x, size_y, arr):
		self.position[0] = (self.position[0] + self.direction[0]*self.speed + size_x) % size_x
		self.position[1] = (self.position[1] + self.direction[1]*self.speed + size_y) % size_y
		self.protect = max(0, self.protect - 1)
	
	def display(self, arr):
		# x = math.floor(self.position[0])
		# y = math.floor(self.position[1])
		x = round(self.position[0]) % display_width
		y = round(self.position[1]) % display_height
		v0 = self.direction[0]
		v1 = self.direction[1]
		# add dots in direction self.velocity resp (v0, v1) * +-1&2
		arr[y][x] = 1
		arr[(y+v1) % display_height][(x+v0) % display_width] = 1
		arr[(y-v1) % display_height][(x-v0) % display_width] = 1
		arr[(y+v1*2) % display_height][(x+v0*2) % display_width] = 1
		arr[(y-v1*2) % display_height][(x-v0*2) % display_width] = 1

def sign(x):
	eps = 0.000000001
	if x > eps:
		return 1
	elif x < -eps:
		return -1
	return 0

from flipdot_display import FlipdotDisplay

use_serial = True
show_debug = False
use_graphical = False

n_blobs = 17
rand_change_prob = 0.005
beta = 0.3
protect_max = 0

panel_width = 28
display_width = panel_width * 2
display_height = 7 # display_width # 7

directions = [(-1, -1), (-1, 0), (-1, 1),
			  (0, -1), (0, 1),
			  (1, -1), (1, 0), (1, 1),
			  ]
# directions = [(-1, 0), (1, 0)]

if use_serial: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

disp = FlipdotDisplay(display_width, display_height, panel_width, graphical=use_graphical)
blops = []
for i in range(n_blobs):
	blops.append(Blop(position=[random.randint(0, disp.display_width-1), random.randint(0, disp.display_height-1)], direction=Blop.random_direction(), speed=Blop.random_speed()))

while True:
	disp.clear()

	for blop in blops:
		blop.display(disp.display_array)
	for blop in blops:
		blop.update_velocity(disp.display_width, disp.display_height, disp.display_array, blops)
		blop.update(disp.display_width, disp.display_height, disp.display_array)

	if show_debug: disp.print()
	if use_graphical: disp.send_to_graphical()
	if use_serial: disp.send_to_display(ser)

	# print('------------')
	# for ib, b in enumerate(blops):
	# 	print(f'{ib=} {b=} {b.look_ahead(disp.display_array)}')

	time.sleep(0.01)

if show_debug:
	curses.endwin()

if use_serial: 
	ser.close()
