#!/usr/bin/env python3
import hashlib
from Crypto.Cipher import AES

common_key = b"\xEB\xE4\x2A\x22\x5E\x85\x93\xE4\x48\xD9\xC5\x45\x73\x81\xAA\xF7"

def check_hash(data, expected_hash):
	return expected_hash == get_hash(data)

def decrypt_bin(data, key, tmd_index):
	tmd_index += b'\0' * 14
	return AES.new(key, AES.MODE_CBC, tmd_index).decrypt(data)

def decrypt_title_key(title_id, title_key):
	title_id += b'\0' * 8
	return AES.new(common_key, AES.MODE_CBC, iv=title_id).decrypt(title_key)

def encrypt_bin(data, key, tmd_index):
	tmd_index += b'\0' * 14
	return AES.new(key, AES.MODE_CBC, tmd_index).encrypt(data)

def get_hash(data):
	return hashlib.sha1(data).digest()
