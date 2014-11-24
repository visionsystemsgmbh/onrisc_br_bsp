#!/usr/bin/python

import sys
import time
import getopt
import struct
import os.path
import fcntl
from datetime import datetime, date, time
from struct import *
from types import *

# error codes
ERR_NONE	= 0
ERR_IO		= 1
ERR_PARSING	= 5

# port type
TYPE_UNKNOWN		= 0
TYPE_RS232		= 1
TYPE_RS422		= 2
TYPE_RS422_TERM		= 3
TYPE_RS485_FD		= 4
TYPE_RS485_FD_TERM	= 5
TYPE_RS485_HD		= 6
TYPE_RS485_HD_TERM	= 7
TYPE_LOOPBACK		= 8
TYPE_DIP		= 9

# OTG modes
MODE_NONE	= 0
MODE_OTG	= 1
MODE_CFAST	= 2
MODE_TRI	= 3

# machine
MODEL_VS860		= 0
MODEL_ALEKTO2		= 1
MODEL_BALIOS_IR_5221	= 2
MODEL_NETCON3		= 3

# GPIO direction
DIR_IN		= 'in'
DIR_OUT		= 'out'

# group 0
GR0_CTRL_IN	= 192
GR0_CTRL_OUT	= 193
GR0_FIRST_PIN	= 200
GR0_LAST_PIN	= 203

# group 1
GR1_CTRL_IN	= 196
GR1_CTRL_OUT	= 197
GR1_FIRST_PIN	= 204
GR1_LAST_PIN	= 205

# group 2
GR2_CTRL_IN	= 198
GR2_CTRL_OUT	= 199
GR2_FIRST_PIN	= 206
GR2_LAST_PIN	= 207

# EEPROM
ALEKTO2_EEPROM	= '/sys/bus/i2c/devices/1-0050/eeprom'
VS860_EEPROM	= '/sys/bus/i2c/devices/2-0054/eeprom'
HWSTRUCT_FMT	= '<III11sH6s6s6s'

# sysfs
SYSFS_EXPORT	= "/sys/class/gpio/export"

# RTC cmds
RTC_NONE	= 0
RTC_SYSTOHC	= 1
RTC_READ	= 2

# RTC wrapper defines
RTC_MASK	= 'iiiiiiiii'
RTC_RD_TIME	= -2145095671
RTC_SET_TIME	= 1076129802

def usage():
	print("OnRISC Tool usage:")
	print("onrisctool [-o cfast|otg|tri] [-p 1|2]")
	print("[-t rs232|rs422|rs422-term|rs485-fd|rs485-fd-term|rs485-hd|rs485-hd-term|dip|loop]")
	print("[-m 0x00..0xff] [-d 0x00..0xff] [-c in|out] [-g 0|1|2]")
	print("[--systohc | --readrtc]")
	print("[--setlanmacs]")

def formatMAC( mac_str ):
	return ''.join( [ "%02X:" % ord( x ) for x in mac_str ] ).strip(':')

def serDriverModeGPIO(pin, mask):
	pin = serial_mode_first_pin + 4 * port_number
	for i in range(4):
		try:
			f = open("/sys/class/gpio/gpio%d/value" % (pin + i), 'w')
		except IOError:
			print("Cannot open /sys/class/gpio/gpio%d/value" % (pin + i))
			return ERR_IO

		f.write(mask[i])
		f.close()

def getDriverMode(port_number):
	pin = serial_mode_first_pin + 4 * port_number
	mask = bytearray(b"0000")
	mode = TYPE_LOOPBACK

	for i in range(4):
		try:
			f = open("/sys/class/gpio/gpio%d/value" % (pin + i), 'r')
		except IOError:
			print("Cannot open /sys/class/gpio/gpio%d/value" % (pin + i))
			return ERR_IO, mode

		mask[i] = f.read(1)
		f.close()

	if mask == '0000':
		mode = TYPE_LOOPBACK
	elif mask == '1000':
		mode = TYPE_RS232
	elif mask == '1110':
		mode = TYPE_RS422
	elif mask == '1111':
		mode = TYPE_RS422_TERM
	elif mask == '1100':
		mode = TYPE_RS485_FD
	elif mask == '1101':
		mode = TYPE_RS485_FD_TERM
	elif mask == '0100':
		mode = TYPE_RS485_HD
	elif mask == '0101':
		mode = TYPE_RS485_HD_TERM

	return ERR_NONE, mode



