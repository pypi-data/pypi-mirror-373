import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['baron', 'libbaronnavvy64.so', 'optbaron.def', 'gmsba_us.run', 'gmsba_ux.out']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'BARON 1001 5 BA 1 0 1 LP MIP RMIP NLP CNS DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsba_us.run\ngmsba_ux.out'
