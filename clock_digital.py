## simple digital clock with optional weekday bar

import serial
import datetime
import time
import calendar
import math
import curses
import json

from flipdot_display import FlipdotDisplay

use_flipdot = True
show_debug = True
add_weekday = False
add_year_part = False
add_month_part = False
add_hour_stripe = False
add_hour_bar = False
do_inverting = True 
inversion_interval = 20   ### TODO *60 # seconds
is_inverted = False

panel_width = 28
display_width = panel_width * 2
display_height = 7

font_data_file = './fonts/5by7.regular.dict.json'
font_data_file = './fonts/5by7.regular.bytes.json'

if use_flipdot: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

disp = FlipdotDisplay(display_width, display_height, panel_width)

## load font data
with open(font_data_file, 'r') as inp:
	char_data = json.load(inp)
with open(font_data_file, 'r') as inp:
	char_bytes = json.load(inp)

def convert_to_pixel_val(part, full):
	return math.floor(part * full)

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

def invert_horizontally():
	for icol in range(disp.display_width):
		for irow in range(disp.display_height):
			if disp.display_array[irow][icol] > 0.1:
				disp.display_array[irow][icol] = 0  
			else:
				disp.display_array[irow][icol] = 1
		disp.print()
		if use_flipdot:
			disp.send_to_display(ser)
		time.sleep(0.005)

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
			# for icol in list(range(12)) + list(range(44, disp.display_width)):
			for icol in list(range(47, disp.display_width)):
				disp.display_array[irow][icol] = 1 - disp.display_array[irow][icol]

	## add year_part
	if add_year_part:
		day_of_year = now.timetuple().tm_yday
		year = now.year
		is_leap = calendar.isleap(year)
		year_max = 366 if is_leap else 365
		year_part = convert_to_pixel_val(day_of_year / year_max, disp.display_height)
		for irow in range(6, 6-year_part-1, -1):
			for icol in list(range(4)):
				disp.display_array[irow][icol] = 1 - disp.display_array[irow][icol]

	## add month_part
	if add_month_part:
		month = now.month
		month_max = calendar.monthrange(year, month)[1]
		day_of_month = now.day
		month_part = convert_to_pixel_val(day_of_month / month_max, disp.display_height)
		for irow in range(6, 6-month_part-1, -1):
			for icol in list(range(5, 9)):
				disp.display_array[irow][icol] = 1 - disp.display_array[irow][icol]

	## add hour_bar
	if add_hour_bar:
		# hour_part = (now.hour * 60 + now.minute) / 24 / 60   ### part of day
		hour_part = now.second / 60 ### part of hour
		hour_pix = convert_to_pixel_val(hour_part, disp.display_width)
		for icol in range(hour_pix):
			for irow in range(7):
				disp.display_array[irow][icol] = 1 - disp.display_array[irow][icol]

	if do_inverting:
		should_be_inverted = math.floor((now.hour * 60 * 60 + now.minute * 60 + now.second)/inversion_interval) % 2 == 0 ## math.floor(now.second/10) % 2 == 0
		# stdscr = curses.initscr()
		# stdscr.addstr(8, 60, f'{now.second} {should_be_inverted}')
		# stdscr.refresh()
		if is_inverted:
			disp.invert()
		if should_be_inverted != is_inverted:
			invert_horizontally()
			is_inverted = not is_inverted

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

	if use_flipdot:
		for p in packets:
			ser.write(p)

	time.sleep(1.0)

if show_debug:
	curses.endwin()

if use_flipdot: 
	ser.close()
