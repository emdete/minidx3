#!/usr/bin/env python3
from time import sleep
from serial import Serial

debug = False

def crc(buf):
	crc = 0
	for b in buf:
		crc ^= b
	return crc

def size(buf):
	return [len(buf) & 0xff00 >> 8, len(buf) & 0x00ff, ]

def send_receive(device, buf, size=3):
	buf.insert(0, 2)
	buf.append(13)
	buf = bytes(buf)
	if debug: print(repr(buf))
	device.write(buf)
	buf = device.read(size)
	if debug: print(repr(buf))
	sleep(.3)
	if buf[0] != 2 or buf[-1] != 13:
		raise Exception('Protocol error in result')
	return buf

# L - login
def login(device, pin='0000'):
	pin = [ord(c) for c in pin]
	pin.insert(0, ord('L'))
	return send_receive(device, pin)[1] == ord('A')

# O - logout
def logout(device):
	num = [ord('O'), ]
	return send_receive(device, num)[1] == ord('A')

# P - set password
def set_password(device, pin):
	pin = [ord(c) for c in pin]
	pin.insert(0, ord('P'))
	return send_receive(device, pin)[1] == ord('A')

# B - get register

# C - set register

# F - get product version
def get_product_version(device):
	buf = [ord('F'), ]
	buf = send_receive(device, buf, 100)
	if buf[1] == ord('A'):
		return buf[2:-1].strip(b'\00').split(b'\r')

# S -set date
def set_date(device):
	date = '2021051421056' #TODO
	date = [ord(c) for c in date]
	date.insert(0, ord('S'))
	return send_receive(device, date)[1] == ord('A')

# T - get time and date
def get_date(device):
	buf = [ord('T'), ]
	buf = send_receive(device, buf, 18)
	if buf[1] == ord('A'):
		return buf[2:-1].decode()

# N - get number of records
def get_number_of_records(device):
	num = [ord('N'), ]
	buf = send_receive(device, num, 9)
	if buf[1] == ord('A'):
		crc = buf[-3:-1]
		# TODO check crc
		return int(buf[2:-3].decode(), 16)

# G - get record
def get_record(device, no=0):
	num = [ord('G'), no>>8, no&0xff, ]
	buf = send_receive(device, num, 200)
	if buf[1] == ord('A'):
		return buf[5:-1].decode().split('?')

# E - erase records
def erase_records(device):
	num = [ord('E'), ]
	return send_receive(device, num)[1] == ord('A')

with Serial(port='/dev/ttyUSB0', baudrate=int(19200), ) as device:
	device.rtscts = False
	device.xonxoff = False
	device.timeout = 1
	print('login', login(device), )
	print('get_product_version', get_product_version(device), )
	print('set_date', set_date(device), )
	print('get_date', get_date(device), )
	no = get_number_of_records(device)
	print('get_number_of_records', no, )
	for idx in range(no):
		print('get_record', get_record(device, idx), )
	print('erase_records', erase_records(device), )
	print('logout', logout(device), )

