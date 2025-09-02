from mnspy.ecuaciones_diferenciales_ordinarias import EcuacionesDiferencialesOrdinarias
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Euler(EcuacionesDiferencialesOrdinarias):
    """Soluciona una EDO de primer orden usando el método de Euler.

    Este es el método explícito más simple para la integración numérica de EDOs.
    Avanza la solución un paso `h` utilizando la tangente en el punto actual.

    Attributes
    ----------
    f : callable
        La ecuación diferencial a resolver, `dy/dx = f(x, y)`.
    x : np.ndarray
        Array con los valores de la variable independiente `x`.
    y : np.ndarray
        Array con los valores de la solución numérica `y(x)`.
    h : float
        Tamaño del paso de integración.

    Methods
    -------
    _calcular():
        Ejecuta el algoritmo de Euler para calcular la solución.

    graficar():
        Genera una gráfica de la solución numérica.

    Examples:
    -------
    from mnspy import Euler
    import numpy as np

    def g(x, y):
        return -2 * x ** 3 + 12 * x ** 2 - 20 * x + 8.5

    def exac_g(x):
        return -0.5 * x ** 4 + 4 * x ** 3 - 10 * x ** 2 + 8.5 * x + 1

    eu = Euler(g, 0, 4, 1, 0.5, exac_g)
    eu.graficar()
    eu.solucion()

    def f(x, y):
        return 4 * np.exp(0.8 * x) - 0.5 * y

    def exac_f(x):
        return (4 / 1.3) * (np.exp(0.8 * x) - np.exp(-0.5 * x)) + 2 * np.exp(-0.5 * x)

    eu = Euler(f, 0, 4, 2, 1, exac_f)
    eu.graficar()
    print(eu.y)
    """
    def __init__(self, f: callable, x_i: float, x_f: float, y_i: float, h: float, sol_exacta: callable = None):
        """Constructor de la clase Euler

        Parameters
        ----------
        f : callable
            Ecuación diferencial a resolver, `dy/dx = f(x, y)`.
        x_i : float
            Valor inicial de la variable independiente `x`.
        x_f : float
            Valor final de la variable independiente `x`.
        y_i : float
            Condición inicial para `y` en `x_i`.
        h : float
            Tamaño del paso de integración.
        sol_exacta : callable, optional
            Función de la solución exacta para graficar y comparar, por defecto ``None``.
        """
        super().__init__(f, x_i, x_f, y_i, h, sol_exacta)
        self._calcular()

    def _calcular(self):
        """Soluciona la EDO por el método de Euler.

        La solución se calcula iterativamente usando la fórmula:
        y_{i+1} = y_i + f(x_i, y_i) * h
        y se almacena en el atributo `self.y`.

        Returns
        -------
        None
        """
        self.y[0] = self.y_i
        for i in range(len(self.x) - 1):
            self.y[i + 1] = self.y[i] + self.f(self.x[i], self.y[i]) * self.h

    def graficar(self):
        """Presenta la gráfica de la solución de la ecuación diferencial.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        plt.plot(self.x, self.y, color='g', lw=2, marker='o', label='Método de Euler')
        plt.title('Método de Euler')
        self._graficar_datos()


def main():
    """Función principal para demostración."""
    def g(x, y):
        return -2 * x ** 3 + 12 * x ** 2 - 20 * x + 8.5

    def exac_g(x):
        return -0.5 * x ** 4 + 4 * x ** 3 - 10 * x ** 2 + 8.5 * x + 1

    eu = Euler(g, 0, 4, 1, 0.5, exac_g)
    eu.graficar()
    eu.solucion()

    def f(x, y):
        return 4 * np.exp(0.8 * x) - 0.5 * y

    def exac_f(x):
        return (4 / 1.3) * (np.exp(0.8 * x) - np.exp(-0.5 * x)) + 2 * np.exp(-0.5 * x)

    eu = Euler(f, 0, 4, 2, 1, exac_f)
    eu.graficar()
    print(eu.y)


if __name__ == '__main__':
    main()
