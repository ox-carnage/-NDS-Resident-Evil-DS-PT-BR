#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 02/02/2011

@author: diego.hahn
'''

import struct
import os

from compression import lzss

def Unpack(filename):
	
	root = "Unpacked"	
	if not os.path.isdir(root):
		os.mkdir(root)	
		
	with open(filename, "rb") as f:
		
		entries = struct.unpack('<L', f.read(4))[0] / 8
		f.seek(0,0)
		
		fat = []
		
		for x in range(entries):
			address = struct.unpack('<L', f.read(4))[0]
			size = struct.unpack('<L', f.read(4))[0]
			fat.append((address, size))
			
		for i, par in enumerate(fat):
			output = open(os.path.join(root, "cpac_%s.bin" % i), "wb")
			f.seek(par[0], 0)
			output.write(f.read(par[1]))
			output.close()
			
def UnpackYEK(filename):

	log = open("make.txt", "w")
	
	root = "UnpackedYEK"	
	if not os.path.isdir(root):
		os.mkdir(root)
		
	with open(filename, "rb") as f:
		
		f.seek(0x14, 0)
		base_address = struct.unpack('<L', f.read(4))[0]
		entries = (base_address - 0x20) / 8
		
		f.seek(0x20, 0)
		fat = []
		for x in range(entries):
			address = struct.unpack("<L", f.read(4))[0]
			size = struct.unpack("<L", f.read(4))[0]			
			fat.append((address, size & 0x7FFFFFFF, size & 0x80000000))
			
		for i, par in enumerate(fat):
			output = open(os.path.join(root, "%05d.bin" % i), "wb")		
			address = base_address + par[0]	
			f.seek(address, 0)
			log.write("%08X\n" % par[2])
			output.write(f.read(par[1]))			
			output.close()
		
	log.close()
	
def PackYEK(filename):
	
	log = open("make.txt", "r")
	entries = log.readlines()
	log.close()
	
	with open(filename, "wb") as f:
		# Header fixo ?!?! Generalizar essa PORRA!!
		f.write("\x18\x00\x00\x00")
		f.write("\x02\x00\x00\x00")
		f.write("YEKB")
		f.write("\x18\x00\x00\x00")
		f.write("TADB")
		f.write("\x20\x05\x00\x00")
		f.seek(0x520, 0)
		
		fat = []
		for i, name in enumerate(os.listdir("New UnpackedYEK")):
			p = open(os.path.join("New UnpackedYEK", name), "rb")
			buffer = p.read()
			bit = int(entries[i].strip("\r\n"), 16)
			fat.append((f.tell()-0x520, len(buffer) | bit))
			f.write(buffer)
			p.close()
			
		f.seek(0x20)
		for address, size in fat:
			f.write(struct.pack("<L", address))
			f.write(struct.pack("<L", size))
			
def Pack(filename):

	with open(filename, "wb") as f:
		f.seek(0x20, 0)
		
		fat = []
		for i, name in enumerate(os.listdir("New CPAC")):
			p = open(os.path.join("New CPAC", name), "rb")
			buffer = p.read()
			fat.append((f.tell(), len(buffer)))
			f.write(buffer)
			p.close()			
			
		f.seek(0x0)
		for address, size in fat:
			f.write(struct.pack("<L", address))
			f.write(struct.pack("<L", size))		

			
if __name__ == "__main__":
	# Unpack("cpac_2d.bin")
	# UnpackYEK("Unpacked/cpac_1.bin")
	
	# PackYEK("cpac_1.bin")
	Pack("new_cpac_2d.bin")