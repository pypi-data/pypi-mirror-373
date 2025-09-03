import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['libxprl.dylib', 'libxprs.dylib', 'libgsi.dylib', 'xpauth.xpr', 'optxpress.def', 'libxpxcclib64.dylib']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'XPRESS 11 5 XPXLXSXXXG 1 0 2 LP MIP RMIP NLP CNS DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgenus.run\ngmsgenux.out\nlibxpxcclib64.dylib xpx 1 1'