def setDriverMode(port_number, driver_mode):
	pin = serial_mode_first_pin + 4 * port_number

	if driver_mode == TYPE_LOOPBACK:
		serDriverModeGPIO(pin, '0000')
	elif driver_mode == TYPE_RS232:
		serDriverModeGPIO(pin, '1000')
	elif driver_mode == TYPE_RS422:
		serDriverModeGPIO(pin, '1110')
	elif driver_mode == TYPE_RS422_TERM:
		serDriverModeGPIO(pin, '1111')
	elif driver_mode == TYPE_RS485_FD:
		serDriverModeGPIO(pin, '1100')
	elif driver_mode == TYPE_RS485_FD_TERM:
		serDriverModeGPIO(pin, '1101')
	elif driver_mode == TYPE_RS485_HD:
		serDriverModeGPIO(pin, '0100')
	elif driver_mode == TYPE_RS485_HD_TERM:
		serDriverModeGPIO(pin, '0101')

def showSerialPortState():

	for i in range(0,2):
		rc, gpio_dir = getGPIODirection(serial_mode_first_pin + i * 4)
		if gpio_dir == DIR_IN:
			print("Port %d: mode control: DIP-switch" % (i + 1))
		else:
			print("Port %d: mode control: GPIO" % (i + 1))

		rc, mode = getDriverMode(i)
		if mode == TYPE_LOOPBACK:
			print("Port %d: mode: loopback" % (i + 1))
		elif mode == TYPE_RS232:
			print("Port %d: mode: rs232" % (i + 1))
		elif mode == TYPE_RS422:
			print("Port %d: mode: rs422" % (i + 1))
		elif mode == TYPE_RS422_TERM:
			print("Port %d: mode: rs422-terminated" % (i + 1))
		elif mode == TYPE_RS485_FD:
			print("Port %d: mode: rs485-full-duplex" % (i + 1))
		elif mode == TYPE_RS485_FD_TERM:
			print("Port %d: mode: rs485-full-duplex-terminated" % (i + 1))
		elif mode == TYPE_RS485_HD:
			print("Port %d: mode: rs485-half-duplex" % (i + 1))
		elif mode == TYPE_RS485_HD_TERM:
			print("Port %d: mode: rs485-half-duplex-terminated" % (i + 1))

def readEeprom():
	if model == MODEL_VS860:
		eeprom_dev = VS860_EEPROM
	else:
		eeprom_dev = ALEKTO2_EEPROM
	try:
		f = open(eeprom_dev, 'r')
	except IOError:
		print("Cannot open EEPROM")
		return ERR_IO

	try:
		buf = f.read(calcsize(HWSTRUCT_FMT))
	except IOError:
		print("Cannot read EEPROM")
		return ERR_IO

	f.close()

	# unpack hwparam struct
	magic, hwrev, sernum, pr_date, sys_id, mac1, mac2, mac3 = struct.unpack(HWSTRUCT_FMT, buf)
	print('magic: 0x%0.8X' % (magic))
	print('hw rev: %d.%d' % (hwrev >> 16, hwrev & 0xff))
	print('SerNum: %d' % (sernum))
	print('Prod date: %s' % (pr_date))
	print('SysId: %d' % (sys_id))
	print('MAC1: %s' % (formatMAC(mac1)))
	print('MAC2: %s' % (formatMAC(mac2)))
	print('MAC3: %s' % (formatMAC(mac3)))


