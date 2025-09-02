from mnspy.ecuaciones_diferenciales_ordinarias import EcuacionesDiferencialesOrdinarias
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Heun(EcuacionesDiferencialesOrdinarias):
    """Soluciona una EDO de primer orden usando el método de Heun.

    Este método es del tipo predictor-corrector. Primero predice un valor
    usando el método de Euler y luego lo corrige promediando las pendientes
    al inicio y al final del intervalo. Opcionalmente, puede iterar el
    paso corrector hasta alcanzar una tolerancia de error.

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
        Ejecuta el algoritmo de Heun para calcular la solución.

    graficar():
        Genera una gráfica de la solución numérica.

    Examples:
    -------
    from mnspy import Heun
    import numpy as np

    def g(x, y):
        return -2 * x ** 3 + 12 * x ** 2 - 20 * x + 8.5

    def exac_g(x):
        return -0.5 * x ** 4 + 4 * x ** 3 - 10 * x ** 2 + 8.5 * x + 1

    eu = Heun(g, 0, 4, 1, 0.5, exac_g)
    eu.graficar()
    print(eu.y)

    def f(x, y):
        return 4 * np.exp(0.8 * x) - 0.5 * y

    def exac_f(x):
        return (4 / 1.3) * (np.exp(0.8 * x) - np.exp(-0.5 * x)) + 2 * np.exp(-0.5 * x)

    eu = Heun(f, 0, 4, 2, 1, exac_f)
    eu.graficar()
    print(eu.y)

    eu = Heun(f, 0, 4, 2, 1, exac_f, 0.00001)
    eu.graficar()
    print(eu.y)
    """
    def __init__(self, f: callable, x_i: float, x_f: float, y_i: float, h: float, sol_exacta: callable = None,
                 por_error: float = None):
        """Constructor de la clase Heun

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
        por_error : float, optional
            Si se proporciona, activa el modo de corrector iterativo. El bucle
            corrector se detiene cuando el error relativo porcentual es menor
            que este valor. Por defecto es ``None``.
        """
        super().__init__(f, x_i, x_f, y_i, h, sol_exacta)
        self._porc_error = por_error
        self._calcular()

    def _calcular(self):
        """Soluciona la EDO por el método de Heun.

        Implementa el método predictor-corrector. Si `_porc_error` está definido,
        itera el paso corrector hasta converger.

        Returns
        -------
        None
        """
        self.y[0] = self.y_i
        if self._porc_error is None:
            # Método de Heun sin corrector iterativo
            for i in range(len(self.x) - 1):
                # Predictor (Paso de Euler)
                y_0 = self.y[i] + self.f(self.x[i], self.y[i]) * self.h
                # Corrector
                self.y[i + 1] = self.y[i] + 0.5 * (
                        self.f(self.x[i], self.y[i]) + self.f(self.x[i + 1], y_0)) * self.h
        else:
            # Método de Heun con corrector iterativo
            for i in range(len(self.x) - 1):
                y_0 = self.y[i] + self.f(self.x[i], self.y[i]) * self.h
                self.y[i + 1] = self.y[i] + 0.5 * (self.f(self.x[i], self.y[i]) + self.f(self.x[i + 1], y_0)) * self.h
                # Bucle para iterar el corrector
                while abs((self.y[i + 1] - y_0) / self.y[i + 1]) * 100 > abs(self._porc_error):
                    y_0 = self.y[i + 1]
                    self.y[i + 1] = self.y[i] + 0.5 * (self.f(self.x[i], self.y[i]) + self.f(self.x[i + 1], y_0)) * self.h

    def graficar(self):
        """Presenta la gráfica de la solución de la ecuación diferencial.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        plt.plot(self.x, self.y, color='g', lw=2, marker='o', label='Método de Heun')
        plt.title('Método de Heun')
        self._graficar_datos()


def main():
    """Función principal para demostración."""
    def g(x, y):
        return -2 * x ** 3 + 12 * x ** 2 - 20 * x + 8.5

    def exac_g(x):
        return -0.5 * x ** 4 + 4 * x ** 3 - 10 * x ** 2 + 8.5 * x + 1

    eu = Heun(g, 0, 4, 1, 0.5, exac_g)
    eu.graficar()
    print(eu.y)

    def f(x, y):
        return 4 * np.exp(0.8 * x) - 0.5 * y

    def exac_f(x):
        return (4 / 1.3) * (np.exp(0.8 * x) - np.exp(-0.5 * x)) + 2 * np.exp(-0.5 * x)

    eu = Heun(f, 0, 4, 2, 1, exac_f)
    eu.graficar()
    print(eu.y)

    eu = Heun(f, 0, 4, 2, 1, exac_f, 0.00001)
    eu.graficar()
    print(eu.y)


if __name__ == '__main__':
    main()
