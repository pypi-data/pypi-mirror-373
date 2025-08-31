import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['optexaminer.def', 'libex_cclib64.dylib']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'EXAMINER 103011 5 00010203040506070809 0 0 2 LP MIP RMIP NLP MCP MPEC RMPEC DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibex_cclib64.dylib ex_ 2 0'
