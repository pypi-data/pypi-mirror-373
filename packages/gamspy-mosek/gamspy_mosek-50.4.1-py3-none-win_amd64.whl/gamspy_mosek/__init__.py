import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['mosek64_11_0.dll', 'tbb12.dll', 'optmosek.def', 'mskcclib64.dll']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'MOSEK 11 5 MKMBML 1 0 2 LP MIP RMIP NLP DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgennt.cmd\ngmsgennx.exe\nmskcclib64.dll msk 1 1'
