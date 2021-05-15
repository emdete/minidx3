#!/usr/bin/env python3
from time import sleep
from datetime import datetime
from serial import Serial

debug = False

def check_crc(buf):
	crc = 0
	for b in buf[2:-3]:
		crc ^= b
	return crc

def size(buf):
	return [len(buf) & 0xff00 >> 8, len(buf) & 0x00ff, ]

def send_receive(device, buf, size=5):
	buf.insert(0, 2)
	buf.append(13)
	buf = bytes(buf)
	if debug: print(repr(buf))
	device.write(buf)
	if debug: sleep(.3)
	buf = device.read(size)
	if debug: print(repr(buf))
	if not buf or buf[0] != 2 or buf[-1] != 13:
		raise Exception('Protocol error in result "{}"'.format(buf))
	return buf

# L - login
def login(device, pin='0000'):
	buf = [ord(c) for c in pin]
	buf.insert(0, ord('L'))
	return send_receive(device, buf)[1] == ord('A')

# O - logout
def logout(device):
	num = [ord('O'), ]
	return send_receive(device, num)[1] == ord('A')

# P - set password
def set_password(device, pin):
	buf = [ord(c) for c in pin]
	buf.insert(0, ord('P'))
	return send_receive(device, buf)[1] == ord('A')

# B - get register
def get_register(device, no):
	no = [ord(c) for c in '{:02x}'.format(no)]
	#no = [no >> 8, no & 0xff, ]
	buf = [ord('B'), ] + no
	buf = send_receive(device, buf, 7)
	if buf[1] == ord('A'):
		check_crc(buf)
		return int(buf[2:-3].decode(), 16)

# C - set register
def set_register(device, no, value):
	no = [ord(c) for c in '{:02x}'.format(no)]
	buf = [ord('C'), ]

# F - get product version
def get_product_version(device):
	buf = [ord('F'), ]
	buf = send_receive(device, buf, 100)
	if buf[1] == ord('A'):
		check_crc(buf)
		# unclean binary zeros, unclear =, crc?
		return buf[3:-4].strip(b'\00').decode().split('\r')

# S - set date
def set_date(device):
	date = datetime.now()
	date = '2021051421056' #TODO
	buf = [ord(c) for c in date]
	buf.insert(0, ord('S'))
	return send_receive(device, buf)[1] == ord('A')

# T - get time and date
def get_date(device):
	buf = [ord('T'), ]
	buf = send_receive(device, buf, 18)
	if buf[1] == ord('A'):
		# crc included?
		check_crc(buf)
		return buf[2:-3].decode()

# N - get number of records
def get_number_of_records(device):
	buf = [ord('N'), ]
	buf = send_receive(device, buf, 9)
	if buf[1] == ord('A'):
		check_crc(buf)
		return int(buf[2:-3].decode(), 16)

# G - get record
def get_record(device, no):
	no = [ord(c) for c in '{:04x}'.format(no)]
	#no = [no >> 8, no & 0xff, ]
	buf = [ord('G'), ] + no
	buf = send_receive(device, buf, 200)
	if buf[1] == ord('A'):
		return buf[2:-1] # .decode().split('?')

# E - erase records
def erase_records(device):
	buf = [ord('E'), ]
	return send_receive(device, buf)[1] == ord('A')

with Serial(port='/dev/ttyUSB0', baudrate=int(19200), ) as device:
	device.rtscts = False
	device.xonxoff = False
	device.timeout = 1
	print('login', login(device), )
	if debug:
		print('get_product_version', get_product_version(device), )
	if debug:
		for idx in range(256):
			print('get_register', idx, get_register(device, idx), )
	print('set_date', set_date(device), )
	if debug:
		print('get_date', get_date(device), )
	no = get_number_of_records(device)
	print('get_number_of_records', no, )
	for idx in range(no):
		print('get_record', idx, get_record(device, idx), )
	#print('erase_records', erase_records(device), )
	print('logout', logout(device), )

