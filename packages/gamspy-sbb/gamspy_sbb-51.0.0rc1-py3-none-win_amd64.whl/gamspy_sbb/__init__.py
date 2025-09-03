import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['optsbb.def', 'gmssb_nt.cmd', 'gmssb_nx.exe']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'SBB 11 5 SB 1 0 1 MINLP MIQCP\ngmssb_nt.cmd\ngmssb_nx.exe'
