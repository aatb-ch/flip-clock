## clock for time, week, year in form of slices/bars

import serial
import random
import datetime
import time
import math
import calendar
import curses

from flipdot_display import FlipdotDisplay

use_serial = False
show_debug = True

panel_width = 28
display_width = panel_width * 2
display_height = 7

sec_max = 60
sec_width = 1
min_max = 60
min_width = 2
hour_max = 24
hour_width = 3
week_max = 7
week_width = 8
# month_max ### depends
# year_max  ### depends1


if use_serial: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

def convert_to_pixel_val(part):
	return math.floor(part * display_width)

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

prev_time = datetime.datetime.fromtimestamp(0)
while True:
	disp = FlipdotDisplay(display_width, display_height, panel_width)
	curr_time = datetime.datetime.now()
	if not int(curr_time.timestamp()) == int(prev_time.timestamp()):
		sec = curr_time.second
		sec_part = convert_to_pixel_val(sec / sec_max)
		sec_parts = convert_to_pixel_range(sec / sec_max, sec_width)
		mins = curr_time.minute
		min_part = convert_to_pixel_val(mins / min_max)
		min_parts = convert_to_pixel_range(mins / min_max, min_width)
		hour = curr_time.hour
		hour_part = convert_to_pixel_val(hour / hour_max)
		hour_parts = convert_to_pixel_range(hour / hour_max, hour_width)

		week = curr_time.isoweekday()
		week_part = convert_to_pixel_val(week / week_max)
		week_parts = convert_to_pixel_range(week / week_max, week_width)

		month = curr_time.month
		year = curr_time.year
		month_max = calendar.monthrange(year, month)[1]
		day_of_month = curr_time.day
		month_part = convert_to_pixel_val(day_of_month / month_max)
		day_of_year = curr_time.timetuple().tm_yday
		is_leap = calendar.isleap(year)
		year_max = 366 if is_leap else 365
		year_part = convert_to_pixel_val(day_of_year / year_max)

		# generate output
		# for i in range(sec_part):
		# 	disp.display_array[0][i] = 1
		for i in range(*sec_parts):
			disp.display_array[0][i] = 1
		#for i in range(min_part):
		#	disp.display_array[1][i] = 1
		for i in range(*min_parts):
			disp.display_array[1][i] = 1
		for i in range(*hour_parts):
			disp.display_array[2][i] = 1
		for i in range(*week_parts):
			disp.display_array[3][i] = 1
		for i in range(month_part):
			disp.display_array[5][i] = 1
		for i in range(year_part):
			disp.display_array[6][i] = 1

		if show_debug: 
			disp.print()

		prev_time = curr_time

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
