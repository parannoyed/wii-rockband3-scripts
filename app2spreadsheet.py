#!/usr/bin/env python3
from argparse import ArgumentParser
import csv
import os
import sys

from dta import DTA

sys.path.append('wii-scripts')
from tmd import TMD
from u8 import U8
import util

def load_dir(in_dir):
	print('Looking in ' + in_dir)
	rval = []

	tmd_fn = os.path.join(in_dir, 'title.tmd')
	if os.path.isfile(tmd_fn):
		# load tmd
		tmd = TMD(tmd_fn)
		for v in tmd.contents:
			app_fn = os.path.join(in_dir, v.content_id.hex() + '.app')
			if os.path.isfile(app_fn):
				song_dta = None
				upgrade_dta = None
				short_name = None
				u8 = U8(app_fn)
				for i in range(len(u8.nodes)):
					if u8.nodes[i].type == b'\x00' and u8.content[i]['name'] == 'songs.dta':
						song_dta = DTA(u8.content[i]['data'])
						break
					elif u8.nodes[i].type == b'\x00' and u8.content[i]['name'] == 'upgrades.dta':
						upgrade_dta = DTA(u8.content[i]['data'])
					elif u8.nodes[i].type == b'\x01' and rval and u8.content[i]['name'] == rval[-1]['short_name']:
						rval[-1]['bin'] += ', ' + str(util.byte2int(v.index)).lstrip('0')
						rval[-1]['app'] += ', ' + str(v.content_id.hex()).lstrip('0')
				if song_dta:
					for song in song_dta.Songs:
						val = {
							'dir': in_dir,
							'title': tmd.get_short_title_id(),
							'bin': str(util.byte2int(v.index)).lstrip('0'),
							'app': str(v.content_id.hex()).lstrip('0'),
							'short_name': song.short_name,
							'artist': song.artist,
							'name': song.name,
							'album': song.album,
							'year': str(song.year_released),
							'genre': song.genre,
							'sub_genre': song.sub_genre,
							'origin': song.source
						}
						rval.append(val)
						print(val['dir'] + ', ' + val['app'] + ', ' + val['bin'] + ', ' + val['artist'] + ', ' + val['name'] + ', ' + val['album'] + ', ' + val['year'] + ', ' + val['genre'] + ', ' + val['origin'])
				if upgrade_dta:
					for upgrade in upgrade_dta.Songs:
						for song in rval:
							if song['short_name'] == upgrade.short_name:
								song['bin'] += ', ' + str(util.byte2int(v.index)).lstrip('0')
								song['app'] += ', ' + str(v.content_id.hex()).lstrip('0')
			#else:
			# MISSING FILE

	dir_list = os.listdir(in_dir)
	for d in sorted(dir_list):
		fn = os.path.join(in_dir, d)
		if os.path.isdir(fn):
			rval += load_dir(fn)
	return rval

def main(in_dir=None):	
	print('Rock Band 3 DLC spreadsheet')

	if not in_dir:
		in_dir = 'files-app'

	lines = load_dir(in_dir)

	with open('app2spreadsheet.csv', mode='w') as f:
		w = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		w.writerow(['Path', 'APP', 'BIN', 'Artist', 'Song', 'Album', 'Year', 'Genre', 'Origin'])
		for line in lines:
			w.writerow([line['dir'], line['app'], line['bin'],line['artist'],  line['name'], line['album'], line['year'], line['genre'], line['origin']])
	#for line in lines:
	#	print('|', line['app'], '|', line['bin'], '|', line['name'], '|', line['artist'], '|', line['album'], '|', line['year'], '|', line['genre'], '|', line['origin'], '|')

if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument(
		'path',
		type=str,
		nargs='?',
		help='Path'
	)
	arguments = parser.parse_args()
	main(arguments.path)
