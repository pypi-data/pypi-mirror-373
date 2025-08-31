import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['optcbc.def', 'cbccclib64.dll']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'CBC 2011 5 00010203040506070809 1 0 2 LP MIP RMIP\ngmsgennt.cmd\ngmsgennx.exe\ncbccclib64.dll cbc 1 0'
