# wii-rockband3-scripts
Python scripts for Rock Band 3 DLC on Wii

Tested with Python 3.7.3. Your experience may vary with older versions.

## Requires
* pycryptodome (https://pypi.org/project/pycryptodome) 

If you're new to python: `pip install pycryptodome`


## TODO: proper documentation


### pack.py

In config directory, set `console_id.txt` and `pack.txt`.
Rock Band 2 titles use a null key (0000, etc) and Rock Band 3 titles use your unique PRNG key.

Copy .app files and title.tmd into `files-app/sZXX` (except use the title you want to pack: sZGE, sZGP, etc)

Run packer `python pack.py sZGE` and .bin files will be written in `files-bin/sZGE`