def parseOptions(opts, args):
	# assign default values
	ser_type = TYPE_RS232
	port = -1
	otg_mode = MODE_NONE
	gpio_mask = 0x100
	gpio_data = 0x100
	gpio_ctrl = DIR_IN
	gpio_group = -1
	rtc_cmd = RTC_NONE
	set_lan_macs = 0


	# parse options
	for o, a in opts:
		if o == "-p":
			port = int(a) - 1
		elif o == "-m":
			gpio_mask = int(a, 16)
		elif o == "-d":
			gpio_data = int(a, 16)
		elif o == "-c":
			gpio_ctrl = a
		elif o == "-g":
			gpio_group = int(a)
		elif o == "--systohc":
			rtc_cmd = RTC_SYSTOHC
		elif o == "--readrtc":
			rtc_cmd = RTC_READ
		elif o == "--setlanmacs":
			set_lan_macs = 1
		elif o == "-o":
			if a == "otg":
				otg_mode = MODE_OTG
			elif a == "cfast":
				otg_mode = MODE_CFAST
			elif a == "tri":
				otg_mode = MODE_TRI
			else:
				print("Invalid OTG mode")
				sys.exit(ERR_PARSING)
		elif o == "-t":
			if a == "rs232":
				ser_type = TYPE_RS232
			elif a == "rs422":
				ser_type = TYPE_RS422
			elif a == "rs422-term":
				ser_type = TYPE_RS422_TERM
			elif a == "rs485-fd":
				ser_type = TYPE_RS485_FD
			elif a == "rs485-fd-term":
				ser_type = TYPE_RS485_FD_TERM
			elif a == "rs485-hd":
				ser_type = TYPE_RS485_HD
			elif a == "rs485-hd-term":
				ser_type = TYPE_RS485_HD_TERM
			elif a == "dip":
				ser_type = TYPE_DIP
			elif a == "loop":
				ser_type = TYPE_LOOPBACK
			else:
				print("Invalid serial type")
				sys.exit(ERR_PARSING)

	return ser_type, port, otg_mode, gpio_mask, gpio_ctrl, gpio_data, gpio_group, rtc_cmd, set_lan_macs

def setGPIOValue(pin, val):
	try:
		f = open("/sys/class/gpio/gpio%d/value" % (pin), 'w')
	except IOError:
		print("Cannot open /sys/class/gpio/gpio%d/value" % (pin))
		return ERR_IO

	f.write("%d" % val)
	f.close()

def getGPIOValue(pin):
	val = 0

	try:
		f = open("/sys/class/gpio/gpio%d/value" % (pin), 'r')
	except IOError:
		print("Cannot open /sys/class/gpio/gpio%d/value" % (pin))
		return ERR_IO, val

	val = int(f.read(1))
	f.close()

	return ERR_NONE, val

def getGPIODirection(pin):
	val = DIR_IN

	try:
		f = open("/sys/class/gpio/gpio%d/direction" % (pin), 'r')
	except IOError:
		print("Cannot open /sys/class/gpio/gpio%d/direction" % (pin))
		return ERR_IO, val

	buf = f.read(10)
	if buf.find('out') != -1:
		val = DIR_OUT

	f.close()

	return ERR_NONE, val

def serDriverModeGPIO(pin, mask):
	for i in range(4):
		try:
			f = open("/sys/class/gpio/gpio%d/value" % (pin + i), 'w')
		except IOError:
			print("Cannot open /sys/class/gpio/gpio%d/value" % (pin + i))
			return ERR_IO

		f.write(mask[i])
		f.close()

def exportGPIO(pin):
	if not os.path.exists("/sys/class/gpio/gpio%d" % pin):
		try:
			f = open(SYSFS_EXPORT, 'w')
		except IOError:
			print("Cannot open /sys/class/gpio/export")
			return ERR_IO


		f.write('%d' % pin)
		f.close()


def exportAndSetDirection(pin, direction):
	rc = ERR_NONE
	if not os.path.exists("/sys/class/gpio/gpio%d" % pin):
		try:
			f = open(SYSFS_EXPORT, 'w')
		except IOError:
			print("Cannot open /sys/class/gpio/export")
			return ERR_IO


		f.write('%d' % pin)
		f.close()

	rc, gpio_dir = getGPIODirection(pin)

	if gpio_dir != direction:
		try:
			f = open("/sys/class/gpio/gpio%d/direction" % pin, 'w')
		except IOError:
			print("Cannot open /sys/class/gpio/gpio%d/direction" % pin)
			return ERR_IO

		f.write(direction)
		f.close()

