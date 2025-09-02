from mnspy.integrales import Integral
from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt
import sys
plt.rcParams.update(plt.rcParamsDefault)

class Simpson13(Integral):
    """Calcula la integral de una función usando la regla de Simpson 1/3 compuesta.

    Attributes
    ----------
    f: callable
        Función a integrar.
    a: float
        Límite inferior de integración.
    b: float
        Límite superior de integración.
    n: int
        Número de segmentos (debe ser un número par).
    integral : float
        Resultado del cálculo de la integral.

    Methods
    -------
    graficar():
        Genera una gráfica del proceso de integración.

    Examples
    -------
    from mnspy import Simpson13
    import numpy as np

    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    sim = Simpson13(g, 0, 0.8, 2)
    sim.graficar()
    print(sim.integral)
    """
    def __init__(self, f: callable, a: float, b: float, n: int = 100):
        """Constructor de la clase Simpson13

        Parameters
        ----------
        f: callable
            Función a integrar, f(x).
        a: float
            Límite inferior de integración.
        b: float
            Límite superior de integración.
        n: int, optional
            Número de segmentos. Debe ser un número par. Por defecto es 100.
        """
        super().__init__(f=f, a=a, b=b, n=n)
        if self._n % 2 != 0:
            print("Error: El número de segmentos (n) debe ser par para la regla de Simpson 1/3.")
            sys.exit()
        self._calcular()

    def _calcular(self):
        """Calcula la integral por el método de Simpson 1/3.

        El resultado se almacena en el atributo `self.integral`.

        Returns
        -------
        None
        """
        h = (self._b - self._a) / self._n
        x_vals = np.linspace(self._a, self._b, self._n + 1)
        y_vals = self._f(x_vals)

        # Suma de los puntos impares (multiplicados por 4)
        s_impares = 4 * np.sum(y_vals[1:-1:2])
        # Suma de los puntos pares (multiplicados por 2)
        s_pares = 2 * np.sum(y_vals[2:-1:2])

        self.integral = (h / 3) * (y_vals[0] + s_impares + s_pares + y_vals[-1])

    def graficar(self):
        """Genera una gráfica del proceso de integración.

        Muestra la función y las parábolas de interpolación utilizadas por la
        regla de Simpson 1/3 para aproximar el área.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        x = np.linspace(self._a, self._b, self._n + 1)
        y = self._f(x)
        xvals = np.linspace(self._a, self._b, 100)
        # Se usa una interpolación cuadrática para visualizar las parábolas
        spl = interp1d(x, y, kind='quadratic')
        y_smooth = spl(xvals)
        plt.stem(x, y, linefmt='C2--', markerfmt='C0o', basefmt='C2-')
        # plt.plot(x, y, 'o--', color='C2', lw=1)
        plt.fill_between(xvals, y_smooth, color='green', alpha=0.3, label='Regla Simpson 1/3')
        plt.title(r'$\int{f(x)}\approx ' + str(self.integral) + '$')
        self._graficar_datos()


def main():
    """Función principal para demostración."""
    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    sim = Simpson13(g, 0, 0.8, 2)
    sim.graficar()
    print(sim.integral)


if __name__ == '__main__':
    main()
