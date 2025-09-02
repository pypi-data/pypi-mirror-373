from mnspy.interpolación import Interpolacion
from mnspy.utilidades import es_notebook
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

import sympy as sp

sp.init_printing(use_latex=True)


class InterpolacionNewton(Interpolacion):
    """Calcula el polinomio de interpolación de Newton usando diferencias divididas.

    Este método construye un polinomio que pasa por todos los puntos de datos.
    Es computacionalmente más eficiente que el método de Lagrange, ya que
    los coeficientes (diferencias divididas) pueden ser calculados de forma
    recursiva y almacenados en una tabla.

    Attributes
    ----------
    x : np.ndarray
        Array con los datos de la variable independiente.
    y : np.ndarray
        Array con los datos de la variable dependiente.

    Methods
    -------
    evaluar(x: float):
        Evalúa el polinomio de interpolación en un punto `x`.
    obtener_polinomio():
        Genera la expresión simbólica del polinomio de interpolación.
    graficar():
        Genera una gráfica del polinomio y los puntos de datos.

    Examples
    -------
    from mnspy import InterpolacionNewton
    import numpy as np

    x = np.array([1., 4., 6., 5.])
    y = np.log(x)
    inter = InterpolacionNewton(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)
    inter.mostrar_diferencias_divididas()
    print(inter.obtener_polinomio(expandido=True))
    """
    def __init__(self, x: np.ndarray, y: np.ndarray):
        """Constructor de la clase InterpolacionNewton.

        Parameters
        ----------
        x: np.ndarray
            Array con los datos de la variable independiente
        y: np.ndarray
            Array con los datos de la variable dependiente
        """
        super().__init__(x, y)
        # Calcula la tabla de diferencias divididas
        self._b = np.zeros((self._n, self._n))
        self._b[:, 0] = np.transpose(self._y)

        for j in range(1, self._n):
            for i in range(self._n - j):
                self._b[i, j] = (self._b[i + 1, j - 1] - self._b[i, j - 1]) / (self._x[i + j] - self._x[i])

    def evaluar(self, x: float) -> float:
        """Evalúa el polinomio de Newton en un punto `x` usando la forma anidada.

        Parameters
        ----------
        x: float
            Valor de la variable independiente en el que se desea interpolar.

        Returns
        -------
        float
            El valor interpolado y(x).
        """
        x_t = 1
        y_int = self._b[0, 0]
        for j in range(self._n - 1):
            x_t *= (x - self._x[j])  # Término (x - x_0)(x - x_1)...
            y_int += self._b[0, j + 1] * x_t
        return y_int

    def obtener_polinomio(self, expandido: bool = False):
        """Genera la expresión simbólica del polinomio de interpolación.

        Parameters
        ----------
        expandido: bool
            Si es verdadero, retorna el polinomio expandido, en caso contrario muestra el polinomio en forma
            de diferencias divididas.

        Returns
        -------
        Retorna el polinomio que pasa por los puntos de los datos de la interpolación
        """
        x = sp.symbols('x')
        pol = sum([self._b[0][i] * np.prod([(x - self._x[j]) for j in range(i)]) for i in range(self._n)])
        if expandido:
            return sp.expand(pol)
        else:
            return pol

    def mostrar_diferencias_divididas(self):
        """Muestra la tabla de diferencias divididas finitas.

        Returns
        -------
        str or None
            Una tabla HTML para notebooks de Jupyter, o imprime la tabla en la consola.
        """
        tabla = {}
        if es_notebook():
            tabla['$x_{i}$'] = self._x
            tabla['$y_{i}$'] = self._y
            for i in range(self._n - 1):
                dato = list([''] * self._n)
                for j in range(self._n - 1 - i):
                    dato[j] = self._b[j, i + 1]
                tabla['$dif_{' + str(i + 1) + '}$'] = dato
            return tabulate(tabla, headers='keys', tablefmt='html')
        else:
            tabla['x_i'] = self._x
            tabla['y_i'] = self._y
            for i in range(self._n - 1):
                dato = list([''] * self._n)
                for j in range(self._n - 1 - i):
                    dato[j] = self._b[j, i + 1]
                tabla['dif_' + str(i + 1)] = dato
            print(tabulate(tabla, headers='keys', tablefmt='simple'))

    def graficar(self, x: float) -> None:
        """Genera una gráfica del polinomio de interpolación.

        Dibuja el polinomio y resalta los puntos de datos originales, así como
        el punto interpolado `(x, y(x))`.

        Parameters
        ----------
        x: float
            Valor de `x` a interpolar y resaltar en la gráfica.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        y = self.evaluar(x)
        x_min = min(self._x)
        x_max = max(self._x)
        x_list = np.linspace(x_min, x_max, 1000)
        y_list = [self.evaluar(val) for val in x_list]
        plt.scatter(x, y, c='r', lw=2, label='Interpolación Newton')
        plt.plot(x_list, y_list, linestyle='dashed', c='k', lw=1, label='Polinomio')
        plt.annotate('$(' + str(x) + r',\,' + str(y) + ')$', (x, y), c='r', alpha=0.9, textcoords="offset points",
                     xytext=(0, 10), ha='center')
        super()._graficar_datos()


def main():
    x = np.array([1., 4., 6., 5.])
    y = np.log(x)
    inter = InterpolacionNewton(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)
    inter.mostrar_diferencias_divididas()


if __name__ == '__main__':
    main()
