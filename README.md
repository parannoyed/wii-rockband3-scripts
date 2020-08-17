# wii-rockband3-scripts
Python scripts for Rock Band 3 DLC on Wii

Tested with Python 3.7.3. Your experience may vary with older versions.

## Requires
* pycryptodome (https://pypi.org/project/pycryptodome) 

If you're new to python: `pip install pycryptodome`

## Overview

Put your directories (`000_00000000_songname_meta`, `000_00000000_songname_song`) in `files-unpacked/sZGE`. Run `python add-unpacked.py sZGE` to rename directories and edit `songs.dta`. Using "merged" customs (multiple songs) hasn't been tested and probably isn't working yet.

Run `python unpacked2app.py sZGE` and .app files will be written in `files-app/sZGE`.

Edit `config/console_id.txt`.

Run `python app2bin.py sZGE` and .bin files will be written in `files-bin/sZGE`.

## TODO: proper documentation

### add-unpacked.py

Renames unpacked directories (`000_00000000_songname_meta`, `000_00000000_songname_song`) to correct indexes and modifies songs.dta location (`dlc/sZAE/000/content/songs`) to correct title and index.

Add directories in `files-unpacked/sZXX` (except use the title you want to add: sZGE, sZGP, etc)

Run `python add-unpacked.py sZGE` and directories in `files-unpacked/sZGE` will be renamed and songs.dta modified

### app2bin.py

Packs .app files into .bin files.

In config directory, set `console_id.txt` and `pack.txt`.
Rock Band 2 titles (sZA* to sZI*) use a null key (0000, etc) and Rock Band 3 titles (sZJ* and higher) use your unique PRNG key. Pack and unpack keys should be 16 bits (32 characters).

Copy .app files and title.tmd into `files-app/sZXX` (except use the title you want to pack: sZGE, sZGP, etc)

Run `python app2bin.py sZGE` and .bin files will be written in `files-bin/sZGE`

### unpacked2app.py

Packs directories into .app files.

Copy directories into `files-unpacked/sZXX` (except use the title you want to add: sZGE, sZGP, etc)

Run `python unpacked2app.py sZGE` and .app files will be written in `files-app/sZGE`
