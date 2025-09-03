import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['optdicopt.def', 'gmsdi_us.run', 'gmsdi_ux.out']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'DICOPT 1 5 DI 1 0 1 MINLP MIQCP\ngmsdi_us.run\ngmsdi_ux.out'
