from .geometry3D import Geometry3D
#from .geometry3D_bk import Geometry3D
from .geometry2D import Geometry2D
from .boundary_conditions import BoundaryConditions
from .visualizer import plot2D as Plot2D
from .visualizer import movie as Movie2D#
from .projection import projection
from .fourier import Fourier
from .bte import BTE
import os
import jax


jax.config.update("jax_enable_x64",True)
jax.config.update("jax_log_compiles",0)

__version__ = "0.64.45"
