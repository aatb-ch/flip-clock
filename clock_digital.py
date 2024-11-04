import serial
import datetime
import time
import math
import curses
import json

from flipdot_display import FlipdotDisplay

add_hour_stripe = False
use_serial = True
show_debug = True
add_weekday = True

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

def convert_to_pixel_range(part, width):
	main = math.floor(part * display_width)
	w_half = math.floor(width/2)
	low =  max(0, main - w_half)
	if width % 2 == 0:
		# even width
		high = min(main + w_half - 1, display_width-1)
	else:
		high = min(main + w_half, display_width-1)
	return low, high+1

hour_ind = 1
while True:
	disp.clear()

	now = datetime.datetime.now()
	time_str = now.strftime("%H:%M")
	text_bytes = []
	for c in time_str:
		text_bytes.extend(char_bytes[c])
		if c != ':':
			text_bytes.append(0)

	disp_bytes = [0] * disp.display_width
	offset = 14
	for icol in range(len(text_bytes)):
		if icol + offset >= disp.display_width:
			break
		disp_bytes[(icol + offset)] = text_bytes[icol]
	disp.update_from_bytes(disp_bytes)

	## add hour_stripe
	if add_hour_stripe and hour_ind == 1:
		hour_part = (now.hour * 60 + now.minute) / 24 / 60
		low, high = convert_to_pixel_range(hour_part, 6)
		for icol in range(low, high):
			for irow in range(7):
				disp.display_array[irow][icol] = 1 - disp.display_array[irow][icol]
	hour_ind *= -1

	## add weekday
	if add_weekday:
		s = now.weekday()
		for irow in range(6, 6-s-1, -1):
			for icol in list(range(12)) + list(range(44, disp.display_width)):
				disp.display_array[irow][icol] = 1 - disp.display_array[irow][icol]

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

	time.sleep(1.0)

if show_debug:
	curses.endwin()

if use_serial: 
	ser.close()
