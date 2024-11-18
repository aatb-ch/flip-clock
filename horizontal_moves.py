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
	length: int = 5
	_view_cone = (#(1, 0), (1, 1), (1, -1), 
			    #(2, 0), 
				(2, 1), (2, -1),
			    (3, 0), (3, 1), (3, -1),
			    (4, 0), (4, 1), (4, -1),
				(5, 0), (5, 1), (5, -1), 
				# (5, 2), (5, -2)
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
		closest = None
		min_dist = 10000000
		for b in blops:
			if b == self: continue
			dist = math.sqrt((self.position[0] - b.position[0])**2 + (self.position[1] - b.position[1])**2)
			if dist < min_dist:
				closest = b
				min_dist = dist
		if min_dist <= 5:
			return closest
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

			### try set to velocity closer to other
			b_closest = self.find_closest(blops)
			if b_closest:
				self.velocity = (self.velocity[0] + (b_closest.velocity[0] - self.velocity[0]) * beta, self.velocity[1] + (b_closest.velocity[1] - self.velocity[1]) * beta)
				b_closest.protect = 10
				self.protect = 10

		# change direction with some probability
		if random.random() < rand_change_prob:
			speed = random.random() * 2
			dir = random.choice(directions)
			self.velocity = (speed * dir[0], speed * dir[1])

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
		for i in range(round(self.length/2) + 1):
			arr[(y) % display_height][(x+i) % display_width] = 1
			arr[(y) % display_height][(x-i) % display_width] = 1


from flipdot_display import FlipdotDisplay

use_serial = True
show_debug = True
use_graphical = False

panel_width = 28
display_width = panel_width * 2
display_height = display_width # 7

n_blobs = 4 * display_height
rand_change_prob = 0.05
beta = 0.5

# directions = [(-1, -1), (-1, 0), (-1, 1),
# 			  (0, -1), (0, 1),
# 			  (1, -1), (1, 0), (1, 1),
# 			  ]
directions = [(-1, 0), (1, 0)]

if use_serial: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

disp = FlipdotDisplay(display_width, display_height, panel_width, graphical=use_graphical)
blops = []
for i in range(n_blobs):
	speed = random.random() * 2
	dir = random.choice(directions)
	length = random.randint(3, 7)
	blops.append(Blop(position=[random.randint(0, disp.display_width-1), i % disp.display_height], velocity=(speed * dir[0], speed * dir[1]), length=length))

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

	time.sleep(0.005)

if show_debug:
	curses.endwin()

if use_serial: 
	ser.close()
