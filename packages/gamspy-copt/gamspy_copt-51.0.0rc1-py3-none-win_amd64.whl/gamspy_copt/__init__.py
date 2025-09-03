import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['copt.dll', 'optcopt.def', 'cptcclib64.dll']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'COPT 1011 5 CT 1 0 2 LP MIP RMIP QCP MIQCP RMIQCP\ngmsgennt.cmd\ngmsgennx.exe\ncptcclib64.dll cpt 1 1'