def handleOtgMode(model, otg_mode):
	if otg_mode == MODE_OTG:
		exportAndSetDirection(otg_pin, DIR_OUT)
		setGPIOValue(otg_pin, 0)
		print('USB0 in OTG mode')
	elif otg_mode == MODE_CFAST:
		exportAndSetDirection(otg_pin, DIR_OUT)
		setGPIOValue(otg_pin, 1)
		print('USB0 in CFast mode')
	elif otg_mode == MODE_TRI:
		exportAndSetDirection(otg_pin, DIR_IN)
		print('USB0 in automatic mode')

def handleSerialMode(serial_mode_first_pin, port, ser_type):
	pin = serial_mode_first_pin + 4 * port
	gpio_dir = DIR_OUT

	if port == -1:
		return

	if ser_type == TYPE_DIP:
		gpio_dir = DIR_IN

	for i in range(pin, pin + 4):
		exportAndSetDirection(i, gpio_dir)

	setDriverMode(port, ser_type)

def changeDirection(pin, direction):

	ctrl_in = GR0_CTRL_IN
	ctrl_out = GR0_CTRL_OUT
	first_pin = GR0_FIRST_PIN
	last_pin = GR0_LAST_PIN

	if pin >= GR1_FIRST_PIN and pin <= GR1_LAST_PIN:
		ctrl_in = GR1_CTRL_IN
		ctrl_out = GR1_CTRL_OUT
		first_pin = GR1_FIRST_PIN
		last_pin = GR1_LAST_PIN

	elif pin >= GR2_FIRST_PIN and pin <= GR2_LAST_PIN:
		ctrl_in = GR2_CTRL_IN
		ctrl_out = GR2_CTRL_OUT
		first_pin = GR2_FIRST_PIN
		last_pin = GR2_LAST_PIN

	# set group data pins to input
	for i in range(first_pin,last_pin + 1):
		exportAndSetDirection(i, DIR_IN)

	# disable drivers
	for i in range(ctrl_in,ctrl_out + 1):
		setGPIOValue(i, 1)

	# set final data bits direction and enable drivers
	if direction == DIR_IN:
		setGPIOValue(ctrl_in, 0)
	else:
		setGPIOValue(ctrl_out, 0)
		# change data bits to output
		for i in range(first_pin,last_pin + 1):
			exportAndSetDirection(i, DIR_OUT)

def handleGPIO(gpio_mask, gpio_ctrl, gpio_data, gpio_group):
	if model == MODEL_ALEKTO2:
		# assertions
		assert gpio_group >= -1 and gpio_group <= 2, "wrong group number"
		assert type(gpio_ctrl) is StringType, "gpio_ctrl is not a string"

		# set group direction
		if gpio_group == 0:
			changeDirection(200, gpio_ctrl)
		elif gpio_group == 1:
			changeDirection(204, gpio_ctrl)
		elif gpio_group == 2:
			changeDirection(206, gpio_ctrl)

		if gpio_mask != 0x100 and gpio_data != 0x100:
			for i in range(8):
				if (gpio_mask >> i) & 0x01 == 1:
					gpio_val = (gpio_data >> i) & 0x01
					setGPIOValue(i + 200, gpio_val)
					print("GPIO %d data: %d" % (i, gpio_val))
	elif model == MODEL_NETCON3:
		if gpio_mask != 0x100 and gpio_data != 0x100:
			for i in range(8):
				if (gpio_mask >> i) & 0x01 == 1:
					gpio_val = (gpio_data >> i) & 0x01
					setGPIOValue(i + 504, gpio_val)
					print("GPIO %d data: %d" % (i, gpio_val))
	elif model == MODEL_BALIOS_IR_5221:
		if gpio_mask != 0x100 and gpio_data != 0x100:
			for i in range(4):
				if (gpio_mask >> i) & 0x01 == 1:
					gpio_val = (gpio_data >> i) & 0x01
					setGPIOValue(i + 500, gpio_val)
					print("GPIO %d data: %d" % (i, gpio_val))


def unpack_data(rtc_data):
	data = struct.unpack('iiiiiiiii', rtc_data)
	real_data = datetime(data[5] + 1900, data[4] + 1, data[3],
		data[2], data[1], data[0])

	return real_data

def pack_data(data):
	return struct.pack('iiiiiiiii',
		data.second, data.minute, data.hour,
		data.day, data.month - 1, data.year - 1900,
		0, 0, 0);

