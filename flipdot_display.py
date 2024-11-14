## Supporting class for the Flipdot display

import curses
import time

FULL_BLOCK = chr(0x2588)
SQUARE = chr(0x2593) #chr(0x258a)
LINE_HZ = chr(0x2500) # horiz line
LINE_VT = chr(0x2502) # vert line
CORNER_TL = chr(0x250c) # corner tl
CORNER_TR = chr(0x2510) # corner tr
CORNER_BL = chr(0x2514) # corner bl
CORNER_BR = chr(0x2518) # corner br

TURTLE_TILE = 10
TURTLE_DOTSIZE = 0.925 * TURTLE_TILE
MARGIN = TURTLE_TILE * 2
TURTLE_BGCOLOR = '#111111'
TURTLE_FGCOLOR = '#fafafa'

from functools import wraps
def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper

class FlipdotDisplay:
	def __init__(self, display_width, display_height, panel_width, graphical=False):
		self.display_width = display_width
		self.display_height = display_height
		self.panel_width = panel_width
		self.graphical = graphical
		self.display_array = []
		for irow in range(self.display_height):
			row = []
			for icol in range(self.display_width):
				row.append(0)
			self.display_array.append(row)
		if self.graphical:
			import turtle
			TURTLE_SCREEN_WIDTH = display_width * TURTLE_TILE
			TURTLE_SCREEN_HEIGHT = display_height * TURTLE_TILE
			window_offset = 10

			self.screen = turtle.Screen()
			self.screen.bgcolor(TURTLE_BGCOLOR)
			self.screen.setup(TURTLE_SCREEN_WIDTH + MARGIN, TURTLE_SCREEN_HEIGHT + MARGIN, startx=window_offset, starty=window_offset)

			self.turtle = turtle.Turtle(visible=False)
			self.turtle.penup()
			self.turtle.color(TURTLE_FGCOLOR)
			# self.screen.tracer(False)
			turtle.tracer(False)
			self.turtle.speed('fastest')

	def __repr__(self):
		border_line_top = CORNER_TL + LINE_HZ * (self.display_width) + CORNER_TR
		string_repr = border_line_top + '\n'
		for irow in range(self.display_height):
			row = ''.join(map(lambda x: ' ' if x == 0 else SQUARE, self.display_array[irow]))
			string_repr += LINE_VT  + row + LINE_VT + '\n'
		border_line_bottom = CORNER_BL + LINE_HZ * (self.display_width) + CORNER_BR
		string_repr += border_line_bottom
		return string_repr
	
	def update_from_bytes(self, bytes):
		for ib, b in enumerate(bytes):
			bits = [int(digit) for digit in f'{b:07b}']
			for ibit, bit in enumerate(bits):
				self.display_array[ibit][ib] = bit
			
	def clear(self):
		self.display_array = []
		for irow in range(self.display_height):
			row = []
			for icol in range(self.display_width):
				row.append(0)
			self.display_array.append(row)        
	
	def invert(self):
		for irow in range(self.display_height):
			for icol in range(self.display_width):
				if self.display_array[irow][icol] > 0.1:
					self.display_array[irow][icol] = 0  
				else:
					self.display_array[irow][icol] = 1

	def scroll_up(self):
		for irow in range(0, self.display_height-1):
			self.display_array[irow] = self.display_array[irow+1]
		self.display_array[self.display_height-1] = [0] * self.display_width

	def print(self):
		text_display = str(self).split('\n')
		stdscr = curses.initscr()
		for i, s in enumerate(text_display):
			stdscr.addstr(i, 0, s)
		stdscr.refresh()

	def to_bytes(self, packets):
		for icol in range(self.display_width-1, -1, -1):
			byte = sum([self.display_array[i][icol] * 2**(self.display_height-i-1) for i in range(self.display_height)])
			panel = 1 if icol < self.panel_width else 0
			packets[panel].append(byte)
		return packets
	
	def send_to_display(self, ser):
		packets = [bytearray(), bytearray()]
		for i, p in enumerate(packets):
			p.append(0x80) # start frame
			p.append(0x83) # display data
			p.append(i) # module id

		packets = self.to_bytes(packets)

		for p in packets:
			p.append(0x8f) # end of frame

		for p in packets:
			ser.write(p)

	def send_to_graphical(self):
		import turtle
		self.turtle.clear()
		for row in range(self.display_height):
			for col in range(self.display_width):
				if self.display_array[row][col] > 0.1:
					y = (self.display_height - row - 0.5) * TURTLE_TILE - self.display_height * TURTLE_TILE * 0.5
					x = (col + 0.5) * TURTLE_TILE - self.display_width * TURTLE_TILE * 0.5
					self.turtle.goto(x, y)
					self.turtle.dot(TURTLE_DOTSIZE)
		turtle.update()
				