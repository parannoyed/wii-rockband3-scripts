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
	available_slots = []

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
	
	cur_index = 1
	if songs_old:
		for v in songs_old:
			print('Existing song: ' + v['dir'])
			if v['index'] > cur_index:
				open_slot = (v['index'] - 1)
				if open_slot - cur_index:
					for i in range(cur_index, open_slot, 2):
						available_slots.append([i, i + 1])
				cur_index = v['index']
			cur_index += 1
	
	for i in range(cur_index, 511, 2):
		available_slots.append([i, i + 1])

	print('')
	print(len(available_slots), 'open song slots')

	for i in range(0, len(available_slots)):
		if songs_new:
			meta = songs_new.pop(0)
			song = songs_new.pop(0)
		else:
			return

		if meta['name'] != song['name']:
			print('ERROR: mismatched song names')
			print(meta['dir'])
			print(song['dir'])
			return
		if meta['type'] != 'meta' or song['type'] != 'song':
			print('ERROR: mismatched directory types')
			print(meta['dir'])
			print(song['dir'])
			return

		# songs.dta
		fn = os.path.join(in_dir, meta['dir'], 'content', 'songs', 'songs.dta')
		if os.path.isfile(fn):
			with open(fn, 'r', encoding='latin-1') as file :
				data = file.read()
			data = data.replace('sZAE/000', title_str + '/' + '{:03}'.format(available_slots[i][0]))
			with open(fn, 'w', newline='\r\n') as file:
				file.write(data)

		# meta
		new_dir = '{:03}_{}_{}_{}'.format(available_slots[i][0], util.get_hex_str(available_slots[i][0], 4), meta['name'], meta['type'])
		print(meta['dir'] + ' to ' + new_dir)
		os.rename(os.path.join(in_dir, meta['dir']), os.path.join(in_dir, new_dir))
		# song
		new_dir = '{:03}_{}_{}_{}'.format(available_slots[i][1], util.get_hex_str(available_slots[i][1], 4), song['name'], song['type'])
		print(song['dir'] + ' to ' + new_dir)
		os.rename(os.path.join(in_dir, song['dir']), os.path.join(in_dir, new_dir))

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
	