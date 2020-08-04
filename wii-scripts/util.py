#!/usr/bin/env python3
from collections import namedtuple
from struct import calcsize, pack, unpack

class StructBase:
	structure = {}

	def get_format(self):
		return pack_format(self.structure)

	def get_items(self):
		return (getattr(self, k) for k, v in self.structure.items())

	def get_packed(self):
		return pack(self.get_format(), *self.get_items())

	def get_size(self):
		return calcsize(self.get_format())

	def set_data(self, data):
		Structure = namedtuple('Structure', ' '.join(self.structure.keys()))
		unpacked = Structure._make(unpack(self.get_format(), data[:self.get_size()]))
		for key in self.structure:
			setattr(self, key, getattr(unpacked, key))

	def __init_subclass__(cls, data=None):
		super().__init_subclass__()
		for k in cls.structure:
			setattr(cls, k, b'\x00' * cls.structure[k])
		if isinstance(data, bytes):
			cls.set_data(data)


def byte2int(val):
	return int.from_bytes(val, 'big')

def get_hex_str(val, val_len=1):
	return '{0:0{1}x}'.format(val, val_len*2)

def get_pretty_hex(val, val_len=1):
	return '0x' + get_hex_str(val, val_len)

def int2byte(val, val_len=1):
	return bytes(bytearray.fromhex(get_hex_str(val, val_len)))

def pad_by(val, size=64):
	by = val % size
	if by:
		by = size - by
	return by

def pad_zeros(val, size=64):
	rval = b''
	for i in range(pad_by(val, size)):
		rval += b'\00'
	return rval

def pack_format(format_dict):
	rval = '>'
	for k, v in format_dict.items():
		rval += str(v) + 's'
	return rval

def str2byte(val):
	return bytes(bytearray.fromhex(val))
