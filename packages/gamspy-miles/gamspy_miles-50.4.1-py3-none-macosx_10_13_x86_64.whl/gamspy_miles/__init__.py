import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['optmiles.def', 'gmsmceus.run', 'gmsmceux.out']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'MILES 103001 5 00010203040506070809 1 0 1 MCP\ngmsmceus.run\ngmsmceux.out'
