from mnspy.utilidades import es_notebook
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
plt.rcParams.update(plt.rcParamsDefault)

class EcuacionesDiferencialesOrdinarias:
    """Clase base para los métodos de solución de ecuaciones diferenciales ordinarias.

    Esta clase proporciona la estructura y funcionalidad común para todos los
    solucionadores de EDOs, como la inicialización de variables, el manejo
    de la solución exacta para comparación y la generación de tablas y gráficos.

    Attributes
    ----------
    f : callable
        La ecuación diferencial a resolver, en la forma `dy/dx = f(x, y)`.
    x : np.ndarray
        Array con los valores de la variable independiente `x`.
    y : np.ndarray
        Array con los valores de la solución numérica `y(x)`.
    h : float
        Tamaño del paso de integración.
    x_i : float
        Valor inicial de `x`.
    x_f : float
        Valor final de `x`.
    y_i : float
        Condición inicial, valor de `y` en `x_i`.
    sol_exacta : callable, optional
        La función de la solución exacta, `y_exacta(x)`, para comparación.
    """
    def __init__(self, f: callable, x_i: float, x_f: float, y_i: float, h: float, sol_exacta: callable = None):
        """Constructor de la clase EcuacionesDiferencialesOrdinarias

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
        self.f = f
        self.x_i = x_i
        self.x_f = x_f
        self.y_i = y_i
        self.h = h
        self.sol_exacta = sol_exacta
        self.x = np.arange(self.x_i, self.x_f + self.h, self.h)
        self.y = np.zeros(len(self.x))
        self._etiquetas = None
        plt.ioff()  # deshabilitada interactividad matplotlib

    def ajustar_etiquetas(self, etiquetas: list, es_latex: bool = True):
        """Ajusta las etiquetas para la tabla de resultados.

        Parameters
        ----------
        etiquetas : list[str]
            Lista con dos strings para las etiquetas de las columnas 'x' e 'y'.
        es_latex : bool, optional
            Si es ``True``, las etiquetas se interpretarán como código LaTeX.
            Por defecto es ``True``.

        Returns
        -------
        None
        """
        self._etiquetas = {'label': etiquetas, 'es_latex': es_latex}

    def solucion(self):
        """Muestra la solución de la ecuación diferencial en forma de tabla.

        Utiliza `tabulate` para una presentación clara en la consola o en un notebook.

        Returns
        -------
        str or None
            Una tabla HTML para notebooks de Jupyter, o imprime la tabla en la
            consola y retorna ``None``.
        """
        if es_notebook():
            if self._etiquetas is None:
                tabla = {'x': self.x, 'y': self.y}
            else:
                if self._etiquetas['es_latex']:
                    tabla = {'$' + self._etiquetas['label'][0] + '$': self.x,
                             '$' + self._etiquetas['label'][1] + '$': self.y}
                else:
                    tabla = {self._etiquetas['label'][0]: self.x, self._etiquetas['label'][1]: self.y}
            if self.sol_exacta is not None:
                tabla['Solución exacta'] = self.sol_exacta(self.x)
            return tabulate(tabla, tablefmt='html', headers='keys')
        else:
            if self._etiquetas is None:
                tabla = {'x': self.x, 'y': self.y}
            else:
                tabla = {self._etiquetas['label'][0]: self.x, self._etiquetas['label'][1]: self.y}
            if self.sol_exacta is not None:
                tabla['Solución Exacta'] = self.sol_exacta(self.x)
            print(tabulate(tabla, tablefmt='simple', headers='keys'))

    def _graficar_datos(self) -> None:
        """Dibuja la gráfica base, incluyendo la solución exacta si está disponible.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        if self.sol_exacta is not None:
            x = np.linspace(self.x_i, self.x_f, 100)
            y = self.sol_exacta(x)
            plt.plot(x, y, c='b', lw=2, label='Solución Exacta')
        plt.grid()
        plt.legend()
        plt.show()
