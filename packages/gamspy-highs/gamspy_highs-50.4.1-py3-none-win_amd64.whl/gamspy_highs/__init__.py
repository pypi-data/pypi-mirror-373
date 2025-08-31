import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['opthighs.def', 'hiscclib64.dll']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'HIGHS 11 5 HI 1 0 2 LP MIP RMIP\ngmsgennt.cmd\ngmsgennx.exe\nhiscclib64.dll his 1 0'
