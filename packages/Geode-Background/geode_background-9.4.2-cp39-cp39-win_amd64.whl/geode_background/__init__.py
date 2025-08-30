## Copyright (c) 2019 - 2025 Geode-solutions

import os, pathlib
os.add_dll_directory(pathlib.Path(__file__).parent.resolve().joinpath('bin'))

from .brep_background import *
from .common_background import *
from .surface_background import *
from .solid_background import *
