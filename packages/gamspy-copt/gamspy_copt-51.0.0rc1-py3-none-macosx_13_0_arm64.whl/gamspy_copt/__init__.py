import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['libcopt.dylib', 'optcopt.def', 'libcptcclib64.dylib']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'COPT 1011 5 CT 1 0 2 LP MIP RMIP QCP MIQCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibcptcclib64.dylib cpt 1 1'
