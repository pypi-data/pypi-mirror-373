import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Interpolacion:
    """Clase base para los métodos de interpolación.

    Esta clase proporciona la estructura y funcionalidad común para todos los
    métodos de interpolación, como la inicialización de los puntos de datos
    (x, y) y un método base para graficar dichos puntos.

    Attributes
    ----------
    x : np.ndarray
        Array con los datos de la variable independiente.
    y : np.ndarray
        Array con los datos de la variable dependiente.
    n : int
        Número de puntos de datos.

    Methods
    -------
    _graficar_datos():
        Dibuja un gráfico de dispersión con los puntos de datos originales.

    """

    def __init__(self, x: np.ndarray, y: np.ndarray):
        """Constructor de la clase base de Interpolación.

        Parameters
        ----------
        x : np.ndarray
            Array con los datos de la variable independiente
        y : np.ndarray
            Array con los datos de la variable dependiente
        """
        self._x = x
        self._y = y
        self._n = len(self._x)
        if len(self._y) != self._n:
            raise ValueError("Los arrays 'x' e 'y' deben tener la misma longitud.")
        plt.ioff()  # deshabilitada interactividad matplotlib

    def _graficar_datos(self) -> None:
        """Dibuja los puntos de datos originales en un gráfico.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        plt.scatter(self._x, self._y, marker='o', c='b', lw=2, label='Datos', zorder=10)
        plt.grid()
        plt.legend()
        plt.show()
