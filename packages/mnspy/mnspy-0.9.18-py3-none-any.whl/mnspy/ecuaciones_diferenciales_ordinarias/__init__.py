"""Módulo Ecuaciones Diferenciales Ordinarias (EDOs)

Este módulo de `mnspy` proporciona una colección de métodos numéricos para
resolver problemas de valor inicial para ecuaciones diferenciales ordinarias (EDOs).

Los métodos implementados son adecuados para resolver EDOs de primer orden de la
forma `dy/dx = f(x, y)`.

Clases Disponibles
------------------
- `EcuacionesDiferencialesOrdinarias`:
    Clase base abstracta de la que heredan todos los solucionadores de EDOs.
- `Euler`:
    Implementación del método de Euler, el método explícito más simple.
- `Heun`:
    Implementación del método de Heun, un método predictor-corrector simple.
- `PuntoMedio`:
    Implementación del método del punto medio (RK2 modificado).
- `RungeKutta`:
    Implementación de los métodos clásicos de Runge-Kutta de órdenes 2, 3, 4 y 5.

"""
from .ecuaciones_diferenciales_ordinarias import EcuacionesDiferencialesOrdinarias
from .euler import Euler
from .heun import Heun
from .punto_medio import PuntoMedio
from .runge_kutta import RungeKutta
