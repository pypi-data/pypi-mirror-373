"""Módulo Interpolación - Métodos de Ajuste de Curvas

Este módulo de `mnspy` proporciona una colección de métodos para la
interpolación de datos. La interpolación es una técnica para estimar valores
desconocidos que se encuentran entre puntos de datos conocidos.

Se incluyen tanto métodos polinómicos globales (que usan todos los puntos para
crear un único polinomio) como métodos de trazadores (splines), que ajustan
polinomios por tramos entre los puntos.

Clases Disponibles
------------------
- `Interpolacion`: Clase base para todos los métodos de interpolación.
- `InterpolacionNewton`: Interpolación polinómica de Newton (diferencias divididas).
- `InterpolacionLagrange`: Interpolación polinómica de Lagrange.
- `SplineLineal`: Trazadores lineales que conectan puntos con rectas.
- `SplineCubica`: Trazadores cúbicos que aseguran la suavidad en las uniones.

"""
from .interpolacion import Interpolacion
from .inter_Newton import InterpolacionNewton
from .inter_Lagrange import InterpolacionLagrange
from .inter_spline_lineal import SplineLineal
from .inter_spline_cubica import SplineCubica
