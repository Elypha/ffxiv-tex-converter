## Required python libraries

    pip install kaitaistruct
    pip install numpy
    pip install tqdm

---
## run.py
```
ffxiv-tex-converter, FFXIV TEX FILE CONVERTER

options:
  -h, --help            show this help message and exit
  --directory -D, -d -D
                        Initial directory to be processed.
  --command -C, -c -C   dds-to-tex, tex-to-dds
  --parallel, --no-parallel, -p
                        multicore processing
  --multiplier -M, -m -M
                        if using multicore processing, job multiplier per core. default = 5
```
* Accepts nested directory structures.
* Supports BGRA, BGRX, BC1 (DXT1), BC2 (DXT3), BC3 (DXT5), and BC7, A8, L8, BGRA4. 

### Usage examples:

**given directory "dog" has dds files I want to convert to FFXIV tex files.**

Run this command: `python run.py -d dog -c dds-to-tex`

I want to run it faster: `python run.py -d dog -c dds-to-tex -p -m 10`

It will output to **"dog_tex"** directory.

**given directory "cat" has FFXIV tex files I want to convert to DDS files.**

Run this command: `python run.py -d cat -c tex-to-dds`

I want to run it faster: `python run.py -d cat -c tex-to-dds -p -m 10`

It will output to **"cat_dds"** directory.

### Why should I use this over TexTools?
* TexTools breaks mipmaps. Either by falsely calculating the offset, or just erasing the end of the file.
* TexTools doesn't support writing many files at once.
* Textools can't interact with most game textures. TexTools only interacts with character and housing textures.

### When should I use TexTools Texture Importer?
* If mipmaps don't bother you, go ahead.
* If you want to write directly to the game files. Please don't.
* If you are working on a file, and you want to immediately see results USE PENUMBRA IMPORT.

### Penumbra Import
* Penumbra also has a BC7/BC3/BGRA8 import
* Use this if you don't need to batch convert or use an esoteric file type.

I personally still use TexTools for a lot of stuff. Please don't perpetuate cultish behavior around mod tools. It's weird.



# parsers

### dds.ksy

* kaitai struct to read dds header, body. body reading is only rudimentary to reach EOF.
* Read [Microsoft DDS_Header Docs](https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-header) for more info.

### dds.py

* kaitai generated parser of dds for python. I did have to modify some Enum to be IntFlag instead, as the compiler did
  not do that for me. Just an FYI if you re-compile the dds.ksy for python you might have to redo that.
* Read [Microsoft DDS_Header Docs](https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-header) for more info.

### tex.ksy

* kaitai struct to read tex header, body. body reading is only rudimentary to reach EOF.
* See Penumbra/TexTools/Lumina source code for more info.

### tex.py

*same as the dds.py info really.
