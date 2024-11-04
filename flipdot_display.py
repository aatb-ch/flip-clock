## Supporting class for the Flipdot display

import curses

class FlipdotDisplay:
	def __init__(self, display_width, display_height, panel_width):
		self.display_width = display_width
		self.display_height = display_height
		self.panel_width = panel_width
		self.display_array = []
		for irow in range(self.display_height):
			row = []
			for icol in range(self.display_width):
				row.append(0)
			self.display_array.append(row)

	def __repr__(self):
		border_line = '-' * (self.display_width + 2)
		string_repr = border_line + '\n'
		for irow in range(self.display_height):
			row = ''.join(map(lambda x: ' ' if x == 0 else '#', self.display_array[irow]))
			string_repr += '|'  + row + '|\n'
		string_repr += border_line
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