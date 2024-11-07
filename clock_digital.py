## simple digital clock with optional additions

import serial
import datetime
import time
import calendar
import math
import curses
import json

from flipdot_display import FlipdotDisplay

use_flipdot = True
use_graphical = False
use_text = True

add_weekday = False     # add vertical bar for day of week
add_year_part = False   # add vertical bar for part of year
add_month_part = False  # add vertical bar for part of month
add_hour_stripe = False # add an inverting stripe in the background moving horizontally
add_hour_bar = False    # add a growing inverting horizontal background bar
do_inverting = True     # invert clock after inversion_interval
inversion_interval = 20 *60 # seconds
is_inverted = False
add_day_dots = False    # add dots as inverting background one by one over time

panel_width = 28
display_width = panel_width * 2
display_height = 7

font_data_file = './fonts/5by7.regular.dict.json'
font_data_file = './fonts/5by7.regular.bytes.json'

if use_flipdot: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

disp = FlipdotDisplay(display_width, display_height, panel_width, graphical=use_graphical)

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
			disp.display_array[irow][icol] = invert_value(disp.display_array[irow][icol])
		disp.print()
		if use_flipdot:
			disp.send_to_display(ser)
		time.sleep(0.001)

def invert_value(x):
	if x > 0.1:
		return 0  
	return 1 

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
	
	if add_day_dots:
		# secs = now.hour * 60 * 60 + now.minute * 60 + now.second
		# secs_part = convert_to_pixel_val(secs / 86400, disp.display_height * disp.display_width)
		secs = now.minute * 60 + now.second
		secs_part = convert_to_pixel_val(secs / 3600, disp.display_height * disp.display_width)
		for i in range(secs_part):
			irow, icol = divmod(i, disp.display_width)
			disp.display_array[irow][icol] = invert_value(disp.display_array[irow][icol])

	if use_text: 
		disp.print()

	if use_flipdot:
		disp.send_to_display(ser)

	time.sleep(1.0)

if use_text:
	curses.endwin()

if use_flipdot: 
	ser.close()
