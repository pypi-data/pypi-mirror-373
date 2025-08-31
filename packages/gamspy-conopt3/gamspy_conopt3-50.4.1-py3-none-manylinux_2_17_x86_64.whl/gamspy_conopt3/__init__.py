import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['libconsub3.so', 'optconopt3.def', 'libconcclib64.so']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'CONOPT3 1 0 CO 1 1 2 LP RMIP NLP CNS DNLP RMINLP QCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibconcclib64.so con 1 1'
