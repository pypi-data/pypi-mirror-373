from mnspy.ecuaciones_diferenciales_ordinarias import EcuacionesDiferencialesOrdinarias
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class RungeKutta(EcuacionesDiferencialesOrdinarias):
    """Soluciona una EDO de primer orden usando los métodos de Runge-Kutta.

    Implementa los métodos clásicos de Runge-Kutta de órdenes 2, 3, 4 y 5.
    Para el orden 2, incluye variantes como Heun, Punto Medio y Ralston.

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
    orden : int
        Orden del método de Runge-Kutta utilizado (2, 3, 4 o 5).

    Methods
    -------
    _calcular():
        Ejecuta el algoritmo de Runge-Kutta del orden especificado.

    graficar():
        Genera una gráfica de la solución numérica.

    Examples:
    -------
    from mnspy import RungeKutta
    import numpy as np

    def g(x, y):
        return -2 * x ** 3 + 12 * x ** 2 - 20 * x + 8.5

    def exac_g(x):
        return -0.5 * x ** 4 + 4 * x ** 3 - 10 * x ** 2 + 8.5 * x + 1

    rk = RungeKutta(g, 0, 4, 1, 0.5, a_2='punto_medio', sol_exacta=exac_g)
    rk.graficar()
    print(rk.y)

    rk = RungeKutta(g, 0, 4, 1, 0.5, orden=5, sol_exacta=exac_g)
    rk.graficar()
    print(rk.y)

    def f(x, y):
        return 4 * np.exp(0.8 * x) - 0.5 * y

    def exac_f(x):
        return (4 / 1.3) * (np.exp(0.8 * x) - np.exp(-0.5 * x)) + 2 * np.exp(-0.5 * x)

    rk = RungeKutta(f, 0, 4, 2, 1, a_2='punto_medio', sol_exacta=exac_f)
    rk.graficar()
    print(rk.y)

    def f(x, y):
        return -2 * x * y

    def ex(x):
        return 2 * np.exp(-x ** 2)

    rk = RungeKutta(f, 0, 3, 2, 0.25, orden=4, sol_exacta=ex)
    rk.graficar()
    print(rk.y)
    """

    def __init__(self, f: callable, x_i: float, x_f: float, y_i: float, h: float, orden: int = 2,
                 a_2: float | str = 'ralston', sol_exacta: callable = None):
        """Constructor de la clase RungeKutta

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
        orden : int, optional
            Orden del método de Runge-Kutta (2, 3, 4 o 5). Por defecto es 2.
        a_2 : float | str, optional
            Parámetro para los métodos de orden 2. Puede ser un valor numérico
            o un string para métodos específicos: 'heun' (a2=1/2),
            'punto_medio' (a2=1), o 'ralston' (a2=2/3). Por defecto es 'ralston'.
        sol_exacta : callable, optional
            Función de la solución exacta para graficar y comparar, por defecto ``None``.
        """
        super().__init__(f=f, x_i=x_i, x_f=x_f, y_i=y_i, h=h, sol_exacta=sol_exacta)
        self.orden = orden
        self._a_2 = a_2
        if self.orden == 2:
            if a_2 == 'heun':
                self._a_2 = 1 / 2
                self._metodo = 'Heun, a2 = 1/2'
            elif a_2 == 'punto_medio':
                self._a_2 = 1
                self._metodo = 'Punto medio, a2 = 1'
            elif a_2 == 'ralston':
                self._a_2 = 2 / 3
                self._metodo = 'Ralston, a2 = 2 / 3'
            elif isinstance(a_2, (int, float)):
                self._a_2 = a_2
                self._metodo = 'a2 = ' + str(a_2)
            else:
                print('Nombre de método no valido')
                quit()
        else:
            self._metodo = 'orden = ' + str(self.orden)
        self._calcular()

    def _calcular(self):
        """Soluciona la EDO por el método de Runge-Kutta del orden especificado.

        Returns
        -------
        None
        """
        self.y[0] = self.y_i
        if self.orden == 2:
            # Método genérico de Runge-Kutta de 2do orden
            a_1 = 1 - self._a_2
            p_1 = 1 / 2 / self._a_2
            q_11 = p_1
            for i in range(len(self.x) - 1):
                k_1 = self.f(self.x[i], self.y[i])
                k_2 = self.f(self.x[i] + p_1 * self.h, self.y[i] + q_11 * k_1 * self.h)
                self.y[i + 1] = self.y[i] + (a_1 * k_1 + self._a_2 * k_2) * self.h
        elif self.orden == 3:
            # Método clásico de Runge-Kutta de 3er orden
            for i in range(len(self.x) - 1):
                k_1 = self.f(self.x[i], self.y[i])
                k_2 = self.f(self.x[i] + self.h / 2, self.y[i] + k_1 * self.h / 2)
                k_3 = self.f(self.x[i] + self.h, self.y[i] - k_1 * self.h + 2 * k_2 * self.h)
                self.y[i + 1] = self.y[i] + (k_1 + 4 * k_2 + k_3) * self.h / 6
        elif self.orden == 4:
            # Método clásico de Runge-Kutta de 4to orden
            for i in range(len(self.x) - 1):
                k_1 = self.f(self.x[i], self.y[i])
                k_2 = self.f(self.x[i] + self.h / 2, self.y[i] + k_1 * self.h / 2)
                k_3 = self.f(self.x[i] + self.h / 2, self.y[i] + k_2 * self.h / 2)
                k_4 = self.f(self.x[i] + self.h, self.y[i] + k_3 * self.h)
                self.y[i + 1] = self.y[i] + (k_1 + 2 * k_2 + 2 * k_3 + k_4) * self.h / 6
        elif self.orden == 5:
            # Método de Runge-Kutta-Butcher de 5to orden
            for i in range(len(self.x) - 1):
                k_1 = self.f(self.x[i], self.y[i])
                k_2 = self.f(self.x[i] + self.h / 4, self.y[i] + k_1 * self.h / 4)
                k_3 = self.f(self.x[i] + self.h / 4, self.y[i] + k_1 * self.h / 8 + k_2 * self.h / 8)
                k_4 = self.f(self.x[i] + self.h / 2, self.y[i] - k_2 * self.h / 2 + k_3 * self.h)
                k_5 = self.f(self.x[i] + 3 * self.h / 4, self.y[i] + 3 * k_1 * self.h / 16 + 9 * k_4 * self.h / 16)
                k_6 = self.f(self.x[i] + self.h, self.y[i] - 3 * k_1 * self.h / 7 + 2 * k_2 * self.h / 7 +
                              12 * k_3 * self.h / 7 - 12 * k_4 * self.h / 7 + 8 * k_5 * self.h / 7)
                self.y[i + 1] = self.y[i] + (7 * k_1 + 32 * k_3 + 12 * k_4 + 32 * k_5 + 7 * k_6) * self.h / 90
        else:
            print('Orden de RK no valido')
            quit()

    def graficar(self):
        """Presenta la gráfica de la solución de la ecuación diferencial.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        plt.plot(self.x, self.y, color='g', lw=2, marker='o',
                 label='Método de Runge Kutta orden = ' + str(self.orden))
        plt.title('Método de Runge Kutta ' + '(' + self._metodo + ')')
        self._graficar_datos()


def main():
    """Función principal para demostración."""
    def g(x, y):
        return -2 * x ** 3 + 12 * x ** 2 - 20 * x + 8.5

    def exac_g(x):
        return -0.5 * x ** 4 + 4 * x ** 3 - 10 * x ** 2 + 8.5 * x + 1

    rk = RungeKutta(g, 0, 4, 1, 0.5, a_2='punto_medio', sol_exacta=exac_g)
    rk.graficar()
    print(rk.y)

    rk = RungeKutta(g, 0, 4, 1, 0.5, orden=5, sol_exacta=exac_g)
    rk.graficar()
    print(rk.y)

    def f(x, y):
        return 4 * np.exp(0.8 * x) - 0.5 * y

    def exac_f(x):
        return (4 / 1.3) * (np.exp(0.8 * x) - np.exp(-0.5 * x)) + 2 * np.exp(-0.5 * x)

    rk = RungeKutta(f, 0, 4, 2, 1, a_2='punto_medio', sol_exacta=exac_f)
    rk.graficar()
    print(rk.y)

    def f(x, y):
        return -2 * x * y

    def ex(x):
        return 2 * np.exp(-x ** 2)

    rk = RungeKutta(f, 0, 3, 2, 0.25, orden=4, sol_exacta=ex)
    rk.graficar()
    print(rk.y)


if __name__ == '__main__':
    main()
