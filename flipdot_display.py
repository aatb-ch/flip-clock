## Supporting class for the Flipdot display

import curses

FULL_BLOCK = chr(0x2588)
SQUARE = chr(0x2593) #chr(0x258a)
LINE_HZ = chr(0x2500) # horiz line
LINE_VT = chr(0x2502) # vert line
CORNER_TL = chr(0x250c) # corner tl
CORNER_TR = chr(0x2510) # corner tr
CORNER_BL = chr(0x2514) # corner bl
CORNER_BR = chr(0x2518) # corner br

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