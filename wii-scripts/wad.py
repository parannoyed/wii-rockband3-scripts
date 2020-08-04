#!/usr/bin/env python3
from argparse import ArgumentParser
import os

import crypto
from tmd import TMD
import util

class DLCWAD:

	class Header(util.StructBase):
		structure = {
				'size': 4,
				'type': 2,
				'version': 2,
				'console_id': 4,
				'savegame_file_count': 4,
				'savegame_file_data_size': 4,
				'tmd_size': 4,
				'content_size': 4,
				'file_size': 4,
				'included_contents': 64,
				'title_id': 8,
				'mac_address': 6,
				'reserved': 2,
				'padding': 16
			}
			
		def __init__(self, data=None):
			self.size = b'\x00\x00\x00\x70'
			self.type = b'\x42\x6b'
			self.version = b'\x00\x01'


	def check_hash(self):
		return self.tmd.check_hash(self.get_content_index(), self.content)

	def create(self, data, title_id, tmd_index, tmd, console_id=None, header=None):
		if header:
			self.header = header
		else:
			self.header = self.Header()
		
		self.set_console_id(console_id)
		self.set_title_id(title_id)
		self.set_included_content(tmd_index)
		self.set_tmd(tmd)
		self.set_content(data)

	def extract(self, base_dir):
		if not os.path.isdir(base_dir):
			os.makedirs(base_dir, exist_ok=True)
		self.tmd.write(os.path.join(base_dir, 'title.tmd'))
		w = open(os.path.join(base_dir, self.tmd.contents[self.get_content_index()].content_id.hex() + '.app'), 'wb')
		w.write(self.content)

	def get_content_index(self):
		content_index = None
		# should only contain a single content index
		for i in range(512):
			if(self.header.included_contents[int(i / 8)] & (1 << (i % 8))):
				content_index = i
		return content_index

	def get_content_size(self):
		return len(self.content) + util.pad_by(len(self.content))

	def get_file_size(self):
		size = self.header.get_size()
		size += self.get_tmd_size() + util.pad_by(self.get_tmd_size())
		size += self.get_content_size()
		return size

	def get_tmd_size(self):
		# tmd cert chain footer isn't included in dlc
		return self.tmd.header.get_size() + self.tmd.get_contents_size()

	def info(self):
		print('Console ID:\t{}'.format(self.header.console_id.hex()))
		print('Title ID:\t{} ({})'.format(self.header.title_id.hex(), self.header.title_id.decode()))
		print('TMD size:\t{} ({} bytes)'.format(self.header.tmd_size.hex(), util.byte2int(self.header.tmd_size)))
		print('Content size:\t{} ({} bytes)'.format(self.header.content_size.hex(), util.byte2int(self.header.content_size)))
		print('File size:\t{} ({} bytes)'.format(self.header.file_size.hex(), util.byte2int(self.header.file_size)))
		print('Content:')
		print('  Title ID:\t{} ({})'.format(self.tmd.header.title_id.hex(), self.tmd.header.title_id.decode()))
		i = self.get_content_index()
		print('  ID:\t\t{}'.format(self.tmd.contents[i].content_id.hex()))
		print('  Index:\t{} ({:03})'.format(self.tmd.contents[i].index.hex(), i))
		print('  Size:\t\t{} ({} bytes)'.format(self.tmd.contents[i].size.hex(), util.byte2int(self.tmd.contents[i].size)))
		print('  SHA1 hash:\t{}'.format(self.tmd.contents[i].sha1_hash.hex()))
		if self.check_hash() == True:
			print('  Hash check:\tPASSED!')
		else:
			print('  Hash check:\tFAILED!')

	def read(self, filepath):
		f = open(filepath, 'rb')
		self.header.set_data(f.read(self.header.get_size()))

		tmd_size = util.byte2int(self.header.tmd_size)
		self.tmd.create(f.read(tmd_size))
		# skip byte align
		f.seek(util.pad_by(tmd_size), 1)

		data = crypto.decrypt_bin(f.read(), self.key, self.tmd.contents[self.get_content_index()].index)
		# trim byte align
		self.set_content(data[:util.byte2int(self.tmd.contents[self.get_content_index()].size)])

	def set_console_id(self, console_id):
		if isinstance(console_id, str):
			console_id = util.str2byte(console_id)
		if not isinstance(console_id, bytes):
			console_id = b'\0' * self.header.structure['console_id']
		self.header.console_id = console_id

	def set_content(self, data):
		self.content = data
		self.header.content_size = util.int2byte(self.get_content_size(), self.header.structure['content_size'])
		self.set_file_size()

	def set_file_size(self):
		self.header.file_size = util.int2byte(self.get_file_size(), self.header.structure['file_size'])

	def set_included_content(self, tmd_index):
		included_contents = bytearray(self.header.included_contents)
		included_contents[int(tmd_index / 8)] = (1 << (tmd_index % 8))
		self.header.included_contents = bytes(included_contents)

	def set_key(self, key):
		if isinstance(key, str):
			key = util.str2byte(key)
		if not isinstance(key, bytes):
			# default
			key = b'\0' * 16		
		self.key = key

	def set_title_id(self, title_id):
		if isinstance(title_id, str):
			if len(title_id) == 4:
				title_id = b'\x00\x01\x00\x00' + util.str2byte(str.encode(title_id).hex())
			elif len(title_id) == 8:
				title_id = b'\x00\x01\x00\x00' + util.str2byte(title_id)
			elif len(title_id) == 16:
				title_id = util.str2byte(title_id)
		if not isinstance(title_id, bytes):
			title_id = b'\0' * self.header.structure['title_id']
		self.header.title_id = title_id

	def set_tmd(self, tmd):
		self.tmd = tmd
		self.header.tmd_size = util.int2byte(self.get_tmd_size(), self.header.structure['tmd_size'])
		self.set_file_size()

	def write(self, filepath):
		f = open(filepath, 'wb')
		f.write(self.header.get_packed())
		# trim cert chain off end
		tmd = self.tmd.get_packed()[:self.get_tmd_size()]
		# byte align to 64 bytes
		tmd += util.pad_zeros(len(tmd))
		f.write(tmd)
		# byte align to 64 bytes
		content = self.content + util.pad_zeros(len(self.content))
		content = crypto.encrypt_bin(content, self.key, self.tmd.contents[self.get_content_index()].index)
		f.write(content)
		f.close()

	def __init__(self, filepath=None, key=None, console_id=None):
		self.header = self.Header()
		self.tmd = TMD()
		self.content = b''

		self.set_console_id(console_id)
		self.set_key(key)

		if isinstance(filepath, str):
			try:
				self.read(filepath)
			except FileNotFoundError:
				raise FileNotFoundError('File not found: ' + filepath)


def main(filepath):
	if os.path.isfile(filepath):
		bin = DLCWAD(filepath)
		bin.info()
	if os.path.isdir(filepath):
		d = os.fsencode(filepath)
		for f in sorted(os.listdir(d)):
			filename = os.fsdecode(f)
			if filename.endswith('.bin'): 
				bin = DLCWAD(os.path.join(filepath, filename))
				bin.info()
				print('')

if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument('filepath', type=str, help='Path to file')
	arguments = parser.parse_args()
	main(arguments.filepath)
