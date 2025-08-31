import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['libxprl.dylib', 'libxprs.dylib', 'libscip.dylib', 'libtbb.12.dylib', 'libmosek64.11.0.dylib', 'libmosek64.10.2.dylib', 'libscpcclib64.dylib']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'SCIP 2001 5 SC 1 0 2 MIP NLP CNS DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibscpcclib64.dylib scp 1 1'
