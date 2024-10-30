import serial
import random
import datetime
import time
import math
import calendar

use_serial = False
show_debug = True

panel_width = 28
display_width = panel_width * 2
display_height = 7

sec_max = 60
min_max = 60
hour_max = 24
week_max = 7
# month_max ### depends
# year_max  ### depends

class Display:
	def __init__(self):
		self.display_array = []
		for irow in range(display_height):
			row = []
			for icol in range(display_width):
				row.append(0)
			self.display_array.append(row)
	
	def __repr__(self):
		border_line = '-' * (display_width + 2)
		string_repr = border_line + '\n'
		for irow in range(display_height):
			row = ''.join(map(lambda x: ' ' if x == 0 else '#', self.display_array[irow]))
			string_repr += '|'  + row + '|\n'
		string_repr += border_line
		return string_repr
	
	def to_bytes(self, packets):
		for icol in range(display_width):
			byte = sum([self.display_array[i][icol] * 2**(i) for i in range(display_height)])
			panel = 0 if icol < panel_width else 1
			packets[panel].append(byte)
		return packets


if use_serial: ser = serial.Serial('/dev/serial0', 19200)  # open serial port

def convert_to_pixel_val(part):
	return math.floor(part * display_width)

prev_time = datetime.datetime.fromtimestamp(0)
while True:
	disp = Display()
	curr_time = datetime.datetime.now()
	if not int(curr_time.timestamp()) == int(prev_time.timestamp()):
		sec = curr_time.second
		sec_part = convert_to_pixel_val(sec / sec_max)
		mins = curr_time.minute
		min_part = convert_to_pixel_val(mins / min_max)
		hour = curr_time.hour
		hour_part = convert_to_pixel_val(hour / hour_max)

		week = curr_time.isoweekday()
		week_part = convert_to_pixel_val(week / week_max)

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
		for i in range(sec_part):
			disp.display_array[0][i] = 1
		for i in range(min_part):
			disp.display_array[1][i] = 1
		for i in range(hour_part):
			disp.display_array[2][i] = 1
		for i in range(week_part):
			disp.display_array[4][i] = 1
		for i in range(month_part):
			disp.display_array[5][i] = 1
		for i in range(year_part):
			disp.display_array[6][i] = 1

		if show_debug: print(disp)

		prev_time = curr_time


	packets = [bytearray(), bytearray()]
	for p in packets:
		p.append(0x80) # start frame
		p.append(0x83) # display data
		p.append(0x00) # module id
		
	packets = disp.to_bytes(packets)

	for p in packets:
		p.append(0x8f) # end of frame

	if use_serial:
		for p in packets:
			ser.write(p)
		
	time.sleep(0.1)

if use_serial: 
	ser.close()
