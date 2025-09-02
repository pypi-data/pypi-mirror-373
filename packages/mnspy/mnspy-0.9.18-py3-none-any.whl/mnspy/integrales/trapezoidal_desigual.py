from mnspy.integrales import Integral
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class TrapezoidalDesigual(Integral):
    """Calcula la integral de un conjunto de datos discretos no espaciados
    uniformemente, utilizando la regla del trapecio.

    Attributes
    ----------
    x: np.ndarray
        Array con los datos de la variable independiente.
    y: np.ndarray
        Array con los datos de la variable dependiente.
    n: int
        Número de puntos de datos.
    integral : float
        Resultado del cálculo de la integral total.

    Methods
    -------
    graficar():
        Genera una gráfica del proceso de integración.

    Examples
    -------
    from mnspy import TrapezoidalDesigual
    import numpy as np

    x = np.array([0, 0.12, 0.22, 0.32, 0.36, 0.4, 0.44, 0.54, 0.64, 0.7, 0.8])
    y = np.array([0.2, 1.309729, 1.305241, 1.743393, 2.074903, 2.456, 2.842985, 3.507297, 3.181929, 2.363, 0.232])
    trap = TrapezoidalDesigual(x, y)
    trap.graficar()
    print(trap.integral)
    """

    def __init__(self, x: np.ndarray, y: np.ndarray):
        """Constructor de la clase TrapezoidalDesigual

        Parameters
        ----------
        x: np.ndarray
            Array con los datos de la variable independiente.
        y: np.ndarray
            Array con los datos de la variable dependiente.
        """
        super().__init__(x=x, y=y)
        self._calcular()

    def _calcular(self):
        """Calcula la integral sumando el área de cada trapecio individual.

        El resultado se almacena en el atributo `self.integral`.

        Returns
        -------
        None
        """
        suma = 0
        for i in range(self._n - 1):
            # Área de un solo trapecio: ancho * altura_promedio
            h = self._x[i + 1] - self._x[i]
            suma += h * (self._y[i] + self._y[i + 1]) / 2
        self.integral = suma

    def graficar(self):
        """Genera una gráfica del proceso de integración.

        Muestra los puntos de datos y los trapecios utilizados para aproximar el área.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        plt.stem(self._x, self._y, linefmt='C2--', markerfmt='C0o', basefmt='C2-')
        # plt.plot(self._x, self._y, 'o--', color='C2', lw=1)
        plt.fill_between(self._x, self._y, color='green', alpha=0.3, label='Regla del Trapecio Desigual')
        plt.title(r'$\int{f(x)}\approx ' + str(self.integral) + '$')
        self._graficar_datos()


def main():
    """Función principal para demostración."""
    x = np.array([0, 0.12, 0.22, 0.32, 0.36, 0.4, 0.44, 0.54, 0.64, 0.7, 0.8])
    y = np.array([0.2, 1.309729, 1.305241, 1.743393, 2.074903, 2.456, 2.842985, 3.507297, 3.181929, 2.363, 0.232])
    trap = TrapezoidalDesigual(x, y)
    trap.graficar()
    print(trap.integral)


if __name__ == '__main__':
    main()
