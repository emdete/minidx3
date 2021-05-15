#!/usr/bin/env python3
' module to drive a MiniDX3 '
from time import sleep
from datetime import datetime
from serial import Serial

DEBUG = False

class MiniDX3(Serial): # pylint: disable=too-many-ancestors
	' Class MiniDX3 to open the serial device to the MiniDX3 and talk to it '

	def __init__(self, filename, pin='0000'):
		super().__init__(port=filename, baudrate=19200, )
		self.rtscts = False
		self.xonxoff = False
		self.timeout = 1
		self.login(pin)

	@staticmethod
	def __check_crc(buf):
		crc = 0
		for b in buf[2:-3]:
			crc ^= b
		# TODO check crc
		# print('---', int(buf[-3:-1].decode(), 16), crc, )
		return buf[0:-2]

	@staticmethod
	def __size(buf):
		return [len(buf) & 0xff00 >> 8, len(buf) & 0x00ff, ]

	def send_receive(self, buf, size=5):
		buf.insert(0, 2)
		buf.append(13)
		buf = bytes(buf)
		if DEBUG: print(repr(buf))
		self.write(buf)
		if DEBUG: sleep(.3)
		buf = self.read(size)
		if DEBUG: print(repr(buf))
		if not buf or buf[0] != 2 or buf[-1] != 13:
			raise Exception('Protocol error in result "{}"'.format(buf))
		if buf[1] != ord('A'):
			raise Exception('Error {}'.format(int(buf[2:4].decode(), 16)))
		buf = buf[2:-1]
		return buf

	# L - login
	def login(self, pin='0000'):
		buf = [ord(c) for c in pin]
		buf.insert(0, ord('L'))
		return self.send_receive(buf)

	# O - logout
	def logout(self):
		num = [ord('O'), ]
		return self.send_receive(num)

	# P - set password
	def set_password(self, pin):
		buf = [ord(c) for c in pin]
		buf.insert(0, ord('P'))
		return self.send_receive(buf)

	# B - get register
	def get_register(self, no):
		no = [ord(c) for c in '{:02x}'.format(no)]
		#no = [no >> 8, no & 0xff, ]
		buf = [ord('B'), ] + no
		buf = self.send_receive(buf, 7)
		buf = MiniDX3.__check_crc(buf)
		return int(buf.decode(), 16)

	# C - set register
	def set_register(self, no, value):
		no = [ord(c) for c in '{:02x}'.format(no)]
		buf = [ord('C'), ]
		# TODO implement

	# F - get product version
	def get_product_version(self):
		buf = [ord('F'), ]
		buf = self.send_receive(buf, 100)
		buf = MiniDX3.__check_crc(buf) # unclean binary zeros, unclear =, crc?
		return buf.strip(b'\00').decode().split('\r')

	# S - set date
	def set_date(self):
		date = datetime.now().strftime('%Y%m%d%H%M%u')
		buf = [ord(c) for c in date]
		buf.insert(0, ord('S'))
		return self.send_receive(buf)

	# T - get time and date
	def get_date(self):
		buf = [ord('T'), ]
		buf = self.send_receive(buf, 18)
		buf = MiniDX3.__check_crc(buf) # crc included?
		return buf.decode()

	# N - get number of records
	def get_number_of_records(self):
		buf = [ord('N'), ]
		buf = self.send_receive(buf, 9)
		buf = MiniDX3.__check_crc(buf)
		return int(buf.decode(), 16)

	# G - get record
	def get_record(self, no):
		no = [ord(c) for c in '{:04x}'.format(no)]
		#no = [no >> 8, no & 0xff, ]
		buf = [ord('G'), ] + no
		buf = self.send_receive(buf, 200)
		return buf.decode() # .split('?')

	# E - erase records
	def erase_records(self):
		buf = [ord('E'), ]
		return self.send_receive(buf)

if __name__ == '__main__':
	with MiniDX3('/dev/ttyUSB0', '0000') as device:
		if DEBUG:
			print('get_product_version', device.get_product_version(), )
		if DEBUG:
			for idx in range(256):
				print('get_register', idx, device.get_register(idx), )
		print('set_date', device.set_date(), )
		if DEBUG:
			print('get_date', device.get_date(), )
		no = device.get_number_of_records()
		print('get_number_of_records', no, )
		for idx in range(no):
			print('get_record', idx, device.get_record(idx), )
		print('erase_records', device.erase_records(), )
		print('logout', device.logout(), )

