from mnspy.raíces import Raices
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Muller(Raices):
    """Clase para la implementación del cálculo de raíces por el método abierto de Muller.

    Attributes
    ----------
    f: callable
        Función a la que se le hallará la raíz.
    x: float
        Valor de x inicial.
    h: float
        Valor del delta x que se sumará y restará al x inicial para crear
        los tres puntos iniciales.
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
        Realiza los cálculos iterativos del método de Muller.
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Genera una gráfica del proceso de búsqueda de la raíz.

    Examples
    -------
    import numpy as np

    def f(x):
        return np.sin(x)

    mu = Muller(f, 5, tol=0.01, tipo_error="%")
    mu.generar_tabla()
    mu.graficar()
    mu.solucion()
    """
    def __init__(self, f: callable, x: float = 0, h: float = 1e-1, tol: float | int = 1e-3, max_iter: int = 20,
                 tipo_error='%'):
        """
        Constructor de la clase Muller.

        Parameters
        ----------
        f: callable
            Función a la que se le hallará la raíz.
        x: float
            Valor de x inicial.
        h: float
            Valor del delta x para generar los puntos iniciales.
        tol: float | int
            Máxima tolerancia del error.
        max_iter: int
            Número máximo de iteraciones permitido.
        tipo_error: str
            Tipo de error a utilizar: ``'%'``, ``'/'`` o ``'n'``.
        """
        # El método de Muller es abierto, por lo que x_min y x_max no se usan en el constructor padre.
        super().__init__(f, None, None, tol, max_iter, tipo_error)
        self.x = x
        self._x_2_i = self._x_0 = self.x
        self._x_1_i = self.x + h
        self._x_0_i = self.x - h
        self._a_0 = []
        self._a_1 = []
        self._a_2 = []
        self._list_x_0 = []
        self._list_x_1 = []
        self._list_x_2 = []
        self._calcular()

    def _calcular(self):
        """Calcula la raíz de la función de forma iterativa usando el método de Muller.

        El método utiliza una parábola que pasa por tres puntos para aproximar
        la siguiente estimación de la raíz.

        Returns
        -------
        None
        """
        h_0 = self._x_1_i - self._x_0_i
        h_1 = self._x_2_i - self._x_1_i
        d_0 = (self._f(self._x_1_i) - self._f(self._x_0_i)) / h_0
        d_1 = (self._f(self._x_2_i) - self._f(self._x_1_i)) / h_1
        a = (d_1 - d_0) / (h_1 + h_0)
        b = a * h_1 + d_1
        c = self._f(self._x_2_i)
        # ***
        self._a_2 += [a]
        self._a_1 += [d_0]
        self._a_0 += [self._f(self._x_0_i)]
        self._list_x_0 += [self._x_0_i]
        self._list_x_1 += [self._x_1_i]
        self._list_x_2 += [self._x_2_i]
        # ***
        rad = np.sqrt(b ** 2 - 4 * a * c)
        if abs(b + rad) > abs(b - rad):
            den = b + rad
        else:
            den = b - rad
        self.x = self._x_2_i - 2 * c / den
        if self._fin_iteracion():
            return
        else:
            self._x_0_i = self._x_1_i
            self._x_1_i = self._x_2_i
            self._x_2_i = self.x
            self._calcular()

    def graficar(self, mostrar_sol: bool = True, mostrar_iter: bool = True, mostrar_lin_iter: bool = True,
                 n_puntos: int = 100):
        """Genera una gráfica del proceso de búsqueda de la raíz por el método de Muller.

        Parameters
        ----------
        mostrar_sol: bool
            Si es ``True``, muestra el punto de la solución final.
        mostrar_iter: bool
            Si es ``True``, muestra los puntos de cada iteración.
        mostrar_lin_iter: bool, optional
            Si es ``True``, muestra las parábolas de interpolación utilizadas en
            cada iteración. Por defecto es ``True``.
        n_puntos: int, optional
            Número de puntos para dibujar la curva de la función. Por defecto es 100.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        plt.autoscale(False)
        if mostrar_lin_iter and len(self._tabla['x']) > 0:
            x = np.linspace(min(self._tabla['x'] + [self._x_0]), max(self._tabla['x'] + [self._x_0]), n_puntos)
            for i in range(len(self._tabla['x'])):
                y = self._a_2[i] * (x - self._list_x_0[i]) * (x - self._list_x_1[i]) + self._a_1[i] * (
                        x - self._list_x_0[i]) + self._a_0[i]
                plt.plot(x, y, linestyle='dashed', c='purple', lw=1)
                plt.plot([self._tabla['x'][i], self._tabla['x'][i]], [0, self._f(self._tabla['x'][i])], linestyle='dashed',
                         c='purple', lw=1)
        plt.autoscale(True)
        plt.title(f'x = {self.x}')
        if self._error_porcentual:
            plt.suptitle('Método de Müller (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle('Método de Müller (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    """Función principal para demostración."""
    def f(x):
        # return x ** 3 - 13 * x - 12
        return np.sin(x)

    mu = Muller(f, 5, tol=0.01, tipo_error="%")
    mu.generar_tabla()
    mu.graficar()
    mu.solucion()


if __name__ == '__main__':
    main()
