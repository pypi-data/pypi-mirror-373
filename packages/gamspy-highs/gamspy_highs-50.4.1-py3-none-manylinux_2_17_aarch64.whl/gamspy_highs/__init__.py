import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['opthighs.def', 'libhiscclib64.so']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'HIGHS 11 5 HI 1 0 2 LP MIP RMIP\ngmsgenus.run\ngmsgenux.out\nlibhiscclib64.so his 1 1'
