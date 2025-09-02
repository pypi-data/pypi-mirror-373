from mnspy.integrales import Integral
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)
class GaussLegendre(Integral):
    """Calcula la integral de una función usando la cuadratura de Gauss-Legendre.

    Este método aproxima la integral evaluando la función en puntos específicos
    (los nodos de Gauss) y sumando estos valores con pesos precalculados. Es
    muy preciso para el número de puntos utilizados.

    Attributes
    ----------
    f: callable
        Función a integrar.
    a: float
        Límite inferior de integración.
    b: float
        Límite superior de integración.
    integral : float
        Resultado del cálculo de la integral.

    Methods
    -------
    graficar():
        Genera una gráfica del proceso de integración.

    Examples
    -------
    from mnspy import GaussLegendre
    import numpy as np

    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    gl = GaussLegendre(g, 0, 0.8, n=6)
    gl.graficar()
    print(gl.integral)
    """
    def __init__(self, f: callable, a: float, b: float, n: int = 2):
        """Constructor de la clase GaussLegendre

        Parameters
        ----------
        f: callable
            Función a integrar, f(x).
        a: float
            Límite inferior de integración.
        b: float
            Límite superior de integración.
        n: int, optional
            Número de puntos a utilizar (2, 3, 4, 5 o 6). Si se ingresa
            un valor no válido, se usará n=2 por defecto.
        """
        super().__init__(f=f, a=a, b=b, n=n)
        # Coeficientes y puntos de la cuadratura de Gauss-Legendre
        if self._n == 2:
            self._c = [1, 1]
            self._x = [-0.577350269, 0.577350269]
        elif self._n == 3:
            self._c = [0.5555556, 0.8888889, 0.5555556]
            self._x = [-0.774596669, 0, 0.774596669]
        elif self._n == 4:
            self._c = [0.3478548, 0.6521452, 0.6521452, 0.3478548]
            self._x = [-0.861136312, -0.339981044, 0.339981044, 0.861136312]
        elif self._n == 5:
            self._c = [0.2369269, 0.4786287, 0.5688889, 0.4786287, 0.2369269]
            self._x = [-0.906179846, -0.538469310, 0, 0.538469310, 0.906179846]
        elif self._n == 6:
            self._c = [0.1713245, 0.3607616, 0.4679139, 0.4679139, 0.3607616, 0.1713245]
            self._x = [-0.932469514, -0.661209386, -0.238619186, 0.238619186, 0.661209386, 0.932469514]
        else:
            self._n = 2
            self._c = [1, 1]
            self._x = [-0.577350269, 0.577350269]
        self._calcular()

    def _calcular(self):
        """Calcula la integral por el método de Gauss-Legendre.

        El resultado se almacena en el atributo `self.integral`.

        Returns
        -------
        None
        """
        suma = 0
        for i in range(self._n):
            # Transformación de la variable de [-1, 1] al intervalo [a, b]
            x_transformado = 0.5 * (self._b - self._a) * self._x[i] + 0.5 * (self._b + self._a)
            suma += self._c[i] * self._f(x_transformado)

        self.integral = 0.5 * (self._b - self._a) * suma

    def graficar(self):
        """Genera una gráfica del proceso de integración.

        Muestra la función y resalta los puntos de Gauss-Legendre evaluados.
        """
        x = list((0.5 * (self._b - self._a) * x_i + 0.5 * (self._b + self._a) for x_i in self._x))
        y = list((self._f(x_i) for x_i in x))
        plt.stem(x, y, linefmt='C2--', markerfmt='C0o', basefmt='C2-', label=f'Gauss-Legendre (n={self._n})')
        plt.title(f'$\\int{{f(x)\\,dx}} \\approx {self.integral:.8f}$')
        self._graficar_datos()


def main():
    """Función principal para demostración."""
    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    gl = GaussLegendre(g, 0, 0.8, n=6)
    gl.graficar()
    print(gl.integral)


if __name__ == '__main__':
    main()
