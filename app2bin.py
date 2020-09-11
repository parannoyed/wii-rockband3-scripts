#!/usr/bin/env python3
from argparse import ArgumentParser
import os
import sys

sys.path.append('wii-scripts')
import crypto
from tmd import TMD
import util
from wad import DLCWAD

rb2_us = ['sZAE', 'sZBE', 'sZCE', 'sZDE', 'sZEE', 'sZFE', 'sZGE', 'sZHE', 'sZIE']
rb2_eu = ['sZAP', 'sZBP', 'sZCP', 'sZDP', 'sZEP', 'sZFP', 'sZGP', 'sZHP', 'sZIP']

def main(raw_option=None):	
	print('Rock Band 3 .BIN Packer')

	if not raw_option:
		raw_option = input('\nTitle string: ')

	option = raw_option[0].lower()
	option += raw_option[1:].upper()
	region = option[3:4]

	pack_key = rb3_pack_key
	if option in rb2_us or option in rb2_eu:
		pack_key = rb2_pack_key

	title_str = option
	in_dir = os.path.join('files-app', title_str)
	out_dir = os.path.join('files-bin', title_str)
	tmd_filepath = os.path.join(in_dir, 'title.tmd')
	
	print('\nChecking TMD...')
	tmd = TMD(tmd_filepath)
	write_tmd = False
	for i in range(len(tmd.contents)):
		appfilepath = os.path.join(in_dir, tmd.contents[i].content_id.hex() + '.app')
		if os.path.isfile(appfilepath):
			f_app = open(appfilepath, 'rb')
			data = f_app.read()
			f_size = util.int2byte(len(data), 8)
			if tmd.contents[i].size != f_size:
				print('Incorrect file size! Index: ' + f'{i:03}' + ', Content: ' + tmd.contents[i].content_id.hex() + '.app' + ', Fixing...')
				tmd.contents[i].size = f_size
				write_tmd = True
			f_hash = crypto.get_hash(data)
			if tmd.contents[i].sha1_hash != f_hash:
				print('Incorrect file hash! Index: ' + f'{i:03}' + ', Content: ' + tmd.contents[i].content_id.hex() + '.app' + ', Fixing...')
				tmd.contents[i].sha1_hash = f_hash
				write_tmd = True
			f_app.close()
	if write_tmd:
		print('Saving fixed TMD...')
		tmd.write(tmd_filepath)
	else:
		print('TMD looks good...')

	print('\nCreating .bin\'s...')
	tmd = TMD(tmd_filepath)
	if not os.path.isdir(out_dir):
		os.makedirs(out_dir, exist_ok=True)
	for i in range(len(tmd.contents)):
		appfilepath = os.path.join(in_dir, tmd.contents[i].content_id.hex() + '.app')
		if os.path.isfile(appfilepath):
			binfilename = f'{i:03}' + '.bin'
			binfilepath = os.path.join(out_dir, binfilename)
			
			f_app = open(appfilepath, 'rb')
			data = f_app.read()

			print('Index: ' + f'{i:03}' + ', Content: ' + tmd.contents[i].content_id.hex() + '.app' + ', Size: ' + str(util.byte2int(tmd.contents[i].size)) + ' bytes, Hash check: ', end='')
			if tmd.check_hash(i, data) == True:
				print('PASSED!')
			else:
				print('FAILED!')

			if os.path.isfile(binfilepath):
				print('SKIP:  ' + binfilename + ', FILE ALREADY EXISTS!')
			else:
				bin = DLCWAD(key=pack_key)
				bin.create(data, 'SZB' + region, i, tmd, console_id)
				print('File:  ' + binfilename + ', Size: ' + str(bin.get_file_size()) + ' bytes')
				bin.write(binfilepath)

if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument(
		'title_str',
		type=str,
		nargs='?',
		help='Title string'
	)
	arguments = parser.parse_args()

	console_id = None
	fn = os.path.join('config', 'console_id.txt')
	if os.path.isfile(fn):
		f = open(fn, 'rb')
		console_id = f.read()
		console_id = console_id.decode('utf-8')
	rb2_pack_key = None
	fn = os.path.join('config', 'pack_rb2.txt')
	if os.path.isfile(fn):
		f = open(fn, 'rb')
		rb2_pack_key = f.read()
		rb2_pack_key = pack_key.decode('utf-8')
	rb3_pack_key = None
	fn = os.path.join('config', 'pack_rb3.txt')
	if os.path.isfile(fn):
		f = open(fn, 'rb')
		rb3_pack_key = f.read()
		rb3_pack_key = pack_key.decode('utf-8')
	
	main(arguments.title_str)
