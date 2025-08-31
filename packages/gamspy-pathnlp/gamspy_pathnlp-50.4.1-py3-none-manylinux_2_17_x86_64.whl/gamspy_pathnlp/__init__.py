import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['optpathnlp.def', 'gmsptnus.run', 'gmsptnux.out']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'PATHNLP 11 5 PT 1 0 1 LP RMIP NLP DNLP RMINLP QCP RMIQCP\ngmsptnus.run\ngmsptnux.out'
