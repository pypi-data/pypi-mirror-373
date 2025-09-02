import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Integral:
    """Clase base para los métodos de integración numérica.

    Esta clase proporciona la estructura y funcionalidad común para todos los
    métodos de integración, como la inicialización de variables y la
    graficación de la función o los datos base.

    Attributes
    ----------
    integral : float
        Resultado del cálculo de la integral.
    tipo : str
        Indica si la integral es de una 'función' o de datos 'discretos'.

    Methods
    -------
    _graficar_datos():
        Dibuja la función o los puntos de datos que se están integrando.
    """
    def __init__(self, x: np.ndarray = None, y: np.ndarray = None, f: callable = None, a: float = None,
                 b: float = None, n: int = 100):
        """Constructor de la clase base Integral

        Parameters
        ----------
        x: np.ndarray, optional
            Array con los datos de la variable independiente para una integral discreta.
        y: np.ndarray, optional
            Array con los datos de la variable dependiente para una integral discreta.
        f: callable, optional
            Función a integrar, f(x).
        a: float, optional
            Límite inferior de integración para una función.
        b: float, optional
            Límite superior de integración para una función.
        n: int, optional
            Número de segmentos para los métodos de Newton-Cotes.
        """
        self._tipo = 'ninguno'  # Inicializa el tipo

        # Determina el tipo de integral basado en los argumentos
        if x is not None and y is not None:
            self._tipo = 'discreto'
            self._x = x
            self._y = y
            self._n = len(x)
        elif f is not None and a is not None and b is not None:
            self._tipo = 'función'
            self._f = f
            self._a = a
            self._b = b
            self._n = n
        self.integral = 0
        plt.ioff()  # deshabilitada interactividad matplotlib

    def _graficar_datos(self) -> None:
        """Dibuja la función o los puntos de datos base de la integral.

        Returns
        -------
        None
            Modifica la figura actual de Matplotlib.
        """
        if self._tipo == 'discreto':
            plt.scatter(self._x, self._y, marker='o', c='b', lw=1, label='Puntos')
            #plt.plot(self._x, self._y, 'o--', c='b', lw=1, label='Puntos')
        elif self._tipo == 'función':
            x = np.linspace(self._a, self._b)
            y = self._f(x)
            plt.plot(x, y, c='b', lw=2, label='Función')
        plt.grid()
        plt.legend()
        plt.show()
