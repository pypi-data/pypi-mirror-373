import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['xprs.dll', 'gsi.dll', 'xprl.dll', 'xpauth.xpr', 'optxpress.def', 'xpxcclib64.dll']

file_paths = [directory + os.sep + file for file in files]
verbatim = 'XPRESS 11 5 XPXLXSXXXG 1 0 2 LP MIP RMIP NLP CNS DNLP RMINLP MINLP QCP MIQCP RMIQCP\ngmsgennt.cmd\ngmsgennx.exe\nxpxcclib64.dll xpx 1 1'
