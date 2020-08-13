#!/usr/bin/env python3
import os
from argparse import ArgumentParser

import util

class U8:

	class Header(util.StructBase):
		structure = {
				'magic': 4,
				'rootnode_offset': 4, # start of nodes
				'header_size': 4, # length of nodes + string table
				'data_offset': 4, # where data starts
				'padding': 16
			}
		def __init__(self, data=None):
			self.magic = b'\x55\xaa\x38\x2d'
			self.rootnode_offset = b'\x00\x00\x00\x20'

	class Node(util.StructBase):
		structure = {
				'type': 1,
				'name_offset': 3,
				'data_offset': 4,
				'size': 4,
			}
		def __init__(self, data=None):
			if data:
				self.set_data(data)

	def create(self, data=None):
		self.header = self.Header()
		self.nodes = []
		self.content = []
		
		# bytes, read
		if isinstance(data, bytes):
			header_size = self.header.get_size()

			self.header.set_data(data[:header_size])
			print('header:')
			print(vars(self.header))
			node_table = data[header_size:header_size+util.byte2int(self.header.header_size)]

			self.nodes.append(self.Node(node_table))
			self.content.append({'name': '', 'data': None})
			print('root node:')
			print(vars(self.nodes[0]))

			num_nodes = util.byte2int(self.nodes[0].size)
			node_table_size = num_nodes * self.nodes[0].get_size()
			string_table = node_table[node_table_size:]
			print(string_table)

			read_start = self.nodes[0].get_size()
			read_end = read_start
			for i in range(1, util.byte2int(self.nodes[0].size)):
				print('node ' + str(i) + ': ')
				# unpack node
				node = self.Node()
				read_end += node.get_size()
				node.set_data(node_table[read_start:read_end])
				self.nodes.append(node)
				read_start += node.get_size()
				print(vars(node))
				# unpack string
				start = util.byte2int(self.nodes[i].name_offset)
				stop = string_table.find(b'\x00', start)
				name = string_table[start:stop].decode('utf-8')
				self.content.append({'name': name, 'data': None})
				print(name)
				if node.type == b'\x00':
					start = util.byte2int(node.data_offset)
					stop = start + util.byte2int(node.size)
					self.content[i]['data'] = data[start:stop]

		else:
			# string, create from directory
			if isinstance(data, str) and os.path.isdir(data):
				# root node
				node = self.Node()
				node.type = b'\x01'
				node.type = b'\x01'
				self.nodes.append(node)
				self.content.append({'name': '', 'data': None})

				new_dir = data
				base_dir = new_dir
				dir_data_offset = 0
				cur_dir = '.'
				while new_dir:
					dir_list = os.listdir(new_dir)
					new_dir = False
					for i in dir_list:
						i_path = os.path.join(base_dir, i)
						if os.path.isfile(i_path):
							print(os.path.join(cur_dir, i))
							f = open(i_path, 'rb')
							content = {'name': i, 'data': f.read()}
							self.content.append(content)
							node = self.Node()
							node.type = b'\x00'
							node.name_offset = util.int2byte(len(self.get_string_table()), 3)
							node.size = util.int2byte(len(content['data']), 4)
							self.nodes.append(node)
							
					for i in dir_list:
						i_path = os.path.join(base_dir, i)
						if os.path.isdir(i_path):
							cur_dir = os.path.join(cur_dir, i)
							print(cur_dir)
							self.content.append({'name': i, 'data': None})
							node = self.Node()
							node.type = b'\x01'
							node.name_offset = util.int2byte(len(self.get_string_table()), 3)
							node.data_offset = util.int2byte(dir_data_offset, 4)
							dir_data_offset += 1
							self.nodes.append(node)
							new_dir = i_path
					base_dir = new_dir

				# build new data
				data_offset = self.get_data_offset()
				self.header.header_size = util.int2byte(self.get_header_size(), 4)
				self.header.data_offset = util.int2byte(data_offset, 4)
				# for some reason, they pack in reverse
				for node in reversed(self.nodes):
					if node.type == b'\x00':
						node.data_offset = util.int2byte(data_offset, 4)
						# used for next file data offset
						node_size = util.byte2int(node.size)
						data_offset += node_size + util.pad_by(node_size, 64)
					if node.type == b'\x01':
						# lazy hack
						node.size = util.int2byte(len(self.nodes), 4)

	def extract(self, to_dir, from_file=None):
		if from_file:
			self.read(from_file)
		os.makedirs(to_dir, exist_ok=True)
		os.chdir(to_dir)

		last_file = [util.byte2int(self.nodes[0].size)]

		for i in range(1, util.byte2int(self.nodes[0].size)):
			node = self.nodes[i]
			name = self.content[i]['name']
			# directory
			if node.type == b'\x01':
				print('Creating: ' + name + ' ('+str(i)+')')
				os.mkdir(name)
				os.chdir(name)
				last_file.append(util.byte2int(node.size))
			# file
			elif node.type == b'\x00':
				print('Extracting: ' + name + ' ('+str(i)+')')
				f = open(name, 'wb')
				f.write(self.content[i]['data'])
				f.close()
			if (i+1) == last_file[-1]:
				os.chdir('..')
				last_file.pop()

	def get_data_offset(self):
		data_offset = util.byte2int(self.header.rootnode_offset) + self.get_nodes_size() + len(self.get_string_table())
		data_offset += util.pad_by(data_offset, 64)
		return data_offset

	def get_header_size(self):
		return self.get_nodes_size() + len(self.get_string_table())

	def get_nodes_size(self):
		return self.nodes[0].get_size() * len(self.nodes)

	def get_packed(self):				
		packed = b''
		packed += self.header.get_packed()
		for i in range(len(self.nodes)):
			packed += self.nodes[i].get_packed()
		packed += self.get_string_table()
		packed += util.pad_zeros(len(packed), 64)
		# for some reason, they pack in reverse
		for content in reversed(self.content):
			if content['data']:
				packed += content['data']
				pad_by = util.pad_by(len(packed), 64)
				packed += b'\x00' * pad_by
		# remove padding from last file
		packed = packed[:-pad_by]
		return packed

	def get_string_table(self):
		string_table = b'\x00' # root node
		for i in range(1, len(self.nodes)):
			string_table += self.content[i]['name'].encode('utf-8') + b'\x00'
		return string_table

	def read(self, filepath):
		if os.path.isdir(filepath):
			self.create(filepath)
		else:
			f = open(filepath, 'rb')
			self.create(f.read())

	def write(self, to_file, from_dir=None):
		if from_dir:
			self.read(from_dir)
		f = open(to_file, 'wb')
		f.write(self.get_packed())

	def __init__(self, filepath=None, key=None, console_id=None):
		self.header = self.Header()
		self.nodes = []
		self.content = []

		if isinstance(filepath, str):
			try:
				self.read(filepath)
			except FileNotFoundError:
				raise FileNotFoundError('File not found: ' + filepath)

def main():
	parser = ArgumentParser()
	parser.add_argument('input', type=str, help='Path to input')
	parser.add_argument('output', type=str, help='Path to output')
	arguments = parser.parse_args()

	#u8 = U8(arguments.input)
	#u8.extract(arguments.output)
	
	#u8 = U8()
	#u8.write(arguments.output, arguments.input)

if __name__ == "__main__":
	main()
