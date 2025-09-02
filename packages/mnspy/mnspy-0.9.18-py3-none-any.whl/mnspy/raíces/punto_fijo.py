from mnspy.raíces import Raices
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class PuntoFijo(Raices):
    """Clase para la implementación del cálculo de raíces por el método abierto de Newton-Raphson.

    Este método busca una raíz resolviendo la ecuación en la forma x = g(x).

    Attributes
    ----------
    f: callable
        Función g(x) para la iteración de punto fijo, donde x = g(x).
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
        Realiza los cálculos iterativos del método de punto fijo.
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Genera una gráfica del proceso de búsqueda de la raíz.

    Examples
    -------
    import numpy as np

    def f(x):
        return 2 * np.sin(np.sqrt(x))

    pf = PuntoFijo(f, 0.5, 0.0001, tipo_error="%")
    pf.generar_tabla()
    pf.graficar()
    pf.solucion()
    """
    def __init__(self, f: callable, x: float = 0, tol: float | int = 1e-3, max_iter: int = 20, tipo_error='%'):
        """
        Constructor de la clase PuntoFijo.

        Parameters
        ----------
        f: callable
            Función g(x) para la iteración, tal que x = g(x).
        x: float
            Valor de x inicial.
        tol: float | int
            Máxima tolerancia del error.
        max_iter: int
            Número máximo de iteraciones permitido.
        tipo_error: str
            Tipo de error a utilizar: ``'%'``, ``'/'`` o ``'n'``.
        """
        # El método de punto fijo es abierto, no requiere x_min y x_max.
        super().__init__(f, None, None, tol, max_iter, tipo_error)
        self._x_0 = self.x = x
        self._calcular()

    def _calcular(self):
        """Calcula la raíz de la función de forma iterativa usando el método de punto fijo.

        La iteración se define por x_{i+1} = g(x_i).

        Returns
        -------
        None
        """
        self.x += self._f(self.x) - self.x
        if self._fin_iteracion():
            return
        else:
            self._calcular()

    def graficar(self, mostrar_sol: bool = True, mostrar_iter: bool = True, mostrar_lin_iter: bool = True,
                 n_puntos: int = 100):
        """Genera una gráfica del proceso de búsqueda de la raíz por el método de Punto Fijo.

        La gráfica muestra la función g(x) y la recta y=x. La solución se
        encuentra en su intersección. Las líneas auxiliares muestran la "escalera"
        o "telaraña" del proceso iterativo.

        Parameters
        ----------
        mostrar_sol: bool
            Si es ``True``, muestra el punto de la solución final.
        mostrar_iter: bool
            si es verdadero muestra los puntos obtenidos de cada iteración
            por defecto es True
        mostrar_lin_iter: bool
            si es verdadero muestra las líneas auxiliares que se usan para obtener la solución
            por defecto es True
        n_puntos: int
            Número de puntos para dibujar la curva de la función.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        if mostrar_lin_iter and len(self._tabla['x']) > 0:
            plt.axline((0, 0), slope=1, linestyle='-', c='k', lw=2, label='$y=x$')
            l_x = self._tabla['x'].copy()
            l_x.insert(0, self._x_0)
            for i, x in enumerate(l_x[:-1]):
                y = self._f(x)
                plt.plot([x, x], [0, y], linestyle='dashed', c='purple', lw=1)
                plt.plot([x, y], [y, y], linestyle='dashed', c='purple', lw=1)
        plt.title(f'x = {self.x}')
        if self._error_porcentual:
            plt.suptitle('Método de Punto Fijo (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle('Método de Punto Fijo (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    """Función principal para demostración."""
    def f(x):
        # return 2 * sin(sqrt(x)) - x
        return 2 * np.sin(np.sqrt(x))

    pf = PuntoFijo(f, 0.5, 0.0001, tipo_error="%")
    pf.generar_tabla()
    pf.graficar()
    pf.solucion()


if __name__ == '__main__':
    main()
