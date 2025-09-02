"""Módulo Ecuaciones Diferenciales Parciales (EDPs)

Este módulo de `mnspy` proporciona herramientas para resolver ecuaciones
diferenciales parciales (EDPs) elípticas, comúnmente encontradas en problemas
de ingeniería en estado estacionario (ej. Ecuación de Laplace, Ecuación de Poisson).

Submódulos Disponibles
----------------------
- `mdf` (Método de Diferencias Finitas):
    Aproxima las derivadas parciales en una rejilla de puntos (nodos),
    transformando la EDP en un sistema de ecuaciones algebraicas lineales.
    - `DiferenciasFinitas`: Implementa el método de diferencias finitas para mallas rectangulares.
    - `Liebmann`: Solucionador iterativo (Gauss-Seidel con sobrerrelajación) para la ecuación de Laplace.

- `mef` (Método de Elementos Finitos):
    Discretiza el dominio en subdominios más pequeños (elementos) y aproxima
    la solución dentro de cada uno. Es muy flexible para geometrías complejas.

- `mvf` (Método de Volúmenes Finitos):
    Discretiza el dominio en volúmenes de control y aplica las leyes de
    conservación de forma integral sobre cada volumen. Es robusto y garantiza
    la conservación de las propiedades.
"""
from .ecuaciones_diferenciales_parciales import EcuacionesDiferencialesParciales
from .liebmann import Liebmann
