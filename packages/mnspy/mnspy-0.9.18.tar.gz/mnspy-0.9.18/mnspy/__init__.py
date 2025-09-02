"""
mnspy: Métodos Numéricos y Simulación en Python.

`mnspy` es una biblioteca de Python desarrollada con fines didácticos para facilitar
la enseñanza y el aprendizaje de métodos numéricos y simulación a estudiantes
de ingeniería.

La biblioteca implementa algoritmos numéricos fundamentales utilizando un enfoque
orientado a objetos, lo que permite una comprensión más clara de los conceptos
teóricos.

Módulos Principales
-------------------
La biblioteca se organiza en los siguientes módulos, cada uno enfocado en un área
específica de los métodos numéricos:

- `raíces`:
    Métodos para encontrar las raíces de ecuaciones no lineales.
- `ecuaciones_algebraicas_lineales`:
    Algoritmos para resolver sistemas de ecuaciones lineales.
- `interpolación`:
    Técnicas de interpolación polinómica.
- `integrales`:
    Métodos para la integración numérica de funciones.
- `derivada`:
    Cálculo numérico de derivadas.
- `ecuaciones_diferenciales_ordinarias` (EDOs):
    Solucionadores para ecuaciones diferenciales ordinarias.
- `ecuaciones_diferenciales_parciales` (EDPs):
    Solucionadores para ecuaciones diferenciales parciales, incluyendo:
    - Método de Diferencias Finitas (`mdf`)
    - Método de Elementos Finitos (`mef`)
    - Método de Volúmenes Finitos (`mvf`)
- `utilidades`:
    Funciones y clases auxiliares utilizadas en toda la biblioteca.

`mnspy` está diseñado para ser una herramienta de apoyo que permita a los
estudiantes visualizar y experimentar con los algoritmos, reforzando así su
comprensión de los principios de la simulación científica.
"""
from .derivada import *
from .ecuaciones_diferenciales_ordinarias import *
from .ecuaciones_diferenciales_parciales import *
from .ecuaciones_diferenciales_parciales.mdf import *
from .ecuaciones_diferenciales_parciales.mef import *
from .ecuaciones_diferenciales_parciales.mvf import *
from .ecuaciones_algebraicas_lineales import *
from .integrales import *
from .interpolación import *
from .raíces import *
from .utilidades import *
