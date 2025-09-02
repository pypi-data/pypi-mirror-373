from mnspy.integrales import Integral
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Trapezoidal(Integral):
    """Calcula la integral de una función usando la regla del trapecio compuesta.

    Attributes
    ----------
    f: callable
        Función a integrar.
    a: float
        Límite inferior de integración.
    b: float
        Límite superior de integración.
    n: int
        Número de segmentos o trapecios en los que se divide el intervalo.
    integral : float
        Resultado del cálculo de la integral.

    Methods
    -------
    graficar():
        Genera una gráfica del proceso de integración.

    Examples
    -------
    from mnspy import Trapezoidal

    def f(x):
        return (x + 1 / x) ** 2

    trap = Trapezoidal(f, 1, 2, 6)
    trap.graficar()
    print(trap.integral)
    """

    def __init__(self, f: callable, a: float, b: float, n: int = 100):
        """Constructor de la clase Trapezoidal

        Parameters
        ----------
        f: callable
            Función a integrar, f(x).
        a: float
            Límite inferior de integración.
        b: float
            Límite superior de integración.
        n: int, optional
            Número de segmentos a utilizar. Por defecto es 100.
        """
        super().__init__(f=f, a=a, b=b, n=n)
        self._calcular()

    def _calcular(self):
        """Calcula la integral por el método del trapecio compuesto.

        El resultado se almacena en el atributo `self.integral`.

        Returns
        -------
        None
        """
        h = (self._b - self._a) / self._n
        # Suma de todos los puntos intermedios
        s = sum(self._f(self._a + i * h) for i in range(1, self._n))
        # Fórmula del trapecio compuesto
        self.integral = h * (0.5 * self._f(self._a) + s + 0.5 * self._f(self._b))

    def graficar(self):
        """Genera una gráfica del proceso de integración.

        Muestra la función y los trapecios utilizados para aproximar el área.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        x = np.linspace(self._a, self._b, self._n + 1)
        y = self._f(x)
        plt.stem(x, y, linefmt='C2--', markerfmt='C0o', basefmt='C2-')
        # plt.plot(x, y, 'o--', color='C2', lw=1)
        plt.fill_between(x, y, color='green', alpha=0.3, label='Regla del Trapecio')
        plt.title(r'$\int{f(x)}\approx ' + str(self.integral) + '$')
        self._graficar_datos()


def main():
    """Función principal para demostración."""
    def f(x):
        return (x + 1 / x) ** 2

    trap = Trapezoidal(f, 1, 2, 6)
    trap.graficar()
    print(trap.integral)


if __name__ == '__main__':
    main()
