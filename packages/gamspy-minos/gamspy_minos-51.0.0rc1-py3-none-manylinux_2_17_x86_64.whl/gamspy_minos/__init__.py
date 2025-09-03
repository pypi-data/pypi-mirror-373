import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['optminos.def', 'libmilcclib64.so']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'MINOS 1 0 M5 1 0 2 LP RMIP NLP CNS DNLP RMINLP QCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibmilcclib64.so mil 1 0'
