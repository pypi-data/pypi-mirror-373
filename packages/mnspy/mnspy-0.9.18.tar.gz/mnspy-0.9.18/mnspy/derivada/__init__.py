"""Módulo Derivada - Cálculo Numérico de Derivadas

Este módulo de `mnspy` proporciona herramientas para el cálculo numérico de
derivadas, tanto para funciones continuas como para conjuntos de datos discretos.

Clases Disponibles
------------------
- `Derivada`:
    Calcula derivadas de diferentes órdenes utilizando fórmulas de diferencias
    finitas (hacia adelante, hacia atrás y centradas).
- `Richardson`:
    Implementa la extrapolación de Richardson para mejorar la precisión de las derivadas calculadas.
- `DerivadaDiscreta`:
    Calcula la derivada para un conjunto de puntos (x, y).

"""
from .derivada import Derivada
from .richardson import Richardson
from .derivada_discreta import DerivadaDiscreta
