from mnspy.integrales import Integral
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class TrapezoidalDesigualAcumulado(Integral):
    """Calcula la integral acumulada de un conjunto de datos discretos no
    espaciados uniformemente, utilizando la regla del trapecio.

    Attributes
    ----------
    x: np.ndarray
        Array con los datos de la variable independiente.
    y: np.ndarray
        Array con los datos de la variable dependiente.
    n: int
        Número de puntos de datos.
    integral : np.ndarray
        Array con los valores de la integral acumulada en cada punto.

    Methods
    -------
    graficar():
        Genera una gráfica de los datos originales y su integral acumulada.

    Examples
    -------
    from mnspy import TrapezoidalDesigualAcumulado
    import numpy as np

    x = np.linspace(0, 2 * np.pi, 40)
    y = np.cos(x)
    trap = TrapezoidalDesigualAcumulado(x, y)
    trap.graficar()
    print(trap.integral)
    """
    def __init__(self, x: np.ndarray, y: np.ndarray):
        """Constructor de la clase TrapezoidalDesigualAcumulado

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
        """Calcula la integral acumulada para el conjunto de datos.

        El resultado es un array de la misma longitud que `x` e `y`, donde
        cada elemento `i` es la integral desde `x[0]` hasta `x[i]`.

        Returns
        -------
        None
        """
        # El primer valor de la integral acumulada es siempre cero.
        integral_acumulada = np.zeros(self._n)
        for i in range(1, self._n):
            h = self._x[i] - self._x[i - 1]
            area_trapecio = h * (self._y[i] + self._y[i - 1]) / 2
            integral_acumulada[i] = integral_acumulada[i - 1] + area_trapecio
        self.integral = integral_acumulada

    def graficar(self):
        """Genera una gráfica de los datos y su integral acumulada.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        plt.plot(self._x, self._y, 'o--', color='C0', lw=1, label='Datos Originales')
        plt.plot(self._x, self.integral, 'o-', color='C3', lw=2, label='Integral Acumulada')
        plt.fill_between(self._x, self.integral, color='red', alpha=0.3, label='Regla del Trapecio Desigual Acumulado')
        plt.title(r'$\int{f(x)}\approx ' + str(self.integral[-1]) + '$')
        plt.grid()
        plt.legend()
        plt.show()


def main():
    """Función principal para demostración."""
    x = np.linspace(0, 2 * np.pi, 40)
    y = np.cos(x)
    trap = TrapezoidalDesigualAcumulado(x, y)
    trap.graficar()
    print(trap.integral)


if __name__ == '__main__':
    main()
