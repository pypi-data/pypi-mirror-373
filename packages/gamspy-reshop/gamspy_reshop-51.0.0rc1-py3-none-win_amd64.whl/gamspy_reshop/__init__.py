import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['reshop.dll', 'embrhpcclib64.dll', 'optreshop.def', 'rhpcclib64.dll']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'RESHOP 103011 5 00010203040506070809 1 0 2 EMP\ngmsgennt.cmd\ngmsgennx.exe\nrhpcclib64.dll rhp 1 1'
