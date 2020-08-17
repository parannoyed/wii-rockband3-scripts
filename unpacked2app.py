#!/usr/bin/env python3
from argparse import ArgumentParser
import os
import sys

sys.path.append('wii-scripts')
from u8 import U8
import util

def main(raw_option=None):	
	print('Rock Band 3 .APP Packer')

	if not raw_option:
		raw_option = input('\nTitle string: ')

	option = raw_option[0].lower()
	option += raw_option[1:].upper()

	title_str = option
	in_dir = os.path.join('files-unpacked', title_str)
	out_dir = os.path.join('files-app', title_str)
	tmd_filepath = os.path.join(in_dir, 'title.tmd')

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

		i += 1
		path_in = os.path.join(in_dir, songs[i]['dir'])
		file_out = util.get_hex_str(songs[i]['index'], 4) + '.app'
		path_out = os.path.join(out_dir, file_out)
		if os.path.isfile(path_out):
			print(songs[i]['dir'] + ' > ' + file_out + ' EXISTS, SKIPPING!')
		else:
			print(songs[i]['dir'] + ' > ' + file_out)
			u8.write(path_out, path_in)


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
