from mnspy.derivada import Derivada
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Richardson(Derivada):
    """Calcula la derivada numérica utilizando la extrapolación de Richardson.

    Este método mejora la precisión de las fórmulas de diferencias finitas
    combinando dos estimaciones de la derivada calculadas con diferentes
    tamaños de paso (h y h/2).

    Attributes
    ----------
    f : callable
        Función a derivar.
    h : float
        Tamaño del paso base para el cálculo.
    modo : str
        Método de diferencia finita: 'adelante', 'atrás' o 'centrada'.
    orden_error : str
        Orden de error de la aproximación a mejorar.
    derivada: float
        Resultado del último cálculo de la derivada.

    Methods
    -------
    derivar(x: float):
        Calcula la derivada en el punto `x` usando extrapolación.
    graficar():
        Grafica la función y la línea tangente en un punto dado.

    Examples
    -------
    from mnspy import Richardson
    import numpy as np

    def g(x):
        return (x + 7) * (x + 2) * (x - 4) * (x - 12) / 100

    der = Derivada(g, orden='h2')
    der.derivar(2)
    print(der.derivada)

    ri = Richardson(g, orden='h2')
    ri.derivar(2)
    ri.graficar(2)
    print(ri.derivada)
    """
    def __init__(self, f: callable, n: int = 1, h: float = 1e-3, orden: str = 'h', modo: str = 'adelante'):
        """Constructor de la clase Richardson.

        Parameters
        ----------
        f : callable
            Función a derivar, f(x).
        n : int, optional
            Grado de la derivada (1, 2, 3 o 4). Por defecto es 1.
        h : float, optional
            Tamaño del paso base. Por defecto es 1e-3.
        orden : str, optional
            Orden de error de la aproximación.
            - Para modo 'adelante' y 'atrás': 'h' o 'h2'.
            - Para modo 'centrada': 'h2' o 'h4'.
            Por defecto es 'h'.
        modo : str, optional
            Método de diferencia finita a utilizar: 'adelante', 'atrás' o 'centrada'.
            Por defecto es 'adelante'.
        """
        super().__init__(f, n, h, orden, modo)

    def derivar(self, x: float):
        """Calcula la derivada en `x` usando la extrapolación de Richardson.

        Parameters
        ----------
        x : float
            Punto en el que se evaluará la derivada.
        """
        # Guarda el h original
        h_original = self._h

        # Calcula D(h/2)
        self._h = h_original / 2.0
        super().derivar(x)
        d_h2 = self.derivada

        # Calcula D(h)
        self._h = h_original
        super().derivar(x)
        d_h1 = self.derivada

        # Aplica la fórmula de extrapolación de Richardson para O(h^2)
        self.derivada = (4 * d_h2 - d_h1) / 3

    def graficar(self, x: float, x_min: float = None, x_max: float = None, delta: float = 10) -> None:
        """Grafica la función y la línea tangente mejorada por Richardson.

        Parameters
        ----------
        x: float
            posición en x en que se dibujará la derivada
        x_min: float
            valor mínimo de la gráfica en x
        x_max: float
            valor máximo de la gráfica en x
        delta: float, optional
            Rango de la gráfica en x si `x_min` y `x_max` no se especifican.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        n = self._n
        self._n = 1
        self.derivar(x)
        self._n = n
        if x_min is None:
            x_min = x - delta
        if x_max is None:
            x_max = x + delta
        if self._orden == 'h':
            orden = r'$\mathcal{O}(h^2)$'
        elif self._orden == 'h2':
            orden = r'$\mathcal{O}(h^4)$'
        else:
            orden = r'$\mathcal{O}(h^6)$'
        y = self._f(x)
        x_list = np.linspace(x_min, x_max, 100)
        y_list = self._f(x_list)
        plt.scatter(x, y, c='r', lw=2, label=f'Punto ({x}, {self._f(x):.4f})')
        plt.plot(x_list, y_list, linestyle='-', c='b', lw=2, label='$f(x)$')
        plt.title(f'Derivada = {self.derivada:.8f}')
        plt.suptitle(
            f'Derivada Richardson, $h_1$={self._h}, $h_2$={self._h / 2}, modo={self._modo}, nuevo orden={orden}')
        plt.axline((x, y), slope=self.derivada, linestyle='dashed', c='r', lw=2,
                   label='Derivada')
        plt.grid()
        plt.legend()
        plt.show()


def main():
    """Función principal para demostración."""
    def g(x):
        return (x + 7) * (x + 2) * (x - 4) * (x - 12) / 100

    der = Derivada(g, orden='h2')
    der.derivar(2)
    print(der.derivada)

    ri = Richardson(g, orden='h2')
    ri.derivar(2)
    ri.graficar(2)
    print(ri.derivada)


if __name__ == '__main__':
    main()
