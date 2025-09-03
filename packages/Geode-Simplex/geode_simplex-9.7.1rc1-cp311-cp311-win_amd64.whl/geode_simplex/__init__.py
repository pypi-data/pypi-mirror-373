## Copyright (c) 2019 - 2025 Geode-solutions

import os, pathlib
os.add_dll_directory(pathlib.Path(__file__).parent.resolve().joinpath('bin'))

from .metric_simplex import *
from .section_simplex import *
from .brep_simplex import *
