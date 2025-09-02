"""Módulo Raíces - Métodos para Encontrar Raíces de Ecuaciones

Este módulo de `mnspy` proporciona una colección de algoritmos numéricos para
encontrar las raíces de ecuaciones no lineales de una variable.

Incluye tanto métodos cerrados (que requieren un intervalo inicial donde
exista un cambio de signo) como métodos abiertos (que requieren uno o más
puntos iniciales).

Clases Disponibles
------------------
- `Raices`: Clase base abstracta de la que heredan todos los métodos.
- `Biseccion`: Implementación del método de bisección.
- `FalsaPosicion`: Implementación del método de la falsa posición.
- `Brent`: Implementación del método de Brent, que combina bisección, secante y cuadratica inversa.
- `PuntoFijo`: Implementación del método de iteración de punto fijo.
- `NewtonRaphson`: Implementación del método de Newton-Raphson.
- `Secante`: Implementación del método de la secante.
- `SecanteModificada`: Variante del método de la secante que no requiere dos puntos iniciales.
- `Muller`: Implementación del método de Müller (interpolación cuadrática).
- `Wegstein`: Implementación del método de Wegstein.

"""
from .raices import Raices
from .bisección import Biseccion
from .brent import Brent
from .falsa_posicion import FalsaPosicion
from .newton_raphson import NewtonRaphson
from .punto_fijo import PuntoFijo
from .secante import Secante
from .secante_modificada import SecanteModificada
from .wegstein import Wegstein
from .muller import Muller
