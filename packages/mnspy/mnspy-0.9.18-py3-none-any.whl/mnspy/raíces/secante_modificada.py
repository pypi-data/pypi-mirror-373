from mnspy.raíces import Raices
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class SecanteModificada(Raices):
    """Clase para la implementación del cálculo de raíces por el método abierto de la Secante Modificada.

    Attributes
    ----------
    f: callable
        Función a la que se le hallará la raíz.
    x: float
        Valor de x inicial.
    delta: float
        Pequeña fracción de x utilizada para aproximar la derivada.
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
        Realiza los cálculos iterativos del método de la Secante Modificada.
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Genera una gráfica del proceso de búsqueda de la raíz.

    Examples
    -------
    from mnspy import SecanteModificada

        def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    se = SecanteModificada(f, 0.2, delta=0.1, tol=0.01, tipo_error="%")
    se.generar_tabla()
    se.graficar()
    se.solucion()
    """
    def __init__(self, f: callable, x: float = 0, delta: float = 1e-6, tol: float | int = 1e-3, max_iter: int = 20,
                 tipo_error='%'):
        """
        Constructor de la clase SecanteModificada.

        Parameters
        ----------
        f: callable
            Función a la que se le hallará la raíz.
        x: float
            Valor de x inicial.
        delta: float
            Pequeña fracción de x para aproximar la derivada.
        tol: float | int
            Máxima tolerancia del error.
        max_iter: int
            Número máximo de iteraciones permitido.
        tipo_error: str
            Tipo de error a utilizar: ``'%'``, ``'/'`` o ``'n'``.
        """
        # El método es abierto, no requiere x_min y x_max.
        super().__init__(f, None, None, tol, max_iter, tipo_error)
        self._x_0 = self.x = x
        self._delta = delta
        self._calcular()

    def _calcular(self):
        """Calcula la raíz de la función de forma iterativa usando el método de la Secante Modificada.

        Este método aproxima la derivada utilizando una pequeña perturbación `delta`,
        similar a una diferencia finita.

        Returns
        -------
        None
        """
        self.x -= (self._f(self.x) * self._delta) / (
                self._f(self.x + self._delta) - self._f(self.x))
        if self._fin_iteracion():
            return
        else:
            self._calcular()

    def graficar(self, mostrar_sol: bool = True, mostrar_iter: bool = True, mostrar_lin_iter: bool = True,
                 n_puntos: int = 100):
        """Genera una gráfica del proceso de búsqueda de la raíz por el método de la Secante Modificada.

        Parameters
        ----------
        mostrar_sol: bool, optional
            Si es ``True``, muestra el punto de la solución final. Por defecto es ``True``.
        mostrar_iter: bool, optional
            Si es ``True``, muestra los puntos de cada iteración. Por defecto es ``True``.
        mostrar_lin_iter: bool
            Si es ``True``, muestra las líneas secantes utilizadas en cada iteración. Por defecto es ``True``.
        n_puntos: int, optional
            Número de puntos para dibujar la curva de la función. Por defecto es 100.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        if mostrar_lin_iter and len(self._tabla['x']) > 0:
            # fun = vectorize(self.f)
            l_x = self._tabla['x'].copy()
            l_x.insert(0, self._x_0)
            for i, x in enumerate(l_x[:-1]):
                y = self._f(x)
                x_next = l_x[i + 1]
                derivada_aprox = (self._f(x + self._delta) - self._f(x)) / self._delta
                plt.axline((x, y), slope=derivada_aprox, linestyle='dashed',
                           c='purple',
                           lw=1)
                plt.plot([x_next, x_next], [0, self._f(x_next)], linestyle='dashed', c='purple', lw=1)
        plt.title(f'x = {self.x}')
        if self._error_porcentual:
            plt.suptitle(
                r'Método de la Secante Modificada, $\delta$ = ' + str(self._delta) + ' (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle(
                r'Método de la Secante Modificada, $\delta$ = ' + str(self._delta) + ' (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    """Función principal para demostración."""
    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    se = SecanteModificada(f, 0.2, delta=0.1, tol=0.01, tipo_error="%")
    se.generar_tabla()
    se.graficar()
    se.solucion()


if __name__ == '__main__':
    main()
