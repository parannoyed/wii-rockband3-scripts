#!/usr/bin/env python3
from argparse import ArgumentParser
import os
import sys

sys.path.append('wii-scripts')
import util


def main(raw_option=None):	
	print('Rock Band 3 DLC Add Batch')

	if not raw_option:
		raw_option = input('\nTitle string: ')

	option = raw_option[0].lower()
	option += raw_option[1:].upper()
	region = option[3:4]

	title_str = option
	in_dir = os.path.join('files-unpacked', title_str)

	dir_list = os.listdir(in_dir)
	dir_list.sort()

	songs_old = []
	songs_new = []

	for v in dir_list:
		split_name = v.split('_')
		if len(split_name) > 3 and split_name[0].isdigit():
			intdex = split_name.pop(0)
			hexdex = split_name.pop(0)
			song_type = split_name.pop()
			song_name = '_'.join(split_name)
			if int(intdex) > 0:
				songs_old.append({
					'dir': v,
					'index': int(intdex),
					'type': song_type,
					'name': song_name
				})
			else:
				songs_new.append({
					'dir': v,
					'index': int(intdex),
					'type': song_type,
					'name': song_name
				})
	
	if songs_old:
		for v in songs_old:
			print('Existing song: ' + v['dir'])
		cur_index = songs_old[-1]['index'] + 1
	else:
		cur_index = 1

	for i in range(0, len(songs_new), 2):
		if songs_new[i]['name'] != songs_new[i+1]['name']:
			print('ERROR: mismatched song names')
			print(songs_new[i]['dir'])
			print(songs_new[i+1]['dir'])
			return
		if songs_new[i]['type'] != 'meta' or songs_new[i+1]['type'] != 'song':
			print('ERROR: mismatched directory types')
			print(songs_new[i]['dir'])
			print(songs_new[i+1]['dir'])
			return

		# songs.dta
		fn = os.path.join(in_dir, songs_new[i]['dir'], 'content', 'songs', 'songs.dta')
		if os.path.isfile(fn):
			with open(fn, 'r', encoding='latin-1') as file :
				data = file.read()
			data = data.replace('sZAE/000', title_str + '/' + '{:03}'.format(cur_index))
			with open(fn, 'w', newline='\r\n') as file:
				file.write(data)

		# meta
		new_dir = '{:03}_{}_{}_{}'.format(cur_index, util.get_hex_str(cur_index, 4), songs_new[i]['name'], songs_new[i]['type'])
		print(songs_new[i]['dir'] + ' to ' + new_dir)
		os.rename(os.path.join(in_dir, songs_new[i]['dir']), os.path.join(in_dir, new_dir))
		cur_index += 1
		# song
		new_dir = '{:03}_{}_{}_{}'.format(cur_index, util.get_hex_str(cur_index, 4), songs_new[i+1]['name'], songs_new[i+1]['type'])
		print(songs_new[i+1]['dir'] + ' to ' + new_dir)
		os.rename(os.path.join(in_dir, songs_new[i+1]['dir']), os.path.join(in_dir, new_dir))
		cur_index += 1

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
	