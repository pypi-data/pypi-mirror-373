from mnspy.raíces import Raices
import numpy as np
import matplotlib.pyplot as plt
import sys
plt.rcParams.update(plt.rcParamsDefault)

class Biseccion(Raices):
    """Clase para la implementación del cálculo de raíces por el método cerrado de la Bisección.

    Attributes
    ----------
    f: callable
        Función a la que se le hallará la raíz.
    x_min: float
        Límite inferior del intervalo de búsqueda.
    x_max: float
        Límite superior del intervalo de búsqueda.
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
        Realiza los cálculos iterativos del método de la bisección.
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Genera una gráfica del proceso de búsqueda de la raíz.

    Examples
    -------
    from mnspy import Biseccion

    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    bis = Biseccion(f, 0, 1, tol=4, tipo_error='n')
    bis.generar_tabla()
    bis.graficar()
    bis.solucion()

    bis = Biseccion(f, 0, 1, tol=5, tipo_error='%')
    bis.generar_tabla()
    bis.graficar()
    bis.solucion()
    """

    def __init__(self, f: callable, x_min: float = 0, x_max: float = 0, tol: float | int = 1e-3, max_iter: int = 20,
                 tipo_error='%'):
        """
        Constructor de la clase Biseccion.

        Parameters
        ----------
        f: callable
            Función a la que se le hallará la raíz.
        x_min: float
            Límite inferior del intervalo de búsqueda.
        x_max: float
            Límite superior del intervalo de búsqueda.
        tol: float | int
            Máxima tolerancia del error.
        max_iter: int
            Número máximo de iteraciones permitido.
        tipo_error: str
            Tipo de error a utilizar: ``'%'``, ``'/'`` o ``'n'``.
        """
        super().__init__(f, x_min, x_max, tol, max_iter, tipo_error)
        self._calcular()

    def _calcular(self):
        """Calcula la raíz de la función de forma iterativa usando el método de bisección.

        El método divide repetidamente el intervalo en dos y selecciona el subintervalo
        en el que existe un cambio de signo.

        Returns
        -------
        None
        """
        # Verifica que la raíz se encuentre dentro del intervalo inicial.
        if np.sign(self._f(self._x_min)) == np.sign(self._f(self._x_max)):
            print("La raíz no está dentro de este rango, pruebe con otro rango de datos")
            sys.exit()

        self.x = (self._x_min + self._x_max) / 2
        if self._fin_iteracion():
            return
        elif np.sign(self._f(self._x_min)) == np.sign(self._f(self.x)):
            self._x_min = self.x
            self._calcular()
        elif np.sign(self._f(self._x_max)) == np.sign(self._f(self.x)):
            self._x_max = self.x
            self._calcular()

    def graficar(self, mostrar_sol: bool = True, mostrar_iter: bool = True, mostrar_lin_iter: bool = True,
                 n_puntos: int = 100):
        """Genera una gráfica del proceso de búsqueda de la raíz por el método de bisección.

        Parameters
        ----------
        mostrar_sol: bool
            si es verdadero muestra el punto donde se encontró la solución
            por defecto es True
        mostrar_iter: bool
            si es verdadero muestra los puntos obtenidos de cada iteración.
        mostrar_lin_iter: bool, optional
            Si es ``True``, muestra las líneas auxiliares que representan los
            intervalos de cada iteración. Por defecto es ``True``.
        n_puntos: int, optional
            Número de puntos para dibujar la curva de la función. Por defecto es 100.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        if mostrar_lin_iter and len(self._tabla['x']) > 0:
            y = [self._f(val) for val in np.linspace(self._rango[0], self._rango[1], n_puntos)]
            y_min = min(y)
            y_max = max(y)
            delta_y = (y_max - y_min) / 40.0
            for i, x in enumerate(self._tabla['x']):
                y = self._f(x)
                ind_color = 'C' + str(i % 10)
                datos = plt.stem(x, y, linefmt=ind_color + '--', markerfmt=ind_color, basefmt=ind_color + '-',
                                 bottom=y_min - (i + 1) * delta_y)
                linea_base = datos[2]
                plt.setp(linea_base, 'linewidth', 2, 'marker', '.')
                linea_base.set_xdata([self._tabla['x_min'][i], self._tabla['x_max'][i]])
        plt.title(f'x = {self.x}')
        if self._error_porcentual:
            plt.suptitle('Método de la Bisección (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle('Método de la Bisección (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    """Función principal para demostración."""
    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    bis = Biseccion(f, 0, 1, tol=4, tipo_error='n')
    bis.generar_tabla()
    bis.graficar()
    bis.solucion()

    bis = Biseccion(f, 0, 1, tol=5, tipo_error='%')
    bis.generar_tabla()
    bis.graficar()
    bis.solucion()


if __name__ == '__main__':
    main()
