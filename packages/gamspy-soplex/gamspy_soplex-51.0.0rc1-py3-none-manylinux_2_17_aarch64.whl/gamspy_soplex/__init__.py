import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['libtbb64.so', 'libospcclib64.so']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'SOPLEX 11 5 SC 1 0 2 LP RMIP\ngmsgenus.run\ngmsgenux.out\nlibospcclib64.so osp 1 1'
