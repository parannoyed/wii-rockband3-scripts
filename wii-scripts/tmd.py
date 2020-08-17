#!/usr/bin/env python3
from argparse import ArgumentParser
import os
from struct import calcsize

import crypto
import util

class TMD:

	class Header(util.StructBase):
		structure = {
			'signature_type': 4,
			'signature': 256,
			'padding': 60,
			'issuer': 64,
			'version': 1,
			'ca_crl_version': 1,
			'signer_crl_version': 1,
			'is_vwii': 1,
			'system_version': 8,
			'title_id': 8,
			'title_type': 4,
			'group_id': 2,
			'zero': 2,
			'region': 2,
			'ratings': 16,
			'reserved1': 12,
			'ipc_mask': 12,
			'reserved2': 18,
			'access_rights': 4,
			'title_version': 2,
			'number_contents': 2,
			'boot_index': 2,
			'unused': 2
		}


	class Content(util.StructBase):
		structure = {
			'content_id': 4,
			'index': 2,
			'type': 2,
			'size': 8,
			'sha1_hash': 20
		}

		def __init__(self, data=None):
			super().__init_subclass__()
			if isinstance(data, bytes):
				self.set_data(data)

	def add_content(self, content_id, index=None, type='0001', size=None, sha1_hash=None, data=None):
		if data:
			if size is None:
				size = len(data)
				print(size)
			if sha1_hash is None:
				sha1_hash = crypto.get_hash(data)

		if isinstance(content_id, str):
			content_id = util.str2byte(content_id)
		elif isinstance(content_id, int):
			content_id = util.int2byte(content_id, self.Content.structure['content_id'])

		if index is None:
			index = len(self.contents)
		if isinstance(index, int):
			index = util.int2byte(index, self.Content.structure['index'])

		if isinstance(type, str):
			type = util.str2byte(type)
		elif isinstance(type, int):
			type = util.int2byte(type, self.Content.structure['type'])

		if size:
			if isinstance(size, int):
				size = util.int2byte(size, self.Content.structure['size'])
		else:
			size = util.int2byte(0, self.Content.structure['size'])

		if sha1_hash is None:
			sha1_hash = b'\x00' * self.Content.structure['sha1_hash']

		content = self.Content(content_id + index + type + size + sha1_hash)

		i = util.byte2int(index)
		# we have missing entries that need filling before we can be added
		if i > len(self.contents):
			self.add_content('00000000', i - 1)
		# add new
		if i == len(self.contents):
			self.contents.append(content)
		# replace existsing
		elif i < len(self.contents):
			self.contents[i] = content
		return content

	def check_hash(self, index, data):
		return crypto.check_hash(data, self.contents[index].sha1_hash)

	def create(self, data=None):
		if isinstance(data, bytes):
			self.header.set_data(data)
			self.contents = []
			read_start = self.header.get_size()
			read_end = read_start
			for i in range(util.byte2int(self.header.number_contents)):
				content = self.Content()
				read_end += content.get_size()
				content.set_data(data[read_start:read_end])
				self.contents.append(content)
				read_start += content.get_size()
			self.footer = data[read_end:]
		#else:
			# TODO: create new

	def decrypt_content(self, index, decrypted_title_key):
		f = open(os.path.join(os.path.dirname(self.filepath), self.contents[index].content_id.hex()), 'rb')
		data = crypto.decrypt_bin(f.read(), decrypted_title_key, self.contents[index].index)
		# data from decrypt must be trimmed
		return data[:util.byte2int(self.contents[index].size)]

	def info(self):
		print('Title ID: ' + self.header.title_id.hex() + ' (' + self.get_short_title_id() + ')')
		print('Title type: ' + self.header.title_type.hex())
		for i in range(util.byte2int(self.header.number_contents)):
			print('Index: ' + str(util.byte2int(self.contents[i].index)) + ', Content ID: ' + self.contents[i].content_id.hex() + ', Size: ' + str(util.byte2int(self.contents[i].size)) + ' bytes')

	def get_contents_size(self):
		return calcsize(util.pack_format(self.Content.structure)) * len(self.contents)

	def get_number_contents(self):
		return util.int2byte(len(self.contents), self.Header.structure['number_contents'])

	def get_short_title_id(self):
		return self.header.title_id[-4:].decode()

	def get_size(self):
		size = self.header.get_size()
		size += self.get_contents_size()
		size += len(self.footer)
		return size

	def get_packed(self):
		packed = b''
		self.header.number_contents = self.get_number_contents()
		packed += self.header.get_packed()
		for i in range(len(self.contents)):
			packed += self.contents[i].get_packed()
		packed += self.footer
		return packed
	
	def read(self, filepath):
		f = open(filepath, 'rb')
		self.create(f.read())

	def write(self, filepath=None):
		if isinstance(filepath, str):
			self.writepath = filepath
		f = open(self.writepath, 'wb')
		f.write(self.get_packed())

	def __init__(self, filepath=None):
		# declare instance vars
		self.filepath = filepath
		self.header = self.Header()
		self.contents = []
		self.footer = b''

		self.writepath = None

		if isinstance(filepath, str):  # Load file
			try:
				self.read(filepath)
			except FileNotFoundError:
				raise FileNotFoundError('File not found: ' + filepath)

def main(filepath):
	t = TMD(filepath)
	t.info()

if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument('filepath', type=str, help='Path to file')
	arguments = parser.parse_args()
	main(arguments.filepath)
