"""Módulo Integrales - Integración Numérica

Este módulo de `mnspy` implementa varios métodos para la integración numérica,
tanto para funciones definidas analíticamente como para conjuntos de datos discretos.

Clases Disponibles
------------------
- `Integral`:
    Clase base para todos los métodos de integración.
- `Trapezoidal`:
    Implementa la regla del trapecio para funciones.
- `Simpson13`:
    Implementa la regla de Simpson 1/3 para funciones.
- `Simpson38`:
    Implementa la regla de Simpson 3/8 para funciones.
- `Romberg`:
    Implementa la integración de Romberg para mejorar la precisión de la regla del trapecio.
- `GaussLegendre`:
    Implementa la cuadratura de Gauss-Legendre.
- `CuadraturaAdaptativa`:
    Implementa un método de cuadratura adaptativa basado en la regla de Simpson.
- `TrapezoidalDesigual`:
    Aplica la regla del trapecio a datos con espaciado no uniforme.
- `TrapezoidalDesigualAcumulado`:
    Calcula la integral acumulada para datos con espaciado no uniforme.

"""
from .integral import *
from .trapezoidal import *
from .trapezoidal_desigual import *
from .simpson_1_3 import Simpson13
from .simpson_3_8 import Simpson38
from .trapezoidal_desigual_acumulado import TrapezoidalDesigualAcumulado
from .romberg import Romberg
from .gauss_legendre import GaussLegendre
from .cuadratura_adaptativa import CuadraturaAdaptativa
