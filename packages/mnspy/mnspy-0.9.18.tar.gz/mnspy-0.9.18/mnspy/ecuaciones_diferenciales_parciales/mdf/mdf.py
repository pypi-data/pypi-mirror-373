from mnspy.ecuaciones_diferenciales_parciales import EcuacionesDiferencialesParciales
from mnspy.ecuaciones_algebraicas_lineales import Gauss
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class DiferenciasFinitas(EcuacionesDiferencialesParciales):
    """Soluciona la ecuación de Laplace en 2D usando el método de Diferencias Finitas.

    Este método discretiza la ecuación de Laplace en una malla rectangular,
    generando un sistema de ecuaciones algebraicas lineales que se resuelve
    directamente mediante la eliminación de Gauss.

    Attributes
    ----------
    sel: Gauss
        Objeto `Gauss` utilizado para resolver el sistema de ecuaciones lineales.

    Methods
    -------
    _calcular():
        Construye y resuelve el sistema de ecuaciones lineales.
    graficar():
        Genera una gráfica de contorno de la solución.
    graficar_campos():
        Genera una gráfica de vectores para los campos de flujo.

    Examples:
    -------
    from mnspy import DiferenciasFinitas

    df = DiferenciasFinitas((5, 5), {'norte': 100.0, 'sur': 0.0, 'oeste': 75.0, 'este': 50.0}, k_x=2.0)
    df.graficar()
    df.graficar_valores()
    df.graficar_coordenadas()
    """
    def __init__(self, n: int | tuple[int, int], frontera: dict[str, float | str | list[float]], k_x: float = 1.0,
                 k_y: float = 1.0):
        """Constructor de la clase DiferenciasFinitas.

        Parameters
        ----------
        n: int | tuple[int, int]
            Número de divisiones que tendrá la placa, si se ingresa un entero n la placa estará dividida en n x n.
            En caso de que se ingrese una tupla (n, m), la placa estara dividida en n x m
        frontera: dict[str, float | str | list[float]]
            Condiciones de frontera ('norte', 'sur', 'este', 'oeste').
            Los valores pueden ser de tipo ``float`` (Dirichlet), ``list[float]`` (Dirichlet)
            o ``'aislado'`` (Neumann).
        k_x: float, optional
            Coeficiente de conductividad térmica en la dirección x. Por defecto es 1.
        k_y: float, optional
            Coeficiente de conductividad térmica en la dirección y. Por defecto es 1.
        """
        super().__init__(n, frontera, 0.0, k_x, k_y)
        self.sel = None
        self._calcular()

    def _calcular(self):
        """Construye y resuelve el sistema de ecuaciones [A]{x} = {b}.
        """
        # Determina el tamaño del sistema basado en los nodos interiores
        n = self._n - 2
        m = self._m - 2
        if self._frontera['sur'] == 'aislado':
            n += 1
        if self._frontera['norte'] == 'aislado':
            n += 1
        if self._frontera['oeste'] == 'aislado':
            m += 1
        if self._frontera['este'] == 'aislado':
            m += 1
        A = np.zeros((n * m, n * m))

        # Llena la matriz A con el stencil de diferencias finitas para Laplace (5 puntos)
        for i in range(n * m):
            for j in range(n * m):
                if i == j:
                    A[i, j] = 4
                elif j == i + m:
                    A[i, j] = -1
                elif i == j + m:
                    A[i, j] = -1
                elif j == i + 1 and j % m:
                    A[i, j] = -1
                elif j == i - 1 and i % m:
                    A[i, j] = -1

        # Modifica la matriz A y el vector b para las condiciones de frontera
        b = np.zeros(n * m)
        ini_i = ini_j = 1
        if self._frontera['sur'] == 'aislado':
            ini_j = 0
            for i in range(m):
                A[i, m + i] -= 1
        else:
            b[:m] += self._frontera['sur']
        if self._frontera['norte'] == 'aislado':
            for i in range(m):
                A[m * (n - 1) + i, m * (n - 2) + i] -= 1
        else:
            b[m * (n - 1):] += self._frontera['norte']
        if self._frontera['oeste'] == 'aislado':
            ini_i = 0
            for i in range(n):
                A[m * i, m * i + 1] -= 1
        else:
            b[::m] += self._frontera['oeste']
        if self._frontera['este'] == 'aislado':
            for i in range(n):
                A[m * (i + 1) - 1, m * (i + 1) - 2] -= 1
        else:
            b[m - 1::m] += self._frontera['este']

        # Resuelve el sistema lineal
        self.sel = Gauss(np.matrix(A), np.matrix(b).transpose(), True)
        self.sel.ajustar_etiquetas(
            ['T_{' + str(i % m + ini_i) + ',' + str(int(i / m) + ini_j) + '}' for i in range(n * m)],
            es_latex=True)
        # Asigna la solución a la matriz U
        self.U[ini_j:n + ini_j, ini_i:m + ini_i] = self.sel.x.reshape(n, m)
        # Calcula los campos de flujo post-proceso
        self._calcular_campos()

    def graficar(self):
        """Genera una gráfica de contorno de la solución.

        Returns
        -------
        Gráfica de los resultados interpolados usando el pquete matplotlib
        """
        plt.axes().set_aspect('equal')
        plt.suptitle('Método de Diferencias Finitas')
        super()._graficar_datos()

    def graficar_campos(self):
        """Genera una gráfica de vectores para los campos de flujo.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib (quiver plot).
        """
        plt.axes().set_aspect('equal')
        plt.suptitle('Método de Diferencias Finitas')
        super()._graficar_campos()


def main():
    """Función principal para demostración."""
    df = DiferenciasFinitas((5, 5), {'norte': 100.0, 'sur': 0.0, 'oeste': 75.0, 'este': 50.0}, k_x=2.0)
    df.graficar()
    df.graficar_valores()
    df.graficar_coordenadas()


if __name__ == '__main__':
    main()
