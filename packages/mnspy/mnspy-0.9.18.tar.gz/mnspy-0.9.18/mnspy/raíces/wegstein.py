from mnspy.raíces import Raices
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Wegstein(Raices):
    """Clase para la implementación del cálculo de raíces por el método abierto de Wegstein.

    Attributes
    ----------
    f: callable
        Función a la que se le hallará la raíz.
    x_0: float
        Valor del primer punto inicial.
    x_1: float
        Valor del segundo punto inicial.
    tol: float | int
        Máxima tolerancia del error.
    max_iter: int
        Número máximo de iteraciones permitido.
    tipo_error: str
        Tipo de error a utilizar para la convergencia:
        - ``'%'``: Error relativo porcentual.
        - ``'/'``: Error relativo.
        - ``'n'``: Número de cifras significativas.

    Methods
    -------
    _calcular():
        Realiza los cálculos iterativos del método de Wegstein.
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Genera una gráfica del proceso de búsqueda de la raíz.

    Examples
    -------
    from mnspy import Wegstein

        def f(x):
        return x ** 2 - 9

    we = Wegstein(f, 0, 4, 0.0001, tipo_error="%")
    we.generar_tabla()
    we.graficar()
    we.solucion()

    def f(x):
        return 40 / (x ** 2) - 2 / x

    we = Wegstein(f, 5, 5.001, 0.0001, tipo_error="%")
    we.generar_tabla()
    we.graficar()
    we.solucion()
    """
    def __init__(self, f: callable, x_0: float = 0, x_1: float = 0, tol: float | int = 1e-3, max_iter: int = 20,
                 tipo_error='%'):
        """
        Constructor de la clase Wegstein.

        Parameters
        ----------
        f: callable
            Función a la que se le hallará la raíz.
        x_0: float
            Valor del primer punto inicial.
        x_1: float
            Valor del segundo punto inicial.
        tol: float | int
            Máxima tolerancia del error.
        max_iter: int
            Número máximo de iteraciones permitido.
        tipo_error: str
            Tipo de error a utilizar: ``'%'``, ``'/'`` o ``'n'``.
        """
        # El método de Wegstein es abierto, no requiere x_min y x_max.
        super().__init__(f, None, None, tol, max_iter, tipo_error)
        self._x_0 = self._x_0_i = x_0
        self._x_1 = self._x_1_i = self.x = x_1
        self._calcular()

    def _calcular(self):
        """Calcula la raíz de la función de forma iterativa usando el método de Wegstein.

        Este método es una modificación del método de la secante, a menudo
        utilizado para acelerar la convergencia de iteraciones de punto fijo.

        Returns
        -------
        None
        """
        self.x = (self._x_1_i * self._f(self._x_0_i) - self._x_0_i * self._f(self._x_1_i)) / (
                self._x_1_i - self._x_0_i - self._f(self._x_1_i) + self._f(self._x_0_i))
        self._x_0_i = self._x_1_i
        self._x_1_i = self.x
        if self._fin_iteracion():
            return
        else:
            self._calcular()

    def graficar(self, mostrar_sol: bool = True, mostrar_iter: bool = True, mostrar_lin_iter: bool = True,
                 n_puntos: int = 100):
        """Genera una gráfica del proceso de búsqueda de la raíz por el método de Wegstein.

        Parameters
        ----------
        mostrar_sol: bool
            si es verdadero muestra el punto donde se encontró la solución
            por defecto es True
        mostrar_iter: bool
            si es verdadero muestra los puntos obtenidos de cada iteración
            por defecto es True
        mostrar_lin_iter: bool
            si es verdadero muestra las líneas auxiliares que se usan para obtener la solución
            por defecto es True
        n_puntos: int
            Número de puntos de la gráfica por defecto 100

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        if mostrar_lin_iter and len(self._tabla['x']) > 0:
            plt.axline((0, 0), slope=1, linestyle='-', c='k', lw=2, label='$y=x$')
            l_x = self._tabla['x'].copy()
            l_x.insert(0, self._x_0)
            l_x.insert(1, self._x_1)
            for i, x in enumerate(l_x[1:-1]):
                y = self._f(x)
                x_last = l_x[i]
                x_next = l_x[i + 2]
                plt.plot([x_last, x, x_next], [self._f(x_last), y, x_next], linestyle='dashed', c='purple', lw=1)
                plt.plot([x_next, x_next], [0, self._f(x_next)], linestyle='dashed', c='purple', lw=1)
                plt.plot([x_next, x_next], [0, x_next], linestyle='dashed', c='purple', lw=1)
        plt.title(f'x = {self.x}')
        if self._error_porcentual:
            plt.suptitle('Método de Wegstein (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle('Método de Wegstein (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    """Función principal para demostración."""
    def f(x):
        return x ** 2 - 9

    we = Wegstein(f, 0, 4, 0.0001, tipo_error="%")
    we.generar_tabla()
    we.graficar()
    we.solucion()

    def f(x):
        return 40 / (x ** 2) - 2 / x

    we = Wegstein(f, 5, 5.001, 0.0001, tipo_error="%")
    we.generar_tabla()
    we.graficar()
    we.solucion()


if __name__ == '__main__':
    main()
