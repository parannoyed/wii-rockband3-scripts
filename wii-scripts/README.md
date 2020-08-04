# wii-scripts
Python scripts for building Wii tools

Tested with Python 3.7.3. Your experience may vary with older versions.

## Requires
* pycryptodome (https://pypi.org/project/pycryptodome) 
* requests (https://pypi.org/project/requests/) 

If you're new to python: `pip install pycryptodome` and `pip install requests`

## API

### crypto.py
Convenience crypto variables and functions

`crypto.common_key`
variable `bytes`

`crypto.check_hash(data, expected_hash)`
returns `bool`

`crypto.decrypt_bin(data, key, tmd_index)`
returns decrypted data `bytes`

`crypto.decrypt_title_key(title_id, title_key)`
returns `bytes`

`crypto.encrypt_bin(data, key, tmd_index)`
returns encrypted data `bytes`

`gcrypto.et_hash(data)`
returns SHA1 hash `bytes`

### nus.py
Download file from Nintendo Update Server

`nus.nus_url`
variable `str`

`nus.download(url, filename, progress_string='', add_newline=False)`

### ticket.py
Create, read, write ticket files

TODO document

### tmd.py
Create, read, write title metadata files

TODO document

### util.py
Various convenience functions, classes

TODO document

### wad.py
Create, read, write various packaged files

TODO document

