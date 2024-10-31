import serial
import random
import time
import math
import curses
import json

from flipdot_display import FlipdotDisplay

use_serial = True
show_debug = True

panel_width = 28
display_width = panel_width * 2
display_height = 7

font_data_file = './fonts/5by7.regular.dict.json'
font_data_file = './fonts/5by7.regular.bytes.json'

if use_serial: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

disp = FlipdotDisplay(display_width, display_height, panel_width)

## load font data
with open(font_data_file, 'r') as inp:
	char_data = json.load(inp)
with open(font_data_file, 'r') as inp:
	char_bytes = json.load(inp)

# text = 'abcdefghijklmnopqrstuvwxyz:ABCDEFGHIJKLMNOPQRSTUVWXYZ:0123456789'
text = ''.join(char_bytes.keys())
# convert to byte sequence
text_bytes = []
for c in text:
	text_bytes.extend(char_bytes[c])
	text_bytes.append(0)

offset = 0
while True:
	disp.clear()

	disp_bytes = []
	for icol in range(disp.display_width):
		disp_bytes.append(text_bytes[(icol + offset) % len(text_bytes)])
	disp.update_from_bytes(disp_bytes)

	offset += 1

	# curr_col = 0
	# for c in text:
	# 	cd = char_data[c]
	# 	for j in range(len(cd)):
	# 		for i in range(len(cd[j])):
	# 			if i + curr_col >= disp.display_width:
	# 				break
	# 			disp.display_array[j][i + curr_col] = cd[j][i]
	# 	curr_col += 6

	if show_debug: 
		disp.print()

	packets = [bytearray(), bytearray()]
	for i, p in enumerate(packets):
		p.append(0x80) # start frame
		p.append(0x83) # display data
		p.append(i) # module id

	packets = disp.to_bytes(packets)

	for p in packets:
		p.append(0x8f) # end of frame

	if use_serial:
		for p in packets:
			ser.write(p)

	time.sleep(0.1)

if show_debug:
	curses.endwin()

if use_serial: 
	ser.close()
