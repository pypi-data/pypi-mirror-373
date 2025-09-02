from mnspy.ecuaciones_diferenciales_parciales import EcuacionesDiferencialesParciales
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Liebmann(EcuacionesDiferencialesParciales):
    """Soluciona la ecuación de Laplace en 2D usando el método de Liebmann.

    Este método es una implementación del método de Gauss-Seidel para resolver
    el sistema de ecuaciones lineales que resulta de discretizar la ecuación
    de Laplace mediante diferencias finitas. Incluye un factor de
    sobrerrelajación (lambda) para acelerar la convergencia.

    Attributes
    ----------
    converge: bool
        Indica si el método convergió dentro de la tolerancia y el número
        máximo de iteraciones.
    factor_lambda: float
        Factor de sobrerrelajación utilizado en los cálculos.
    iter: int
        Número de iteraciones realizadas.
    iter_max: int
        Máximo número de iteraciones permitidas.
    tol_porc: float
        Tolerancia de error porcentual para el criterio de parada.

    Methods
    -------
    _calcular():
        Ejecuta el algoritmo iterativo de Liebmann.
    graficar():
        Genera una gráfica de contorno de la solución.
    graficar_campos():
        Genera una gráfica de vectores para los campos de flujo.

    Examples:
    -------
    from mnspy import Liebmann

    lp = Liebmann((10, 10), {'norte': 80.0, 'sur': 20.0, 'oeste': 20.0, 'este': 0.0}, 5, tol_porc=1)
    lp.graficar()
    lp.graficar_campos()

    """
    def __init__(self, n: int | tuple[int, int], frontera: dict[str, float | str | list[float]], val_inicial: float,
                 tol_porc: float = 0.1, factor_lambda: float = 1, iter_max: int = 200, k_x: float = 1, k_y: float = 1):
        """Constructor de la clase Liebmann

        Parameters
        ----------
        n: int | tuple[int, int]
            Número de nodos en cada dirección. Si es un entero, la malla será de
            n x n. Si es una tupla (n_filas, n_columnas), la malla será de
            n_filas x n_columnas.
        frontera: dict[str, float | str | list[float]]
            Condiciones de frontera de la placa ('norte', 'sur', 'este', 'oeste').
            Los valores pueden ser de tipo ``float`` (Dirichlet), ``list[float]`` (Dirichlet)
            o ``'aislado'`` (Neumann).
        val_inicial: float
            Valor inicial para todos los nodos interiores de la malla.
        tol_porc: float, optional
            Tolerancia porcentual de error para el criterio de parada. Por defecto es 0.1.
        factor_lambda: float, optional
            Factor de sobrerrelajación (1 <= lambda < 2). Por defecto es 1 (Gauss-Seidel).
        iter_max: int, optional
            Número máximo de iteraciones. Por defecto es 200.
        k_x: float, optional
            Coeficiente de conductividad térmica en la dirección x. Por defecto es 1.
        k_y: float, optional
            Coeficiente de conductividad térmica en la dirección y. Por defecto es 1.
        """
        super().__init__(n, frontera, val_inicial, k_x, k_y)
        self.iter_max = iter_max
        self.factor_lambda = factor_lambda
        self.tol_porc = tol_porc
        self.converge = True
        self.iter = 0
        self._calcular()

    def _calcular(self):
        """Ejecuta los cálculos iterativos del método de Liebmann.
        """
        for k in range(self.iter_max):
            self.iter = k + 1
            self.converge = True
            # Manejo de fronteras de Neumann (aisladas)
            if self._frontera['norte'] == 'aislado':
                self.U[self._n - 1, 1:self._m - 1] = (self.U[self._n - 2, 1:self._m - 1] / 2 +
                                                       self.U[self._n - 1, :self._m - 2] / 4 + self.U[self._n - 1,
                                                                                          2:self._m] / 4)
                self.q_x[self._n - 1, 1:self._m - 1] = -(self.U[self._n - 1, 2:self._m] - self.U[self._n - 1,
                                                                                      :self._m - 2]) / 2
            if self._frontera['sur'] == 'aislado':
                self.U[0, 1:self._m - 1] = (self.U[1, 1:self._m - 1] / 2 + self.U[0, :self._m - 2] / 4 +
                                             self.U[0, 2:self._m] / 4)
                self.q_x[0, 1:self._m - 1] = -(self.U[0, 2:self._m] - self.U[0, :self._m - 2]) / 2

            if self._frontera['oeste'] == 'aislado':
                self.U[1:self._n - 1, 0] = (
                        self.U[1:self._n - 1, 1] / 2 + self.U[2:self._n, 0] / 4 + self.U[:self._n - 2, 0] / 4)
                self.q_y[1:self._n - 1, 0] = -(self.U[2:self._n, 0] - self.U[:self._n - 2, 0]) / 2

            if self._frontera['este'] == 'aislado':
                self.U[1:self._n - 1, self._m - 1] = (
                        self.U[1:self._n - 1, self._m - 2] / 2 + self.U[2:self._n, self._m - 1] / 4 + self.U[
                                                                                                  :self._n - 2,
                                                                                                        self._m - 1] / 4)
                self.q_y[1:self._n - 1, self._m - 1] = -(self.U[2:self._n, self._m - 1] - self.U[:self._n - 2,
                                                                                            self._m - 1]) / 2
            # Itera sobre los nodos interiores
            for i in range(1, self._n - 1):
                for j in range(1, self._m - 1):
                    last_val = self.U[i, j]
                    # Fórmula de Liebmann (Gauss-Seidel con sobrerrelajación)
                    self.U[i, j] = self.factor_lambda * (
                            self.U[i + 1, j] + self.U[i - 1, j] + self.U[i, j + 1] + self.U[i, j - 1]) / 4 + (
                                           1 - self.factor_lambda) * last_val
                    # Verifica la convergencia
                    if self.U[i, j] != 0.0:
                        cumple = abs((self.U[i, j] - last_val) / self.U[i, j]) < self.tol_porc / 100.0
                    else:
                        cumple = False
                    self.converge = self.converge and cumple
            if self.converge:
                break
        self._calcular_campos()

    def graficar(self):
        """Genera una gráfica de contorno de la solución.

        Returns
        -------
        Gráfica de los resultados interpolados usando el pquete matplotlib
        """
        plt.axes().set_aspect('equal')
        plt.suptitle('Método de Liebmann')
        if self.converge:
            plt.title(f'Tolerancia= {self.tol_porc} %, N iteraciones= {self.iter}')
        else:
            plt.title(f'No converge, N iteraciones= {self.iter}')
        super()._graficar_datos()

    def graficar_campos(self):
        """Genera una gráfica de vectores para los campos de flujo.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib (quiver plot).
        """
        plt.axes().set_aspect('equal')
        plt.suptitle('Método de Liebmann')
        super()._graficar_campos()


def main():
    """Función principal para demostración."""
    lp = Liebmann((10, 10), {'norte': 80.0, 'sur': 20.0, 'oeste': 20.0, 'este': 0.0}, 5, tol_porc=1)
    lp.graficar()
    lp.graficar_campos()


if __name__ == '__main__':
    main()
