from mnspy.raíces import Raices
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class NewtonRaphson(Raices):
    """Clase para la implementación del cálculo de raíces por el método abierto de Newton-Raphson.

    Attributes
    ----------
    f: callable
        Función a la que se le hallará la raíz.
    df: callable
        Derivada de la función `f`. Si es ``None``, se calculará numéricamente.
    x: float
        Valor de x inicial.
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
        Realiza los cálculos iterativos del método de Newton-Raphson.
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Genera una gráfica del proceso de búsqueda de la raíz.

    Examples
    -------
    from mnspy import NewtonRaphson

    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    def df(x):
        return 3 * x ** 2 - 20 * x

    nr = NewtonRaphson(f, x=10, tol=4, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()

    nr = NewtonRaphson(f, df=df, x=10, tol=4, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()

    nr = NewtonRaphson(f, x=10, tol=5, tipo_error='%')
    nr.generar_tabla()
    nr.graficar()

    nr = NewtonRaphson(f, df=df, x=10, tol=5, tipo_error='%')
    nr.generar_tabla()
    nr.graficar()

    def g(x):
        return x ** 2 - 2

    def dg(x):
        return 2 * x

    nr = NewtonRaphson(g, df=dg, x=1, tol=4, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()

    def f(x):
        return x ** 4 - 6.4 * x ** 3 + 6.45 * x ** 2 + 20.538 * x - 31.752

    def df(x):
        return 4.0 * x ** 3 - 19.2 * x ** 2 + 12.9 * x + 20.538

    nr = NewtonRaphson(f, df=df, x=2, tol=6, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()
    """
    def __init__(self, f: callable, df: callable = None, x: float = 0, tol: float | int = 1e-3, max_iter: int = 20,
                 tipo_error='%'):
        """
        Constructor de la clase NewtonRaphson.

        Parameters
        ----------
        f: callable
            Función a la que se le hallará la raíz.
        df: callable, optional
            Derivada de la función `f`. Si es ``None``, la derivada se calculará
            numéricamente.
        x: float
            Valor de x inicial.
        tol: float | int
            Máxima tolerancia del error.
        max_iter: int
            Número máximo de iteraciones permitido.
        tipo_error: str
            Tipo de error a utilizar: ``'%'``, ``'/'`` o ``'n'``.
        """
        if df is None:
            self._df = self._derivada
        else:
            self._df = df
        # El método de Newton-Raphson es abierto, no requiere x_min y x_max.
        super().__init__(f, None, None, tol, max_iter, tipo_error)
        self.x = x
        self._x_0 = x
        self._calcular()

    def _calcular(self):
        """Calcula la raíz de la función de forma iterativa usando el método de Newton-Raphson.

        El método utiliza la tangente a la curva en el punto actual para
        encontrar la siguiente aproximación de la raíz.

        Returns
        -------
        None
        """
        self.x -= self._f(self.x) / self._df(self.x)
        if self._fin_iteracion():
            return
        else:
            self._calcular()

    def graficar(self, mostrar_sol: bool = True, mostrar_iter: bool = True, mostrar_lin_iter: bool = True,
                 n_puntos: int = 100):
        """
        Realiza la gráfica del cálculo de la raíz por el método de NewtonRaphson.

        Parameters
        ----------
        mostrar_sol: bool, optional
            Si es ``True``, muestra el punto de la solución final. Por defecto es ``True``.
        mostrar_iter: bool, optional
            Si es ``True``, muestra los puntos de cada iteración. Por defecto es ``True``.
        mostrar_lin_iter: bool, optional
            Si es ``True``, muestra las líneas tangentes utilizadas en cada
            iteración. Por defecto es ``True``.
        n_puntos: int, optional
            Número de puntos para dibujar la curva de la función. Por defecto es 100.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        if mostrar_lin_iter and len(self._tabla['x']) > 0:
            l_x = self._tabla['x'].copy()
            l_x.insert(0, self._x_0)
            for i, x in enumerate(l_x[:-1]):
                y = self._f(x)
                plt.axline((x, y), slope=self._df(x), linestyle='dashed', c='purple', lw=1)
                x_next = l_x[i + 1]
                plt.plot([x_next, x_next], [0, self._f(x_next)], linestyle='dashed', c='purple', lw=1)
        plt.title(f'x = {self.x}')
        if self._error_porcentual:
            plt.suptitle('Método de Newton-Raphson (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle('Método de Newton-Raphson (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    """Función principal para demostración."""
    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    def df(x):
        return 3 * x ** 2 - 20 * x

    nr = NewtonRaphson(f, x=10, tol=4, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()

    nr = NewtonRaphson(f, df=df, x=10, tol=4, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()

    nr = NewtonRaphson(f, x=10, tol=5, tipo_error='%')
    nr.generar_tabla()
    nr.graficar()

    nr = NewtonRaphson(f, df=df, x=10, tol=5, tipo_error='%')
    nr.generar_tabla()
    nr.graficar()

    def g(x):
        return x ** 2 - 2

    def dg(x):
        return 2 * x

    nr = NewtonRaphson(g, df=dg, x=1, tol=4, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()

    def f(x):
        return x ** 4 - 6.4 * x ** 3 + 6.45 * x ** 2 + 20.538 * x - 31.752

    def df(x):
        return 4.0 * x ** 3 - 19.2 * x ** 2 + 12.9 * x + 20.538

    nr = NewtonRaphson(f, df=df, x=2, tol=6, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()


if __name__ == '__main__':
    main()
