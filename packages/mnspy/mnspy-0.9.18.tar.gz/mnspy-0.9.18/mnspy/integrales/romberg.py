from mnspy.integrales import Trapezoidal
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Romberg(Trapezoidal):
    """Calcula la integral de una función usando el método de integración de Romberg.

    Este método utiliza la extrapolación de Richardson para mejorar sucesivamente
    las estimaciones de la integral obtenidas con la regla del trapecio,
    logrando una alta precisión con menos evaluaciones de la función.

    Attributes
    ----------
    f: callable
        Función a integrar.
    a: float
        Límite inferior de integración.
    b: float
        Límite superior de integración.
    error_deseado: float
        Máximo error porcentual permitido para la convergencia.
    max_iter: int
        Número máximo de iteraciones permitidas.
    integral : float
        Resultado del cálculo de la integral.

    Methods
    -------
    graficar():
        Genera una gráfica del proceso de integración.

    Examples
    -------
    from mnspy import Romberg

    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    ro = Romberg(g, 0, 0.8)
    ro.graficar()
    print(ro.integral)
    """

    def __init__(self, f: callable, a: float, b: float, error_deseado: float = 1.e-8, max_iter: int = 30):
        """Constructor de la clase Romberg

        Parameters
        ----------
        f: callable
            Función a integrar, f(x).
        a: float
            Límite inferior de integración.
        b: float
            Límite superior de integración.
        error_deseado: float, optional
            Máximo error porcentual permitido. Por defecto es 1e-8.
        max_iter: int, optional
            Número máximo de iteraciones permitidas. Por defecto es 30.
        """
        super().__init__(f=f, a=a, b=b, n=1)
        self._error_deseado = error_deseado
        self._max_iter = max_iter
        self._error = 0
        self._iter = 0
        self._iterar()

    def _iterar(self):
        """Proceso iterativo para el cálculo de la integral con el método de Romberg.

        Construye una tabla de extrapolación de Richardson para mejorar
        sucesivamente las estimaciones de la integral obtenidas con la regla del trapecio.
        """
        self._n = 1
        I = np.zeros((2 * self._max_iter, self._max_iter + 1))
        super()._calcular()
        I[0, 0] = self.integral
        for self._iter in range(1, self._max_iter + 1):
            self._n = 2 ** self._iter
            super()._calcular()
            I[self._iter, 0] = self.integral
            # Extrapolación de Richardson
            for k in range(1, self._iter + 1):
                j = self._iter - k
                I[j, k] = (4 ** k * I[j + 1, k - 1] - I[j, k - 1]) / (4 ** k - 1)
            # Criterio de parada
            self._error = abs((I[0, self._iter] - I[1, self._iter - 1]) * 100 / I[0, self._iter])
            if self._error <= self._error_deseado:
                break
        self.integral = I[0, self._iter]

    def _agregar_datos(self):
        """Agrega a la gráfica los polígonos trapezoidales para cada nivel
        de la extrapolación de Romberg.
        """
        for i in range(self._iter + 1):
            x = np.linspace(self._a, self._b, (2 ** i) + 1)
            y = self._f(x)
            ind_color = 'C' + str(i)
            plt.stem(x, y, linefmt='C0--', markerfmt='C0o', basefmt='C0-')
            plt.fill_between(x, y, color=ind_color, alpha=0.3, label='Regla de Romberg' + ' n=' + str((2 ** i)))
            # plt.plot(x, y, 'o--', color=ind_color, lw=1)
            # plt.fill_between(x, y, color=ind_color, alpha=0.3, label='Trapecio n=' + str((2 ** i)))

    def graficar(self):
        """Genera una gráfica del proceso de integración de Romberg.

        Muestra la función y las áreas trapezoidales superpuestas que se
        utilizan en cada nivel de la extrapolación.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        self._agregar_datos()
        plt.title(r'$\int{f(x)}\approx ' + str(self.integral) + '$')
        self._graficar_datos()


def main():
    """Función principal para demostración."""
    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    ro = Romberg(g, 0, 0.8)
    ro.graficar()
    print(ro.integral)


if __name__ == '__main__':
    main()
