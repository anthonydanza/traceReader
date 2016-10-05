# A logger for lens/frame traces from the National Optronics 4Ti.
# Connect an FTDI cable to COM1 on the 4Ti, plug into your computer,
# and run this server on the corresponding serial port.
#
# OMA support recommended but not included.
# 
# Tom Hobson 2016

import serial
import time
import sys
import os
import argparse
import json

#TODO
class OMAPacket(): 
	def __init__(self):
		return

#TODO
def parse_oma(self, packet):
	return

class GCPacket():

	def __init__(self, job=0, AB=[0,0], DBL=0, CIR=0, data=[]):
		self.job = job
		self.AB = AB
		self.DBL = DBL
		self.CIR = CIR
		self.data = data

	def save(self, save_dir):
		timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
		filename = "GC_Trace_Record " + timestamp + ".json"
		filepath = os.path.join(save_dir,filename)
		try:
			f = open(filepath, "wb")
			content = json.dumps(self, default=jdefault)
			f.write(content)
			f.close()
			print filepath + " saved."
		except IOError:
			print "Error opening file " + filepath

def jdefault(o):
    return o.__dict__

def parse_gc(packet):
	data = packet.split('\r\n')

	if data[len(data)-1] != '\x04':
		print "ERROR: G-C packet is malformed."
		return ''
	else:
		gc = GCPacket()
		gc.job = gcfield_to_array(data[0],' ')
		gc.AB = gcfield_to_array(data[1],' ')
		gc.DBL = gcfield_to_array(data[2],' ')
		gc.CIR = gcfield_to_array(data[3],' ')
		gc.data = map(float, data[4:len(data)-1])
		return gc

def gcfield_to_array(string, delimiter):
	delimited = string.split(delimiter)
	print delimited
	return [float(i) for i in delimited[1:len(delimited)]]

class traceServer():

	def __init__(self, serial_connection, save_dir):
		self.serial = serial_connection
		self.save_dir = save_dir

	def listen(self):
		print "Listening for trace data on port " + self.serial.port + "\n"
		buff = []
		while 1:
			byte = ser.read(1)
			if len(byte) == 0:
				if len(buff) > 0:
					buff = ''.join(buff)
					print buff
					self.parse_packet(buff)
				buff = []
			else:
				print "Receiving data...\r",
				buff.append(byte)

	def parse_packet(self, packet):
		if packet[0] == '\x1c':
			data = parse_oma(packet)
		elif ''.join(packet[0:3]) == "JOB":
			data = parse_gc(packet)
			if data:
				data.save(self.save_dir)
		else:
			print "ERROR: unknown packet type received: "
			self.serial.resetInputBuffer()
			self.serial.resetOutputBuffer()
			return

if __name__ == '__main__':

	arg_parser = argparse.ArgumentParser(description = "A simple server for saving G-C formatted lens/frame traces.")
	arg_parser.add_argument("port", help="serial port interface to tracer. usually something like /dev/tty.usbserial-A6Z49Y8X on *nix systems. windows people, uh, figure it out.")
	arg_parser.add_argument("--save", help="directory in which trace records will be saved. can be a local directory or a mounted network drive using SMB or similar.", default=".")
	args = arg_parser.parse_args()

	if not os.path.isdir(args.save):
		print "Specified save directory does not exist. Creating new directory at " + args.save
		os.makedirs(args.save)

	print "\nG-C trace data logger.\n"

	ser = serial.Serial(args.port, 9600, timeout=0.5)
	server = traceServer(ser, args.save)
	server.listen()
