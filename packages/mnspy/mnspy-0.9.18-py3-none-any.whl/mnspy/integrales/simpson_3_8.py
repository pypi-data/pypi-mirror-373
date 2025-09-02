from mnspy.integrales import Integral
from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt
import sys
plt.rcParams.update(plt.rcParamsDefault)

class Simpson38(Integral):
    """Calcula la integral de una función usando la regla de Simpson 3/8 compuesta.

    Attributes
    ----------
    f: callable
        Función a integrar.
    a: float
        Límite inferior de integración.
    b: float
        Límite superior de integración.
    n: int
        Número de segmentos (debe ser un múltiplo de 3).
    integral : float
        Resultado del cálculo de la integral.

    Methods
    -------
    graficar():
        Genera una gráfica del proceso de integración.

    Examples
    -------
    from mnspy import Simpson38
    import numpy as np

    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    sim = Simpson38(g, 0, 0.8, 3)
    sim.graficar()
    print(sim.integral)
    """
    def __init__(self, f: callable, a: float, b: float, n: int = 99):
        """Constructor de la clase Simpson38

        Parameters
        ----------
        f: callable
            Función a integrar, f(x).
        a: float
            Límite inferior de integración.
        b: float
            Límite superior de integración.
        n: int, optional
            Número de segmentos. Debe ser un múltiplo de 3. Por defecto es 99.
        """
        super().__init__(f=f, a=a, b=b, n=n)
        if self._n % 3 != 0:
            print("Error: El número de segmentos (n) debe ser múltiplo de 3 para la regla de Simpson 3/8.")
            sys.exit()
        self._calcular()

    def _calcular(self):
        """Calcula la integral por el método de Simpson 3/8.

        El resultado se almacena en el atributo `self.integral`.

        Returns
        -------
        None
        """
        h = (self._b - self._a) / self._n
        x_vals = np.linspace(self._a, self._b, self._n + 1)
        y_vals = self._f(x_vals)

        s = y_vals[0] + y_vals[-1]
        # Suma de los puntos con i no múltiplo de 3 (multiplicados por 3)
        s += 3 * np.sum(y_vals[1:-1][(np.arange(1, self._n) % 3) != 0])
        # Suma de los puntos con i múltiplo de 3 (multiplicados por 2)
        s += 2 * np.sum(y_vals[3:-1:3])

        self.integral = (3 * h / 8) * s

    def graficar(self):
        """Genera una gráfica del proceso de integración.

        Muestra la función y las cúbicas de interpolación utilizadas por la
        regla de Simpson 3/8 para aproximar el área.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        x = np.linspace(self._a, self._b, self._n + 1)
        y = self._f(x)
        xvals = np.linspace(self._a, self._b, 100)
        # Se usa una interpolación cúbica para visualizar las curvas
        spl = interp1d(x, y, kind='cubic')
        y_smooth = spl(xvals)
        plt.stem(x, y, linefmt='C2--', markerfmt='C0o', basefmt='C2-')
        # plt.plot(x, y, 'o--', color='C2', lw=1)
        plt.fill_between(xvals, y_smooth, color='green', alpha=0.3, label='Regla Simpson 3/8')
        plt.title(r'$\int{f(x)}\approx ' + str(self.integral) + '$')
        self._graficar_datos()


def main():
    """Función principal para demostración."""
    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    sim = Simpson38(g, 0, 0.8, 3)
    sim.graficar()
    print(sim.integral)


if __name__ == '__main__':
    main()