def handleRTC(rtc_cmd):
	if rtc_cmd == RTC_NONE:
		return

	# open RTC
	try:
		rtc = open("/dev/rtc0", "r")
	except:
		print('Failed to open /dev/rtc0')
		return

	# read RTC
	if rtc_cmd == RTC_READ:
		a=struct.pack(RTC_MASK, 0,0,0,0,0,0,0,0,0)
		try:
			rtc_data = fcntl.ioctl(rtc, RTC_RD_TIME, a)
		except IOError:
			rtc.close()
			print("Failed to read RTC")
			return

		real_data = unpack_data(rtc_data)
		print("RTC read: %s" % real_data)

	# get current date/time and write it to RTC
	elif rtc_cmd == RTC_SYSTOHC:
		rtc_data = datetime.now()

		try:
			rtc_data = fcntl.ioctl(rtc, RTC_SET_TIME, pack_data(rtc_data))
		except IOError:
			rtc.close()
			print("Failed to set RTC")
			return

	rtc.close()

def handleDIPs():
	print('\nDIPs\n')

	exportAndSetDirection(44, DIR_IN)
	exportAndSetDirection(45, DIR_IN)
	exportAndSetDirection(46, DIR_IN)
	exportAndSetDirection(47, DIR_IN)

	for i in range(4):
		rc, val = getGPIOValue(i + 44)
		if rc != ERR_NONE:
			return rc

		if val == 0:
			print('DIP ' + repr(i+1) + ': on')
		else:
			print('DIP ' + repr(i+1) + ': off')

def handleMACs(set_lan_macs):
	if not set_lan_macs:
		return

	if model == MODEL_VS860:
		eeprom_dev = VS860_EEPROM
	else:
		eeprom_dev = ALEKTO2_EEPROM
	try:
		f = open(eeprom_dev, 'r')
	except IOError:
		print("Cannot open EEPROM")
		return ERR_IO

	buf = f.read(calcsize(HWSTRUCT_FMT))
	f.close()

	# unpack hwparam struct
	magic, hwrev, sernum, pr_date, sys_id, mac1, mac2, mac3 = struct.unpack(HWSTRUCT_FMT, buf)

	if model == MODEL_VS860:
		os.system("ifconfig eth0 hw ether %s" % formatMAC(mac1))
		os.system("ifconfig usb0 hw ether %s" % formatMAC(mac2))
	else:
		os.system("ifconfig eth0 hw ether %s" % formatMAC(mac1))
		os.system("ifconfig eth1 hw ether %s" % formatMAC(mac2))

def showGPIOStatusBaliosir5221():
	print('GPIO status\n')
	for i in range(4):
		rc, val = getGPIOValue(i + 496)
		if rc != ERR_NONE:
			return rc

		print('GPIO INPUT ' + repr(i) + ': ' + repr(val))

	for i in range(4):
		rc, val = getGPIOValue(i + 500)
		if rc != ERR_NONE:
			return rc

		print('GPIO OUTPUT ' + repr(i) + ': ' + repr(val))

def showGPIOStatusNetCon3():
	print('GPIO status\n')
	for i in range(8):
		rc, val = getGPIOValue(i + 496)
		if rc != ERR_NONE:
			return rc

		print('GPIO INPUT ' + repr(i) + ': ' + repr(val))

	for i in range(8):
		rc, val = getGPIOValue(i + 504)
		if rc != ERR_NONE:
			return rc

		print('GPIO OUTPUT ' + repr(i) + ': ' + repr(val))

def showGPIOStatus():
	rc, val = getGPIOValue(GR0_CTRL_IN)
	if rc != ERR_NONE:
		return rc

	if val == 0:
		changeDirection(200, gpio_ctrl)
		print("Group 0-3: in")
	else:
		print("Group 0-3: out")

	rc, val = getGPIOValue(GR1_CTRL_IN)
	if rc != ERR_NONE:
		return rc

	if val == 0:
		changeDirection(204, gpio_ctrl)
		print("Group 4-5: in")
	else:
		print("Group 4-5: out")

	rc, val = getGPIOValue(GR2_CTRL_IN)
	if rc != ERR_NONE:
		return rc

	if val == 0:
		changeDirection(206, gpio_ctrl)
		print("Group 6-7: in")
	else:
		print("Group 6-7: out")

