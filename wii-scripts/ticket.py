#!/usr/bin/env python3
from argparse import ArgumentParser

import crypto
import util

class Ticket(util.StructBase):
	structure = {
			'signature_type': 4,
			'signature': 256,
			'padding1': 60,
			'issuer': 64,
			'ecdh_data': 60,
			'padding2': 3,
			'title_key': 16,
			'unknown1': 1,
			'ticket_id': 8,
			'console_id': 4,
			'title_id': 8,
			'unknown2': 2,
			'title_version': 2,
			'permitted_titles': 4,
			'permit_mask': 4,
			'title_export': 1,
			'common_key_index': 1,
			'is_vc': 48,
			'content_access_permissions': 64,
			'padding3': 2,
			'is_time_limit1': 4,
			'time_limit1': 4,
			'is_time_limit2': 4,
			'time_limit2': 4,
			'is_time_limit3': 4,
			'time_limit3': 4,
			'is_time_limit4': 4,
			'time_limit4': 4,
			'is_time_limit5': 4,
			'time_limit5': 4,
			'is_time_limit6': 4,
			'time_limit6': 4,
			'is_time_limit7': 4,
			'time_limit7': 4,
			'is_time_limit8': 4,
			'time_limit8': 4
		}

	def create(self, data=None, title_key=None, console_id=None, title_id=None):
		if isinstance(data, bytes):
			self.set_data(data)
		else:
			# reset
			for k in self.structure:
				setattr(self, k, b'\x00' * self.structure[k])
			# defaults
			self.signature_type = b'\x00\x01\x00\x01'
			self.set_issuer('Root-CA00000001-XS00000003')
			# self.ticket_id?
			self.unknown2 = b'\xFF' * self.structure['unknown2']
			self.permit_mask = b'\xFF' * self.structure['permit_mask']
			self.is_vc = (b'\x00' * (self.structure['is_vc'] - 1)) + b'\x01'
			self.content_access_permissions = b'\xFF' * self.structure['content_access_permissions']

		if title_key:
			self.title_key = title_key
		if console_id:
			self.set_console_id(console_id)
		if title_id:
			self.set_title_id(title_id)

	def decrypt_title_key(self):
		return crypto.decrypt_title_key(self.title_id, self.title_key)

	def get_short_title_id(self):
		return self.ticket.title_id[-4:].decode()

	def info(self):
		print('Signature: ' + self.signature.hex())
		print('Issuer: ' + self.issuer.decode('utf-8'))
		print('Console ID: ' + self.console_id.hex())
		print('Title ID: ' + self.title_id.hex() + ' (' + self.get_short_title_id() + ')')
		print('Encrypted Title Key: ' + self.title_key.hex())
		print('Decrypted Title Key: ' + self.decrypt_title_key().hex())

	def read(self, filepath):
		f = open(filepath, 'rb')
		self.create(f.read())

	def set_console_id(self, console_id):
		if isinstance(console_id, str):
			console_id = util.str2byte(console_id)
		if not isinstance(console_id, bytes):
			console_id = b'\0' * self.structure['console_id']
		self.console_id = console_id

	def set_issuer(self, issuer):
		if isinstance(issuer, str):
			issuer = util.str2byte(str.encode(issuer).hex())
		self.issuer = issuer + (b'\x00' * (self.structure['issuer'] - len(issuer)))

	def set_title_id(self, title_id):
		if isinstance(title_id, str):
			if len(title_id) == 4:
				title_id = b'\x00\x01\x00\x05' + util.str2byte(str.encode(title_id).hex())
			elif len(title_id) == 8:
				title_id = b'\x00\x01\x00\x05' + util.str2byte(title_id)
			elif len(title_id) == 16:
				title_id = util.str2byte(title_id)
		if not isinstance(title_id, bytes):
			title_id = b'\0' * self.header.structure['title_id']
		self.title_id = title_id

	def write(self, filepath):
		f = open(filepath, 'wb')
		f.write(self.get_packed())

	def __init__(self, filepath=None, title_key=None, console_id=None, title_id=None):
		if isinstance(filepath, str):  # Load file
			try:
				self.read(filepath)
			except FileNotFoundError:
				raise FileNotFoundError('File not found: ' + filepath)
		else:
			self.create(title_key=title_key, console_id=console_id, title_id=title_id)

def main(filepath):
	t = Ticket(filepath)
	t.info()

if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument('filepath', type=str, help='Path to file')
	arguments = parser.parse_args()
	main(arguments.filepath)
