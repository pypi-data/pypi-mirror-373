# mnspy: Métodos Numéricos y Simulación en Python

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/mnspy.svg)](https://badge.fury.io/py/mnspy)

`mnspy` es una biblioteca de Python desarrollada con fines didácticos para facilitar la enseñanza y el aprendizaje de métodos numéricos. Fue creada como herramienta de apoyo para la asignatura de **Métodos Numéricos y Simulación** del programa de Ingeniería Mecánica en la **Universidad Pontificia Bolivariana, Seccional Bucaramanga**.

La biblioteca implementa algoritmos numéricos fundamentales utilizando un enfoque orientado a objetos, lo que permite una comprensión más clara de los conceptos teóricos y su aplicación práctica. Además, incluye herramientas de visualización para interpretar mejor los resultados.

## Características Principales

- **Enfoque Orientado a Objetos**: Cada método numérico es una clase, facilitando su uso y comprensión.
- **Visualización Integrada**: Métodos de graficación incorporados que utilizan `matplotlib` para visualizar los procesos y resultados.
- **Código Didáctico**: El código fuente está documentado exhaustivamente para ser una referencia de aprendizaje.
- **Amplia Cobertura**: Abarca desde la búsqueda de raíces hasta la solución de Ecuaciones Diferenciales Parciales con métodos avanzados como MEF y MVF.

## Instalación

Puedes instalar `mnspy` a través de pip:

```bash
pip install mnspy
```


## Dependencias

`mnspy` se basa en varias bibliotecas científicas y de visualización de Python. Las principales dependencias, que se instalan automáticamente, son:

- **`NumPy`** y **`SciPy`**: Para el manejo de arrays, operaciones matriciales y algoritmos numéricos subyacentes.
- **`SymPy`**: Para la manipulación de expresiones simbólicas.
- **`Matplotlib`**: Para la generación de todas las gráficas.
- **`Tabulate`**: Para la presentación de tablas de resultados.
- **`IPython`**: Para la visualización enriquecida en notebooks de Jupyter.
- **`Pandas`**: Para la manipulación de datos.
- **`Gmsh`**: Para la importación de mallas en el módulo de elementos finitos.

## Módulos Disponibles

La biblioteca se organiza en los siguientes módulos:

- **`raíces`**: Métodos para encontrar raíces de ecuaciones no lineales (Bisección, Newton-Raphson, Secante, etc.).
- **`ecuaciones_algebraicas_lineales`**: Algoritmos para resolver sistemas de ecuaciones lineales (Gauss, Gauss-Jordan, Descomposición LU, etc.).
- **`interpolación`**: Técnicas de interpolación polinómica (Newton, Lagrange) y por Trazadores (Splines).
- **`integrales`**: Métodos para la integración numérica (Trapecio, Simpson, Romberg, Gauss-Legendre).
- **`derivada`**: Cálculo numérico de derivadas usando diferencias finitas y extrapolación de Richardson.
- **`ecuaciones_diferenciales_ordinarias` (EDOs)**: Solucionadores para problemas de valor inicial (Euler, Heun, Runge-Kutta).
- **`ecuaciones_diferenciales_parciales` (EDPs)**: Solucionadores para EDPs, organizados en:
    - **`mdf` (Método de Diferencias Finitas)**: Para problemas en mallas rectangulares.
    - **`mef` (Método de Elementos Finitos)**: Para análisis estructural de resortes, barras, vigas, armaduras, marcos y problemas 2D con elementos triangulares (CST).
    - **`mvf` (Método de Volúmenes Finitos)**: Para problemas de transporte (convección-difusión) basados en la conservación.

## Ejemplos de Uso

Para ver ejemplos detallados y cuadernos de Jupyter que demuestran el uso de los diferentes módulos, por favor visita el repositorio público de ejemplos:

[**mnspy_notebooks en GitHub**](https://github.com/EdwinSoft/mnspy_notebooks)

## Licencia

Este proyecto está bajo la Licencia MIT.
