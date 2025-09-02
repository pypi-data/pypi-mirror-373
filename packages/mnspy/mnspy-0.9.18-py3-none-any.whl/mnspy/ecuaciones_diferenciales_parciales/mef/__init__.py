"""Módulo de Método de Elementos Finitos (MEF)

Este submódulo de `mnspy` proporciona una implementación orientada a objetos
del Método de Elementos Finitos (MEF o FEM por sus siglas en inglés) para el
análisis estructural de resortes, barras, armaduras, vigas y marcos.

Conceptos Clave
----------------
- **Nodo**: Representa un punto en la estructura donde se conectan los elementos
  y se aplican cargas o restricciones (soportes).
- **Grado de Libertad (GL)**: Describe la capacidad de un nodo para desplazarse
  o rotar en una dirección específica.
- **Elemento**: Es la unidad básica que, al unirse con otras, conforma la
  estructura completa (ej. `Barra`, `Viga`). Cada elemento tiene asociada una
  matriz de rigidez que relaciona fuerzas y desplazamientos.
- **Ensamble**: Es el proceso de combinar las matrices de rigidez de todos los
  elementos para formar la matriz de rigidez global de la estructura,
  permitiendo resolver el sistema de ecuaciones `[K]{d} = {F}`.

Clases Disponibles
------------------
*   `Nodo`, `Elemento`, `GradoLibertad`, `Rigidez`: Clases base.
*   `Resorte`, `Barra`, `Armadura`, `Viga`, `Marco`: Elementos estructurales 1D.
*   `TriangularCST`: Elemento 2D de deformación constante para problemas de tensión plana.
*   `Ensamble`: Clase principal para construir y analizar la estructura completa.
*   Funciones de utilidad como `mallado_estructurado_triangular` e `importar_gmsh`.

"""
from .mef import Nodo, GradoLibertad, Elemento, Rigidez
from .resorte import Resorte
from .barra import Barra
from .armadura import Armadura
from .viga import Viga
from .marco import Marco
from .triangular_cst import TriangularCST
from .ensamble import Ensamble, mallado_estructurado_triangular, importar_gmsh
