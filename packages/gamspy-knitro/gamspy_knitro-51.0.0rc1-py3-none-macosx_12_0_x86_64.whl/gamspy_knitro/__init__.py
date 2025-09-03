import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['libknitro1501.dylib', 'optknitro.def', 'libknxcclib64.dylib']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'KNITRO 103011 5 KN 1 0 2 LP RMIP NLP MCP MPEC RMPEC CNS DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibknxcclib64.dylib knx 1 0'
