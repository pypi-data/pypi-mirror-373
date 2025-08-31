import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['optexaminer2.def', 'optexaminer.def', 'libexmcclib64.dylib']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'EXAMINER2 103011 5 00010203040506070809 0 1 2 LP MIP RMIP NLP MCP DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgenus.run optexaminer.def\ngmsgenux.out\nlibexmcclib64.dylib exm 1 0'
