"""Paquete ecuaciones_algebraicas_lineales - Métodos numéricos y simulación en Python

El paquete ecuaciones_algebraicas_lineales es un submódulo de mnspy, enfocada en el cálculo de ecuaciones
algebráicas lineales.

"""
from .ecuaciones_algebraicas_lineales import EcuacionesAlgebraicasLineales
from .cramer import Cramer
from .gauss import Gauss
from .gauss_jordan import GaussJordan
from .descomposicion_LU import DescomposicionLU
from .tridiagonal import Tridiagonal
from .descomposicion_cholesky import DescomposicionCholesky
from .gauss_sediel import GaussSediel
