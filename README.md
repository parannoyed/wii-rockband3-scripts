# wii-rockband3-scripts
Python scripts for Rock Band 3 DLC on Wii

Tested with Python 3.7.3. Your experience may vary with older versions.

## Requires
* pycryptodome (https://pypi.org/project/pycryptodome) 

If you're new to python: `pip install pycryptodome`


## TODO: proper documentation

### add-unpacked.py

Renames unpacked directories (`000_00000000_songname_meta`, `000_00000000_songname_song`) to correct indexes and modifies songs.dta location (`dlc/sZAE/000/content/songs`) to correct title and index.

Add directories in `files-unpacked/sZXX` (except use the title you want to add: sZGE, sZGP, etc)

Run packer `python add-unpacked.py sZGE` and directories in `files-unpacked/sZGE` will be renamed and songs.dta modified

### app2bin.py

In config directory, set `console_id.txt` and `pack.txt`.
Rock Band 2 titles use a null key (0000, etc) and Rock Band 3 titles use your unique PRNG key. Key must be 16 bits (32 characters).

Copy .app files and title.tmd into `files-app/sZXX` (except use the title you want to pack: sZGE, sZGP, etc)

Run packer `python app2bin.py sZGE` and .bin files will be written in `files-bin/sZGE`
