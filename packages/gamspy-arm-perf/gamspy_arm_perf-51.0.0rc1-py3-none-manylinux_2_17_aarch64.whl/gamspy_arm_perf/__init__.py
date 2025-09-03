import os
from pathlib import Path
from .version import __version__
directory = str(Path(__file__).resolve().parent)

files = ['libarmpl_gams.so']

file_paths = [directory + os.sep + file for file in files]
