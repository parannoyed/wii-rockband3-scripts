#!/usr/bin/env python3
import requests

nus_url = 'http://nus.cdn.shop.wii.com/ccs/download/'

def download(url, filename, progress_string='', add_newline=False):
	url = nus_url + url
	try:
		req = requests.get(url, stream=True)
	except requests.HTTPError:
		raise requests.HTTPError('Not found on server')

	content_length = req.headers.get('content-length')
	if content_length is None:
		return
	else:
		done = 0
		content_length = int(content_length)
		with open(filename, 'wb') as f:
			for chunk in req.iter_content(chunk_size=1024*16):
				if chunk:
					f.write(chunk)
					done += len(chunk)
					percent = int( 100 * done / content_length )
					print('\r[ %s%% ] %s... ' % (percent, progress_string), end='')
	if add_newline == True:
		print('')
