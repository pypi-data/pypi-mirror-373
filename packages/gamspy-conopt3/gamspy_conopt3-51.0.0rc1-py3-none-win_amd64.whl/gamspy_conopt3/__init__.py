import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['conopt3.dll', 'optconopt3.def', 'concclib64.dll']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'CONOPT3 1 0 CO 1 1 2 LP RMIP NLP CNS DNLP RMINLP QCP RMIQCP\ngmsgennt.cmd\ngmsgennx.exe\nconcclib64.dll con 1 1'
