"""Módulo de Método de Volúmenes Finitos (MVF)

Este submódulo de `mnspy` implementa el Método de Volúmenes Finitos (MVF o FVM
por sus siglas en inglés) para resolver ecuaciones diferenciales parciales,
particularmente ecuaciones de transporte (convección-difusión).

Conceptos Clave
----------------
El MVF discretiza el dominio en un conjunto de volúmenes de control (celdas)
y aplica las leyes de conservación de forma integral sobre cada uno. Es un
método robusto que garantiza la conservación de las propiedades físicas.

- **`Vertice`**: Representa un nodo o esquina en la malla.
- **`Superficie`**: Representa una cara o frontera que delimita un volumen de control.
- **`Celda`**: Representa un volumen de control, el núcleo del método donde se
  realiza el balance de flujos.
- **`VolumenFinito`**: La clase principal que gestiona la malla, ensambla y
  resuelve el sistema de ecuaciones, y realiza el post-proceso.

El módulo también incluye clases para diferentes condiciones de frontera
(`SuperficieDirichlet`, `SuperficieNeumann`, `SuperficieRobin`) y esquemas
de discretización (`Metodo`: CDS, UDS, HDS).

"""

from .mvf import Vertice, Superficie, Celda, SuperficieNeumann, SuperficieDirichlet, SuperficieRobin, Metodo, \
    es_superficie_dirichlet, es_superficie_neumann, es_superficie_robin
from .volumen_finito import VolumenFinito
