import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['libmosek64.so.11.0', 'libtbb.so.12', 'optmosek.def', 'libmskcclib64.so']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'MOSEK 11 5 MKMBML 1 0 2 LP MIP RMIP NLP DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibmskcclib64.so msk 1 1'