def showSystemStatus():
	rc = ERR_NONE
	gpio_val = 0
	gpio_dir = DIR_IN

	print('OnRISC Tool 1.0.0\n')
	print('System Status\n')

	# show hardware info from EEPROM
	readEeprom()

	if model != MODEL_BALIOS_IR_5221 and model != MODEL_NETCON3:
		print('\n')
		rc, gpio_val = getGPIOValue(otg_pin)
		if rc != ERR_NONE:
			return rc

		rc, gpio_dir = getGPIODirection(otg_pin)
		if rc != ERR_NONE:
			return rc

		if gpio_dir == DIR_IN:
			if gpio_val == 0:
				print("OTG automatic mode: OTG")
			else:
				print("OTG automatic mode: CFast")
		else:
			if gpio_val == 0:
				print("OTG force mode: OTG")
			else:
				print("OTG force mode: CFast")

		print('\n')

	if model != MODEL_NETCON3:
		showSerialPortState()

	print('\n')

	if model == MODEL_ALEKTO2:
		showGPIOStatus()
	elif model == MODEL_NETCON3:
		showGPIOStatusNetCon3()
	elif model == MODEL_BALIOS_IR_5221:
		showGPIOStatusBaliosir5221()

	if model == MODEL_NETCON3:
		handleDIPs()

	return rc

def getModel():

	# init variables
	model = MODEL_VS860
	otg_pin = 154
	serial_mode_first_pin = 200

	# find the model
	with open('/proc/cpuinfo', 'r') as f:
		for line in f:
			if line.find('am335xevm') != -1 or line.find('AM33X') != -1:
				model = MODEL_ALEKTO2
				otg_pin = 67
				serial_mode_first_pin = 208
				try:
					with open('/proc/device-tree/model','r') as f_model:
						for line in f_model:
							if line.find('Balios') != -1:
								model = MODEL_BALIOS_IR_5221
								serial_mode_first_pin = 504
							elif line.find('NetCON 3') != -1:
								model = MODEL_NETCON3
				except:
					pass

	return model, otg_pin, serial_mode_first_pin

#main routine

model, otg_pin, serial_mode_first_pin = getModel()

# export GPIOs
if model != MODEL_BALIOS_IR_5221 and model != MODEL_NETCON3:
	exportGPIO(otg_pin)

if model == MODEL_ALEKTO2:
	exportAndSetDirection(GR0_CTRL_IN, DIR_OUT)
	exportAndSetDirection(GR0_CTRL_OUT, DIR_OUT)
	exportAndSetDirection(GR1_CTRL_IN, DIR_OUT)
	exportAndSetDirection(GR1_CTRL_OUT, DIR_OUT)
	exportAndSetDirection(GR2_CTRL_IN, DIR_OUT)
	exportAndSetDirection(GR2_CTRL_OUT, DIR_OUT)

	for i in range(200,208):
		exportGPIO(i)

elif model == MODEL_NETCON3:
	for i in range(496,504):
		exportAndSetDirection(i, DIR_IN)
		exportAndSetDirection(i + 8, DIR_OUT)
elif model == MODEL_BALIOS_IR_5221:
	for i in range(496,500):
		exportAndSetDirection(i, DIR_IN)
		exportAndSetDirection(i + 4, DIR_OUT)

# parse command line arguments
if model != MODEL_NETCON3:
	for i in range(serial_mode_first_pin, serial_mode_first_pin + 8):
		exportGPIO(i)

try:
	opts, args = getopt.getopt(sys.argv[1:], "o:t:p:m:c:d:g:", ["systohc", "hctosys", "readrtc", "setlanmacs"])
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err) # will print something like "option -a not recognized"
	usage()
	sys.exit(ERR_PARSING)

ser_type, port, otg_mode, gpio_mask, gpio_ctrl, gpio_data, gpio_group, rtc_cmd, set_lan_macs = parseOptions(opts, args)

if len(sys.argv) == 1:
	showSystemStatus()
	sys.exit(0)

handleOtgMode(model, otg_mode)

handleSerialMode(serial_mode_first_pin, port, ser_type)

handleGPIO(gpio_mask, gpio_ctrl, gpio_data, gpio_group)

handleRTC(rtc_cmd)

handleMACs(set_lan_macs)

