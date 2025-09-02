from mnspy.raíces import Raices
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Secante(Raices):
    """Clase para la implementación del cálculo de raíces por el método abierto de la Secante.

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
        Realiza los cálculos iterativos del método de la Secante.
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Genera una gráfica del proceso de búsqueda de la raíz.

    Examples
    -------
    from mnspy import Secante

    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    se = Secante(f, 0, 0.5, 0.01, tipo_error="%")
    se.generar_tabla()
    se.graficar()
    se.solucion()
    """
    def __init__(self, f: callable, x_0: float = 0, x_1: float = 0, tol: float | int = 1e-3, max_iter: int = 20,
                 tipo_error='%'):
        """
        Constructor de la clase Secante.

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
        # El método de la secante es abierto, no requiere x_min y x_max.
        super().__init__(f, None, None, tol, max_iter, tipo_error)
        self._x_0 = self._x_0_i = x_0
        self._x_1 = self._x_1_i = self.x = x_1
        self._calcular()

    def _calcular(self):
        """Calcula la raíz de la función de forma iterativa usando el método de la Secante.

        Este método es una aproximación del método de Newton-Raphson que no
        requiere el cálculo de la derivada. Utiliza una línea secante a través
        de los dos últimos puntos para aproximar la siguiente raíz.

        Returns
        -------
        None
        """
        self.x -= (self._f(self._x_1_i) * (self._x_1_i - self._x_0_i)) / (
                self._f(self._x_1_i) - self._f(self._x_0_i))
        self._x_0_i = self._x_1_i
        self._x_1_i = self.x
        if self._fin_iteracion():
            return
        else:
            self._calcular()

    def graficar(self, mostrar_sol: bool = True, mostrar_iter: bool = True, mostrar_lin_iter: bool = True,
                 n_puntos: int = 100):
        """Genera una gráfica del proceso de búsqueda de la raíz por el método de la Secante.

        Parameters
        ----------
        mostrar_sol: bool
            si es verdadero muestra el punto donde se encontró la solución
            por defecto es True
        mostrar_iter: bool
            si es verdadero muestra los puntos obtenidos de cada iteración
            por defecto es True
        mostrar_lin_iter: bool, optional
            Si es ``True``, muestra las líneas secantes utilizadas en cada
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
            l_x.insert(1, self._x_1)
            for i, x in enumerate(l_x[:-1]):
                y = self._f(x)
                x_next = l_x[i + 1]
                if not np.allclose(x, x_next) and not np.allclose(y, self._f(x_next)):
                    plt.axline((x, y), (x_next, self._f(x_next)), linestyle='dashed', c='purple', lw=1)
                if i > 0:
                    plt.plot([x_next, x_next], [0, self._f(x_next)], linestyle='dashed', c='purple', lw=1)
        plt.title(f'x = {self.x}')
        if self._error_porcentual:
            plt.suptitle('Método de la Secante (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle('Método de la Secante (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    """Función principal para demostración."""
    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    se = Secante(f, 0, 0.5, 0.01, tipo_error="%")
    se.generar_tabla()
    se.graficar()
    se.solucion()


if __name__ == '__main__':
    main()
