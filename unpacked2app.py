#!/usr/bin/env python3
from argparse import ArgumentParser
import os
import sys

sys.path.append('wii-scripts')
from tmd import TMD
from u8 import U8
import util

def main(raw_option=None):	
	print('Rock Band 3 .APP Packer')

	if not raw_option:
		raw_option = input('\nTitle string: ')

	option = raw_option[0].lower()
	option += raw_option[1:].upper()
	region = option[3:4]

	title_str = option
	in_dir = os.path.join('files-unpacked', title_str)
	out_dir = os.path.join('files-app', title_str)
	tmd_filepath = os.path.join(out_dir, 'title.tmd')
	tmd = TMD()

	# create or read/fix tmd
	if os.path.isfile(tmd_filepath):
		tmd.read(tmd_filepath)
	else:
		tmd.read(os.path.join('config', 'template.tmd'))
		tmd.header.title_id = b'\x00\x01\x00\x05' + option.encode('utf-8')
		# TODO
		#tmd.header.region = 

	if len(tmd.contents) == 0:
		with open(os.path.join('config', 'template.app'), 'rb') as f :
			data = f.read()
		tmd.add_content('00000000', index=0, type='0001', data=data)

	os.makedirs(out_dir, exist_ok=True)

	dir_list = os.listdir(in_dir)
	dir_list.sort()

	songs = []
	u8 = U8()

	for v in dir_list:
		split_name = v.split('_')
		if len(split_name) > 3 and split_name[0].isdigit():
			intdex = split_name.pop(0)
			hexdex = split_name.pop(0)
			song_type = split_name.pop()
			song_name = '_'.join(split_name)
			songs.append({
				'dir': v,
				'index': int(intdex),
				'type': song_type,
				'name': song_name
			})

	for i in range(0, len(songs), 2):
		# check directory names
		if songs[i]['name'] != songs[i+1]['name']:
			print('ERROR: mismatched song names')
			print(songs[i]['dir'])
			print(songs[i+1]['dir'])
			return
		if songs[i]['type'] != 'meta' or songs[i+1]['type'] != 'song':
			print('ERROR: mismatched directory types')
			print(songs[i]['dir'])
			print(songs[i+1]['dir'])
			return

		path_in = os.path.join(in_dir, songs[i]['dir'])
		file_out = util.get_hex_str(songs[i]['index'], 4) + '.app'
		path_out = os.path.join(out_dir, file_out)
		if os.path.isfile(path_out):
			print(songs[i]['dir'] + ' > ' + file_out + ' EXISTS, SKIPPING!')
		else:
			print(songs[i]['dir'] + ' > ' + file_out)
			u8.write(path_out, path_in)
			# add to tmd
			with open(path_out, 'rb') as f :
				data = f.read()
			tmd.add_content(util.int2byte(songs[i]['index'], 4), index=songs[i]['index'], type='4001', data=data)

		i += 1
		path_in = os.path.join(in_dir, songs[i]['dir'])
		file_out = util.get_hex_str(songs[i]['index'], 4) + '.app'
		path_out = os.path.join(out_dir, file_out)
		if os.path.isfile(path_out):
			print(songs[i]['dir'] + ' > ' + file_out + ' EXISTS, SKIPPING!')
		else:
			print(songs[i]['dir'] + ' > ' + file_out)
			u8.write(path_out, path_in)
			# add to tmd
			with open(path_out, 'rb') as f :
				data = f.read()
			tmd.add_content(util.int2byte(songs[i]['index'], 4), index=songs[i]['index'], type='4001', data=data)

	tmd.write(tmd_filepath)


if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument(
		'title_str',
		type=str,
		nargs='?',
		help='Title string'
	)
	arguments = parser.parse_args()
	main(arguments.title_str)
