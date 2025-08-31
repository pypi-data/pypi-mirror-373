import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['grbgetkey.exe', 'grbprobe.exe', 'optgurobi.def', 'grbcclib64.dll']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'GUROBI 11 5 GUGLGD 1 0 2 LP MIP RMIP NLP DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgennt.cmd\ngmsgennx.exe\ngrbcclib64.dll grb 1 1'
