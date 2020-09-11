#!/usr/bin/env python3
from argparse import ArgumentParser
import os
import re
import sys

# ported from https://github.com/RBTools/CON-Tools "C3 Tools/DTAParser.cs"
class DTA():

	class SongData():

		def __init__(self):
			self.dta_lines = []
			self.song_id = 0
			self.name = ''
			self.short_name = ''
			self.artist = ''
			self.album = ''
			self.source = ''
			self.gender = 'N/A'
			self.genre = ''
			self.raw_genre = ''
			self.sub_genre = ''
			self.file_path = ''
			self.internal_name = ''
			self.drum_bank = ''
			self.percussion_bank = ''
			self.override_name = ''
			self.chart_author = ''
			self.attenuation_values = ''
			self.panning_values = ''
			self.pro_bass_tuning = ''
			self.pro_guitar_training = ''
			self.instrument_solos = ''
			self.encoding = ''
			self.languages = ''
			self.song_id_string = ''
			self.midi_file = ''
			self.song_link = ''
			self.year_recorded = 0
			self.year_released = 0
			self.drums_diff = 0
			self.pro_bass_diff = 0
			self.bass_diff = 0
			self.pro_guitar_diff = 0
			self.vocals_diff = 0
			self.keys_diff = 0
			self.pro_keys_diff = 0
			self.band_diff = 0
			self.track_number = 0
			self.rating = 4
			self.game_version = -1
			self.scroll_speed = 2300
			self.tonality = 0
			self.tonic_note = -1
			self.length = 0
			self.preview_end = 0
			self.preview_start = 0
			self.channels_bass = 0
			self.channels_drums = 0
			self.channels_guitar = 0
			self.channels_keys = 0
			self.channels_vocals = 0
			self.channels_crowd = 0
			self.channels_total = 0
			self.hopo_threshold = 0
			self.mute_volume = -96
			self.mute_volume_vocals = -12
			self.tuning_cents = 0
			self.anim_tempo = 0
			self.guide_pitch = -3.0
			self.master = False
			self.do_not_export = False
			self.rb3_version = False
			self.karaoke = False
			self.multitrack = False
			self.convert = False
			self.expert_only = False
			self.rhythm_bass = False
			self.rhythm_keys = False
			self.double_bass = False
			self.disable_pro_keys = False
			self.has_song_id_error = False
			self.cat_emh = False
			self.dta_index = 0
			self.ps_delay = 0

			self.vocal_parts = 0

	def create(self, data):
		self.ReadDTA(data)

	def ReadDTA(self, data):
		self.Songs = []

		DTAEntries = self.GetDTAEntries(data)

		if not len(DTAEntries):
			return False

		for entry in DTAEntries:
			self.Songs.append(self.SongData())
			index = len(self.Songs) - 1
			song = self.Songs[index]
			song.dta_lines = entry
			song.dta_index = index

			opened = 0
			line = ''
			isDLC = False
			isRB1 = False

			for z in range(len(entry)):
				line  = entry[z]

				if line.strip().startswith(';;'): 
					continue # skip commented out lines
				if not line or line.isspace():
					continue # don't want empty lines

				if line.find('(') >= 0:
					opened += 1
				# short_name
				if opened == 1 and line.strip().startswith('(') and ')' not in line:
					if line.strip() == '(':
						song.short_name = entry[z + 1].replace('\'', '').strip()
					else:
						song.short_name = line.replace('(', '').replace('\'', '').strip()
				# name
				if '(name' in line and 'songs/' not in line:
					song.name = self.GetSongName(line)
				elif '\'name\'' in line and 'songs/' not in line:
					z += 1
					line = entry[z]
					if 'songs/' not in line:
						song.name = self.GetSongName(line)
					else:
						song.file_path = self.GetSongPath(line)
						song.internal_name = self.GetInternalName(line)
				elif 'songs/' in line:
					song.file_path = self.GetSongPath(line)
					song.internal_name = self.GetInternalName(line)
				elif 'midi_file' in line:
					song.midi_file = line.replace('midi_file', '').replace('(', '').replace(')', '').replace('"', '').strip()
				elif '(artist' in line:
					song.artist = self.GetArtistName(line)
				elif '\'artist\'' in line:
					z += 1
					line = entry[z]
					song.artist = self.GetArtistName(line)
				elif '(master' in line or '(\'master' in line:
					song.master = '1' in line or 'true' in line.lower()
				elif '(tracks' in line:
					while line != None and line.strip() != ")":
						if 'bass' in line.lower():
							song.channels_bass = self.GetChannels(line, "bass")
						elif 'guitar' in line.lower():
							song.channels_guitar = self.GetChannels(line, "guitar")
						elif 'keys' in line.lower():
							song.channels_keys = self.GetChannels(line, "keys")
						elif 'vocals' in line.lower():
							song.channels_vocals = self.GetChannels(line, "vocals")
						elif 'drum' in line.lower():
							song.channels_drums = self.GetChannels(line, "drum")
						elif 'crowd_channels' in line.lower():
							song.channels_crowd = self.GetChannels(line, "crowd_channels")
						z += 1
						line = entry[z]
				elif '\'tracks\'' in line:
					z += 1
					line = entry[z]
					while line != None and not 'pans' in line.lower():
						if 'bass' in line.lower():
							z += 1
							line = entry[z]
							song.channels_bass = self.GetChannels(line, "bass")
						elif 'guitar' in line.lower():
							z += 1
							line = entry[z]
							song.channels_guitar = self.GetChannels(line, "guitar")
						elif 'keys' in line.lower():
							z += 1
							line = entry[z]
							song.channels_keys = self.GetChannels(line, "keys")
						elif 'vocals' in line.lower():
							z += 1
							line = entry[z]
							song.channels_vocals = self.GetChannels(line, "vocals")
						elif 'drum' in line.lower():
							z += 1
							line = entry[z]
							song.channels_drums = self.GetChannels(line, "drum")
						elif 'crowd_channels' in line.lower():
							song.channels_crowd = self.GetChannels(line, "crowd_channels")
						z += 1
						line = entry[z]
					if '\'pans\'' in line:
						z += 1
						line = entry[z]
						song.panning_values = line.replace("(", "").replace(")", "").replace("'", "").replace("pans", "")
				elif 'song_id' in line:
					try:
						song.song_id_string = self.GetSongID(line)
						song.has_song_id_error = not song.song_id_string or song.song_id_string.isspace()
						song.song_id = int(song.song_id_string)
					except Exception:
						# fails because it's not numeric, make it into a custom
						song.song_id = 99999999
				elif 'vocal_parts' in line:
					song.vocal_parts = self.GetVocalParts(line)
				elif '\'vols\'' in line:
					z += 1
					line = entry[z]
					song.attenuation_values = line.replace("(", "").replace(")", "").replace("'", "").replace("vols", "")
				elif '(vols' in line:
					song.attenuation_values = line.replace("(", "").replace(")", "").replace("'", "").replace("vols", "")
				elif '\'pans\'' in line:
					z += 1
					line = entry[z]
					song.panning_values = line.replace("(", "").replace(")", "").replace("'", "").replace("pans", "")
				elif '(pans' in line:
					song.panning_values = line.replace("(", "").replace(")", "").replace("'", "").replace("pans", "")
				elif '(cores' in line:
					song.channels_total = self.GetAudioChannels(line)
				elif '\'cores\'' in line:
					z += 1
					line = entry[z]
					song.channels_total = self.GetAudioChannels(line)
				elif 'hopo_threshold' in line:
					song.hopo_threshold = self.int_from_dta_string(line)
					if song.hopo_threshold == -1:
						song.hopo_threshold = 0
				elif 'crowd_channels' in line:
					song.channels_crowd = self.GetChannels(line, "crowd_channels")
				elif 'bank sfx' in line and not 'drum_bank' in line:
					song.percussion_bank = line.replace("(bank", "").replace("(", "").replace(")", "").strip()
				elif '\'bank\'' in line:
					z += 1
					line = entry[z]
					song.percussion_bank = line.replace("\"", "").strip()
				elif 'drum_bank' in line:
					song.drum_bank = line.replace("drum_bank", "").replace("(", "").replace(")", "").strip()
				elif 'song_scroll_speed' in line:
					song.scroll_speed = self.int_from_dta_string(line)
					if song.scroll_speed == -1:
						song.scroll_speed = 2300
				elif ('(preview' in line or '(\'preview' in line) and not line.strip().startswith(';'):
					song.preview_start = self.GetPreviewTimes(line, 0)
					song.preview_end = self.GetPreviewTimes(line, 1)
				elif 'song_length' in line:
					try:
						song.length = self.GetSongDurationLong(line)
					except Exception:
						song.length = 0
				elif ('(\'drum\'' in line or '(drum ' in line) and not 'solo' in line:
					song.drums_diff = self.DrumDiff(line)
				elif ('(\'guitar\'' in line or '(guitar ' in line) and not 'solo' in line:
					song.guitar_diff = self.GuitarDiff(line)
				elif ('(\'bass\'' in line or '(bass ' in line) and not 'solo' in line:
					song.bass_diff = self.BassDiff(line)
				elif ('(\'vocals\'' in line or '(vocals ' in line) and not 'solo' in line:
					song.vocals_diff = self.VocalsDiff(line)
				elif ('(\'keys\'' in line or '(keys ' in line) and not 'solo' in line:
					song.keys_diff = self.KeysDiff(line)
				elif 'real_keys' in line:
					song.pro_keys_diff = self.ProKeysDiff(line)
				elif 'real_guitar' in line and not 'tuning' in line:
					song.pro_guitar_diff = self.ProGuitarDiff(line)
				elif 'real_bass' in line and not 'tuning' in line:
					song.pro_bass_diff = self.ProBassDiff(line)
				elif '(\'band\'' in line or '(band ' in line:
					song.band_diff = self.BandDiff(line)
				elif 'version' in line and not 'short' in line and not 'fake' in line:
					song.game_version = self.GetGameVersion(line)
				elif 'game_origin' in line.lower():
					song.source = self.GetSourceGame(line)
				elif '(solo (' in line.lower():
					song.instrument_solos = line.replace("solo", "").replace("(", "").replace(")", "")
				# TODO: encoding didn't work right in my inital tests
				# example: '' 'latin1'
				# should just be: latin1?
				elif 'encoding' in line.lower():
					song.encoding = line.lower().replace("encoding", "").replace("(", "").replace(")", "")
				elif 'rating' in line.lower():
					song.rating = self.GetRating(line)
				elif 'genre' in line and not 'subgenre' in line:
					song.genre = self.DoGenre(line, True)
					song.raw_genre = self.GetRawGenre(line)
				elif 'subgenre_' in line.lower():
					song.sub_genre = self.DoSubGenre(line, True)
					song.raw_sub_genre = self.GetRawSubGenre(line)
				elif 'gender' in line:
					if 'female' in line.lower():
						song.gender = 'Female'
					else:
						song.gender = 'Male'
				elif '(year_released' in line or '(\'year_released' in line:
					song.year_released = self.int_from_dta_string(line)
				elif '(year_recorded' in line or '(\'year_recorded' in line:
					song.year_recorded = self.int_from_dta_string(line)
				elif '(album_name' in line:
					song.album = self.GetAlbumName(line)
				elif '\'album_name\'' in line:
					z += 1
					line = entry[z]
					song.album = self.GetAlbumName(line)
				elif 'track_number' in line.lower():
					song.track_number = self.int_from_dta_string(line)
				elif '(exported TRUE)' in line.strip():
					isRB1 = True
					song.source = "rb1"
				elif 'vocal_tonic_note' in line:
					song.tonic_note = self.int_from_dta_string(line)
					if song.tonic_note == -1:
						song.tonic_note = 0
				elif 'song_tonality' in line:
					song.tonality = self.int_from_dta_string(line)
					if song.tonality == -1:
						song.tonality = 0
				elif 'guide_pitch' in line:
					song.guide_pitch = self.GetGuidePitch(line)
				elif 'mute_volume_vocals' in line:
					song.mute_volume_vocals = self.GetVolumeLevel(line)
				elif 'mute_volume' in line and not 'vocals' in line:
					song.mute_volume = self.GetVolumeLevel(line)
				elif 'tuning_offset' in line:
					song.tuning_cents = self.int_from_dta_string(line)
					if song.tuning_cents == -1:
						song.tuning_cents = 0
				elif 'guitar_tuning' in line:
					song.pro_guitar_tuning = self.GetTuning(line)
				elif 'bass_tuning' in line:
					song.pro_bass_tuning = self.GetTuning(line)
				elif 'downloaded' in line.lower() and 'true' in line.lower():
					isDLC = True
				# read extra Magma C3 info
				elif ';Song authored by ' in line:
					song.chart_author = line.replace(";Song authored by ", "").strip()
				elif ';Song=' in line:
					song.override_name = line.replace(";Song=", "").strip()
				elif ';SongTitle=' in line:
					song.override_name = line.replace(";SongTitle=", "").strip()
				elif ';Language(s)' in line:
					song.languages = line.replace(";Languages(s)", "").replace("=", "")
				elif ';DisableProKeys=1' in line:
					song.disable_pro_keys = True
				elif ';RhythmBass=1' in line:
					song.rhythm_bass = True
				elif ';RhythmKeys=1' in line and not song.RhythmBass:
					song.rhythm_keys = True
				elif ';2xBass=1' in line:
					song.double_bass = True
				elif ';Karaoke=1' in line:
					song.karaoke = True
				elif ';Multitrack=1' in line:
					song.multitrack = True
				elif ';Convert=1' in line:
					song.convert = True
				elif ';RB3Version=1' in line:
					song.rb3_version = True
				elif ';CATemh=1' in line:
					song.cat_emh = True
				elif ';ExpertOnly=1' in line:
					song.expert_only = True

			# old songs didn't have the vocal_parts line when it was one part
			if song.vocals_diff > 0 and song.vocal_parts == 0:
				song.vocal_parts = 1
			if song.source.isspace():
				song.source = "rb1_dlc" # default to old DLC

			if song.chart_author.strip().isspace() and len(song.song_id_string) == 7:
				val = song.song_id_string[0:2]
				if val == '10':
					song.chart_author = 'Harmonix'
				elif val == '50':
					song.chart_author = 'Rock Band Network'

			if song.song_id_string.isspace():
				song.song_id_string = str(song.song_id)

			if not isDLC or not isRB1:
				continue

			if song.source == '' or song.source == 'rb1':
				song.source = 'rb1_dlc'
			elif song.source == 'rb2':
				song.source = 'rb2_dlc'
		return True

	def BandDiff(self, raw_line):
		diffs = [0, 165, 215, 243, 267, 292, 345]
		return self.DoDifficulty(self.int_from_dta_string(raw_line), diffs)

	def BassDiff(self, raw_line):
		diffs = [0, 135, 181, 228, 293, 364, 436]
		return self.DoDifficulty(self.int_from_dta_string(raw_line), diffs)

	def DoDifficulty(self, diff, diffs):
		if diff > 0 and diff < diffs[1]:
			return 1
		if diff >= diffs[1] and diff < diffs[2]:
			return 2
		if diff >= diffs[2] and diff < diffs[3]:
			return 3
		if diff >= diffs[3] and diff < diffs[4]:
			return 4
		if diff >= diffs[4] and diff < diffs[5]:
			return 5
		if diff >= diffs[5] and diff < diffs[6]:
			return 6
		if diff >= diffs[6]:
			return 7
		else:
			return 0

	# raw_line: Raw line from songs.dta file
	# is_dta_line: Set to true if it's a raw line, false if raw genre
	def DoGenre(self, raw_line, is_dta_line):
		genres = {
				"alternative": "Alternative",
				"blues": "Blues",
				"classical": "Classical",
				"classicrock": "Classic Rock",
				"country": "Country",
				"emo": "Emo",
				"fusion": "Fusion",
				"glam": "Glam",
				"grunge": "Grunge",
				"hiphoprap": "Hip-Hop/Rap",
				"indierock": "Indie Rock",
				"jazz": "Jazz",
				"jrock": "J-Rock",
				"latin": "Latin",
				"metal": "Metal",
				"new_wave": "New Wave",
				"novelty": "Novelty",
				"numetal": "Nu-Metal",
				"other": "Other",
				"poprock": "Pop-Rock",
				"popdanceelectronic": "Pop/Dance/Electronic",
				"prog": "Prog",
				"punk": "Punk",
				"rbsoulfunk": "R&B/Soul/Funk",
				"reggaeska": "Reggae/Ska",
				"inspirational": "Inspirational",
				"rock": "Rock",
				"southernrock": "Southern Rock",
				"urban": "Urban",
				"world": "World"
			}
		v = raw_line
		if is_dta_line:
			v = self.GetRawGenre(raw_line)
		if v in genres:
			v = genres[v]
		return v

	# raw_line: Raw line from songs.dta file
	# is_dta_line: Set to true if it's a raw line, false if raw genre
	def DoSubGenre(self, raw_line, is_dta_line):
		subgenres = {
				"alternative": "Alternative",
				"college": "College",
				"other": "Other",
				"acoustic": "Acoustic",
				"chicago": "Chicago",
				"classic": "Classic",
				"contemporary": "Contemporary",
				"country": "Country",
				"delta": "Delta",
				"electric": "Electric",
				"classicrock": "Classic Rock",
				"bluegrass": "Bluegrass",
				"honkytonk": "Honky Tonk",
				"outlaw": "Outlaw",
				"traditionalfolk": "Traditional Folk",
				"emo": "Emo",
				"fusion": "Fusion",
				"glam": "Glam",
				"goth": "Goth",
				"acidjazz": "Acid Jazz",
				"experimental": "Experimental",
				"ragtime": "Ragtime",
				"smooth": "Smooth",
				"metal": "Metal",
				"black": "Black",
				"core": "Core",
				"death": "Death",
				"hair": "Hair",
				"industrial": "Industrial",
				"power": "Power",
				"prog": "Prog",
				"speed": "Speed",
				"thrash": "Thrash",
				"novelty": "Novelty",
				"numetal": "Nu-Metal",
				"disco": "Disco",
				"motown": "Motown",
				"pop": "Pop",
				"rhythmandblues": "Rhythm and Blues",
				"softrock": "Soft Rock",
				"soul": "Soul",
				"teen": "Teen",
				"progrock": "Prog Rock",
				"garage": "Garage",
				"hardcore": "Hardcore",
				"dancepunk": "Dance Punk",
				"arena": "Arena",
				"blues": "Blues",
				"funk": "Funk",
				"hardrock": "Hard Rock",
				"psychadelic": "Psychedelic",
				"rock": "Rock",
				"rockandroll": "Rock and Roll",
				"rockabilly": "Rockabilly",
				"ska": "Ska",
				"surf": "Surf",
				"folkrock": "Folk Rock",
				"reggae": "Reggae",
				"southernrock": "Southern Rock",
				"alternativerap": "Alternative Rap",
				"dub": "Dub",
				"downtempo": "Downtempo",
				"electronica": "Electronica",
				"gangsta": "Gangsta",
				"hardcoredance": "Hardcore Dance",
				"hardcorerap": "Hardcore Rap",
				"hiphop": "Hip Hop",
				"drumandbass": "Drum and Bass",
				"oldschoolhiphop": "Old School Hip Hop",
				"rap": "Rap",
				"triphop": "Trip Hop",
				"undergroundrap": "Underground Rap",
				"acapella": "A capella",
				"classical": "Classical",
				"contemporaryfolk": "Contemporary Folk",
				"oldies": "Oldies",
				"house": "House",
				"techno": "Techno",
				"breakbeat": "Breakbeat",
				"ambient": "Ambient",
				"trance": "Trance",
				"chiptune": "Chiptune",
				"dance": "Dance",
				"new_wave": "New Wave",
				"electroclash": "Electroclash",
				"darkwave": "Dark Wave",
				"synth": "Synthpop",
				"indierock": "Indie Rock",
				"mathrock": "Math Rock",
				"lofi": "Lo-fi",
				"shoegazing": "Shoegazing",
				"postrock": "Post Rock",
				"noise": "Noise",
				"grunge": "Grunge",
				"jrock": "J-Rock",
				"latin": "Latin",
				"inspirational": "Inspirational",
				"world": "World"
			}
		v = raw_line
		if is_dta_line:
			v = self.GetRawSubGenre(raw_line).replace("subgenre_", "").strip()
		if v in subgenres:
			v = subgenres[v]
		return v

	def DrumDiff(self, raw_line):
		diffs = [0, 124, 151, 178, 242, 345, 448]
		return self.DoDifficulty(self.int_from_dta_string(raw_line), diffs)

	def GetDTAEntries(self, data):
		DTAEntries = []
		opened = 0
		closed = 0
		counter = 0
		DTAEntries.append([])

		for line in data.splitlines():
			if line.strip().startswith(';;') and ';;ORIG_ID=' not in line: 
				continue # skip commented out lines
			if not line or line.isspace():
				continue # don't want empty lines
			if line.strip().startswith(';') and opened == 0:
				continue # skip hmx comments in between songs

			# possibly need to remove nbsp?
			if line.strip().startswith(')(') or line.strip().endswith(')(') and (closed + 1 == opened): 
				# back-to-back dta entries combine )(
				line = line.strip()
				index = line.find('(')
				DTAEntries[counter].append(line[0:index])
				counter += 1
				DTAEntries.append([])
				DTAEntries[counter].append(line[index:len(line) - index])
				opened = 1
				closed = 0
				continue

			if line.find(')') > -1:
				closed = closed + line.count(')') # rather than add +1, count how many instances in the string

			if line.find('(') > -1:
				opened = opened + line.count('(') # rather than add +1, count how many instances in the string

			DTAEntries[counter].append(line)

			if closed != opened or closed <= 0:
				continue
			opened = 0
			closed = 0
			counter += 1
			DTAEntries.append([])

		DTAEntries.pop() # remove blank last entry
		return DTAEntries

	def GetAlbumName(self, raw_line):
		album = self.RemoveDTAComments(raw_line)
		album = album.replace("(album_name", "")
		album = album.replace("(\"", "").replace("\")", "").strip()
		if album.startswith("\""):
			album = album[1:len(album)]
		if album.endswith("\""):
			album = album[0:len(album) - 1]
		if ';' in album:
			album = album[0:album.find(";")]
		album = album.strip().replace("\\q", "\"")
		# i left out a bunch of character fixing
		return album

	def GetArtistName(self, raw_line):
		artist = self.RemoveDTAComments(raw_line)
		artist = artist.replace('(artist', '')
		artist = artist.replace('("', '').replace('")', '').strip()
		if artist.startswith('"'):
			artist = artist[1:]
		if artist.endswith('"'):
			artist = artist[:-1]
		if ';' in artist:
			artist = artist[0:artist.find(';')]
		artist = artist.strip().replace('\\q', '"')
		# i left out a bunch of character fixing
		return artist

	def GetAudioChannels(self, raw_line):
		channels = self.RemoveDTAComments(raw_line)
		channels = channels.replace("cores", "")
		channels = channels.replace("'", "")
		channels = channels.replace("(", "")
		channels = channels.replace(")", "")
		channels = channels.replace("-", "")
		channels = channels.replace(" ", "").strip()

		return len(channels)

	def GetChannels(self, raw_line, remove):
		if '()' in raw_line:
			return 0 # old GHtoRB3 songs have empty entries
		channels = raw_line.replace("(", "").replace("tracks", "")
		channels = channels.replace(remove, "")
		channels = channels.replace(")", "")
		channels = channels.replace("'", "").strip()

		number = number = len(channels.split(' '))
		return number

	def GetGameVersion(self, raw_line):
		version = raw_line.replace("version", "").replace("'", "").replace("(", "").replace(")", "").strip()
		version = self.RemoveDTAComments(version)
		try:
			return int(version)
		except Exception:
			return 0

	def GetGuidePitch(self, line):
		pitch = -3.0
		volume = line.replace("guide_pitch_volume", "")
		volume = volume.replace("'", "")
		volume = volume.replace("(", "")
		volume = volume.replace("\"", "")
		volume = volume.strip()
		try:
			if ')' in volume:
				volume = volume[0:volume.find(")")]
			pitch = float(volume)
		except Exception:
			return pitch
		return pitch

	def GetInternalName(self, raw_line):
		index1 = raw_line.find('/') + 1
		index2 = raw_line.find('/', index1)
		return raw_line[index1:index2]

	def GetPreviewTimes(self, raw_line, request_type):
		preview = self.RemoveDTAComments(raw_line)
		preview = preview.replace("preview", "").replace("(", "").replace(")", "").replace("'", "").replace("\"", "").strip()
		previews = preview.split(' ')
		try:
			return int(previews[request_type])
		except Exception:
			return 0

	def GetRating(self, raw_line):
		rating = self.int_from_dta_string(raw_line)
		if rating > 0 and rating < 5: # RB3 uses 1,2,3,4
			return rating
		return -1

	def GetRawGenre(self, raw_line):
		# old style
		if '(genre' in raw_line and len(raw_line) > 11:
			genre = self.RemoveDTAComments(raw_line)
			genre = genre.replace("(genre", "").replace(")", "").strip()
			return genre

		# new style
		if not '\'genre\'' in raw_line or len(raw_line) <= 15:
			return ''
		#genre = raw_line.Substring(13, raw_line.Length - 15)
		genre = self.RemoveDTAComments(raw_line)
		genre = genre.replace("'genre'", "").replace("'", "").replace("(", "").replace(")", "").strip()
		return genre

	def GetRawSubGenre(self, raw_line):
		# remove "sub_genre" if it's in the same line
		subgenre = self.RemoveDTAComments(raw_line)
		subgenre = subgenre.replace("sub_genre", "")
		subgenre = subgenre.replace("'", "")
		subgenre = subgenre.replace("\"", "")
		subgenre = subgenre.replace("(", "")
		subgenre = subgenre.replace(")", "")
		return subgenre.strip()

	def GetSongDurationLong(self, raw_line):
		rval = self.int_from_dta_string(raw_line)
		# con tools returns zero for this one, instead of -1 like everything else
		if rval == -1:
			rval = 0
		return rval

	def GetSongID(self, raw_line):
		songid = self.RemoveDTAComments(raw_line)
		songid = songid.replace("song_id", "")
		songid = songid.replace("(", "")
		songid = songid.replace("'", "")
		songid = songid.replace("\"", "").strip()

		index = songid.find(')')
		if index > -1:
			songid = songid[0:index]
		return songid

	def GetSongName(self, raw_line):
		song = self.RemoveDTAComments(raw_line)
		song = song.replace('(name', '')
		song = song.replace('("', '').replace('")', '').strip()
		if song.startswith('"'):
			song = song[1:len(song)]
		if song.endswith('"'):
			song = song[0:len(song) - 1]
		if ';' in song:
			song = song[0:song.find(';')]
		song = song.strip().replace('\\q', '"')
		# i left out a bunch of character fixing
		return song

	def GetSongPath(self, raw_line):
		return raw_line.replace('(name', '').replace(')', '').replace('"', '').replace('.mid', '').replace('midi_file', '').replace('(', '').strip()

	def GetSourceGame(self, raw_line):
		origin = raw_line.replace("game_origin", "").replace("'", "").replace("(", "").replace(")", "").strip()
		origin = self.RemoveDTAComments(origin)
		return origin.strip()

	def GetTuning(self, raw_line):
		tuning = self.RemoveDTAComments(raw_line)
		tuning = tuning.replace("(real_guitar_tuning (", "")
		tuning = tuning.replace("(real_bass_tuning (", "")
		tuning = tuning.replace(")", "")
		tuning = tuning.replace("(", "")
		tuning = tuning.replace("'", "").strip()
		return tuning

	def GetVocalParts(self, raw_line):
		parts = raw_line.replace("vocal_parts", "").replace("'", "").replace("(", "").replace(")", "").strip()
		parts = self.RemoveDTAComments(parts)
		try:
			return int(parts)
		except Exception:
			return 0

	def GetVolumeLevel(self, line):
		volume = line.replace("mute_volume_vocals", "")
		volume = volume.replace("mute_volume", "")
		volume = volume.replace("(", "")
		volume = volume.replace(")", "")
		volume = volume.replace("'", "")
		volume = volume.replace("\"", "")
		volume = volume.strip()
		try:
			return int(volume)
		except Exception:
			return -96

	def GuitarDiff(self, raw_line):
		diffs = [0, 139, 176, 221, 267, 333, 409]
		return self.DoDifficulty(self.int_from_dta_string(raw_line), diffs)

	def KeysDiff(self, raw_line):
		diffs = [0, 153, 211, 269, 327, 385, 443]
		return self.DoDifficulty(self.int_from_dta_string(raw_line), diffs)

	def ProBassDiff(self, raw_line):
		diffs = [0, 150, 208, 267, 325, 384, 442]
		return self.DoDifficulty(self.int_from_dta_string(raw_line), diffs)

	def ProGuitarDiff(self, raw_line):
		diffs = [0, 150, 208, 267, 325, 384, 442]
		return self.DoDifficulty(self.int_from_dta_string(raw_line), diffs)

	def ProKeysDiff(self, raw_line):
		diffs = [0, 153, 211, 269, 327, 385, 443]
		return self.DoDifficulty(self.int_from_dta_string(raw_line), diffs)

	def VocalsDiff(self, raw_line):
		diffs = [0, 132, 175, 218, 279, 353, 427]
		return self.DoDifficulty(self.int_from_dta_string(raw_line), diffs)

	def int_from_dta_string(self, string):
		string = self.RemoveDTAComments(string)
		try:
			return int(re.search('\d+', string).group())
		except Exception:
			return -1

	# remove comments
	def RemoveDTAComments(self, raw_line):
		line = raw_line
		index = line.find(';')
		if index > -1:
			line = line[0:index]
		return line.strip()

	def read(self, filepath):
		with open(filepath, 'r', encoding='latin-1') as f:
			data = f.read()
		self.create(data)

	def __init__(self, filepath_or_data=None):
		self.Songs = []
		if isinstance(filepath_or_data, str):
			try:
				self.read(filepath_or_data)
			except FileNotFoundError:
				raise FileNotFoundError('File not found: ' + filepath_or_data)
		elif isinstance(filepath_or_data, bytes):
			self.create(filepath_or_data.decode('latin-1'))

def main(filepath):
	d = DTA(filepath)
	for song in d.Songs:
		for v in sorted(vars(song)):
			if v != 'dta_lines':
				print(v + ':', getattr(song, v))
	
if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument('filepath', type=str, help='Path to file')
	arguments = parser.parse_args()
	main(arguments.filepath)
