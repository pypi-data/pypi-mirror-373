import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['libreshop.so', 'libembrhpcclib64.so', 'optreshop.def', 'librhpcclib64.so']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'RESHOP 103011 5 00010203040506070809 1 0 2 EMP\ngmsgenus.run\ngmsgenux.out\nlibrhpcclib64.so rhp 1 1'
