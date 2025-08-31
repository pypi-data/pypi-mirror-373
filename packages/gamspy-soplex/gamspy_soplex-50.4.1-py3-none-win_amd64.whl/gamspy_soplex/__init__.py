import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['tbb12.dll', 'ospcclib64.dll']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'SOPLEX 11 5 SC 1 0 2 LP RMIP\ngmsgennt.cmd\ngmsgennx.exe\nospcclib64.dll osp 1 1'
