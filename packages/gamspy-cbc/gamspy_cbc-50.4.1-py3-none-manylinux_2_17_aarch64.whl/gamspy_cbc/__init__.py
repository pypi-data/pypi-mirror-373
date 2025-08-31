import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['optcbc.def', 'libcbccclib64.so']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'CBC 2011 5 00010203040506070809 1 0 2 LP MIP RMIP\ngmsgenus.run\ngmsgenux.out\nlibcbccclib64.so cbc 1 0'
