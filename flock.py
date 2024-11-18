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
	velocity: tuple
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
		v = self.velocity
		vperp = (-self.velocity[1], self.velocity[0])
		pix_sum = 0
		cone_pix = []
		for n in self._view_cone:
			delta = (n[0] * v[0] + n[1] * vperp[0], n[0] * v[1] + n[1] * vperp[1])
			pix = (math.floor(self.position[0] + delta[0]) % display_width, math.floor(self.position[1] + delta[1]) % display_height)
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

	def update_velocity(self, size_x, size_y, arr, blobs):
		# change direction if something ahead
		# print(f'>>>> observed  {self.look_ahead(arr)=}')
		if self.protect > 0:
			return
		if self.look_ahead(arr) > 0:
			# print(f'before: {self.velocity}')
			# print(f'.... changing velocity {self.look_ahead(arr)=}')
			self.velocity = random.choice(directions)
			# print(f'after: {self.velocity}')
			### try set to velocity of other
			b_closest = self.find_closest(blops)
			if b_closest:
				self.velocity = b_closest.velocity
				b_closest.protect = 4
				self.protect = 4

		# change direction with some probability
		if random.random() < rand_change_prob:
			self.velocity = random.choice(directions)

	def update(self, size_x, size_y, arr):
		self.position[0] = (self.position[0] + self.velocity[0] + size_x) % size_x
		self.position[1] = (self.position[1] + self.velocity[1] + size_y) % size_y
		self.protect = max(0, self.protect - 1)
	
	def display(self, arr):
		# disp.display_array[math.floor(blop.position[1])][math.floor(blop.position[0])] = 1
		x = math.floor(self.position[0])
		y = math.floor(self.position[1])
		# add dot in direction self.velocity * +-1&2
		arr[y][x] = 1
		arr[(y+self.velocity[1]) % display_height][(x+self.velocity[0]) % display_width] = 1
		arr[(y-self.velocity[1]) % display_height][(x-self.velocity[0]) % display_width] = 1
		arr[(y+self.velocity[1]*2) % display_height][(x+self.velocity[0]*2) % display_width] = 1
		arr[(y-self.velocity[1]*2) % display_height][(x-self.velocity[0]*2) % display_width] = 1


from flipdot_display import FlipdotDisplay

use_serial = True
show_debug = False
use_graphical = False

n_blobs = 7
rand_change_prob = 0.1

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
	# blops.append(Blop(position=[random.randint(0, disp.display_width-1), random.randint(0, disp.display_height-1)], velocity=[(2*random.random()-1)*2, (2*random.random()-1)*2]))
	blops.append(Blop(position=[random.randint(0, disp.display_width-1), random.randint(0, disp.display_height-1)], velocity=random.choice(directions)))

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
