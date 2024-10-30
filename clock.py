import serial
import random

ser = serial.Serial('/dev/serial0', 19200)  # open serial port


while True:
	packet1 = bytearray()
	packet2 = bytearray()
	packet1.append(0x80) # start frame
	packet1.append(0x83) # display data
	packet1.append(0x00) # module id
	packet2.append(0x80) # start frame
	packet2.append(0x83) # display data
	packet2.append(0x01) # module id

	i=0
	while i in range(28):
		packet1.append(random.randint(0,128)) # data at col i
		packet2.append(random.randint(0,128)) # data at col i
		i=i+1

	packet1.append(0x8f) # end of frame
	packet2.append(0x8f)

	ser.write(packet1)
	ser.write(packet2)
ser.close()
