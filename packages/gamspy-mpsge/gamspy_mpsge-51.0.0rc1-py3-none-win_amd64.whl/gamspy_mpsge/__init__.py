import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['mpsgeset', 'gmsge_nt.cmd', 'gmsge_nx.exe', 'mpsgeval.dll', 'gmsgewnt.cmd', 'gmsgewnx.exe']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'MPSGE 100001 5 GE 1 0 1\ngmsgewnt.cmd\ngmsgewnx.exe'
