from mnspy.interpolación import Interpolacion
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Math
plt.rcParams.update(plt.rcParamsDefault)

class SplineLineal(Interpolacion):
    """Calcula la interpolación por trazadores (splines) lineales.

    Este método conecta puntos de datos consecutivos con segmentos de línea recta,
    creando una función definida por tramos. Es la forma más simple de
    interpolación por trazadores.

    Attributes
    ----------
    x : np.ndarray
        Array con los datos de la variable independiente.
    y : np.ndarray
        Array con los datos de la variable dependiente.

    Methods
    -------
    evaluar(x: float):
        Evalúa la interpolación lineal en un punto `x`.
    obtener_polinomio():
        Genera la expresión simbólica de la función a tramos.
    graficar():
        Genera una gráfica de los trazadores lineales.

    Examples
    -------
    from mnspy import SplineLineal
    import numpy as np

    T = np.array([-40., 0., 20., 50., 100, 150, 200, 250, 300, 400, 500])
    rho = np.array([1.52, 1.29, 1.2, 1.09, 0.95, 0.84, 0.75, 0.68, 0.62, 0.53, 0.46])
    sc = SplineLineal(T, rho)
    print(sc.evaluar(350))
    sc.graficar(350)

    x = np.array([1., 4., 5, 6.])
    y = np.log(x)
    inter = SplineLineal(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)
    """
    def __init__(self, x: np.ndarray, y: np.ndarray):
        """Constructor de la clase SplineLineal.

        Parameters
        ----------
        x: np.ndarray
            Array con los datos de la variable independiente
        y: np.ndarray
            Array con los datos de la variable dependiente
        """
        super().__init__(x, y)

    def evaluar(self, x: float) -> float | str:
        """Evalúa el spline lineal en un punto `x`.

        Encuentra el intervalo [x_i, x_{i+1}] que contiene a `x` y aplica la
        fórmula de interpolación lineal en ese segmento.

        Parameters
        ----------
        x: float
            Valor de la variable independiente en el que se desea interpolar.

        Returns
        -------
        float or str
            El valor interpolado y(x), o un mensaje de error si `x` está
            fuera del rango de los datos.
        """
        if (x < self._x[0]) or (x > self._x[self._n - 1]):
            return "Valor de entrada fuera del rango de la tabla"
        i_0 = 0
        for i in range(self._n):
            if x == self._x[i]:
                return float(self._y[i])
            elif self._x[i] > x:
                i_0 = i - 1
                break
        # Fórmula de la recta que pasa por dos puntos
        y_int = self._y[i_0] + (x - self._x[i_0]) * (self._y[i_0 + 1] - self._y[i_0]) / (
                    self._x[i_0 + 1] - self._x[i_0])
        return float(y_int)

    def obtener_polinomio(self):
        """Genera una representación en LaTeX de la función a tramos.

        Returns
        -------
        IPython.display.Math
            Un objeto Math que renderiza la función a tramos en formato LaTeX.
        """
        texto_latex = r'\begin{cases}'
        for i in range(self._n - 1):
            m = (self._y[i + 1] - self._y[i]) / (self._x[i + 1] - self._x[i])
            b = self._y[i] - m * self._x[i]
            sb_0 = '+'
            if b < 0:
                sb_0 = ''
            if m != 0:
                texto_latex += '{:.8G}'.format(m) + 'x'
            if b != 0:
                texto_latex += sb_0 + '{:.8G}'.format(b)
            if i == self._n - 2:
                texto_latex += r' & ' + str(self._x[i]) + r' \leq  x \leq ' + str(self._x[i + 1]) + r'\\'
            else:
                texto_latex += r' & ' + str(self._x[i]) + r' \leq  x < ' + str(self._x[i + 1]) + r'\\'
        texto_latex += r'\end{cases}'
        return display(Math(texto_latex))

    def graficar(self, x: float) -> None:
        """Genera una gráfica de los trazadores lineales.

        Parameters
        ----------
        x: float
            Valor de `x` a interpolar y resaltar en la gráfica.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        y = self.evaluar(x)
        x_min = float(min(self._x))
        x_max = float(max(self._x))
        x_list = np.linspace(x_min, x_max, 100)
        y_list = list(map(self.evaluar, x_list))
        plt.scatter(x, y, c='r', lw=2, label='Interpolación Spline Lineal')
        plt.plot(x_list, y_list, linestyle='dashed', c='k', lw=1, label='Polinomio')
        plt.annotate('$(' + str(x) + r',\,' + str(y) + ')$', (x, y), c='r', alpha=0.9, textcoords="offset points",
                     xytext=(0, 10), ha='center')
        super()._graficar_datos()


def main():
    T = np.array([-40., 0., 20., 50., 100, 150, 200, 250, 300, 400, 500])
    rho = np.array([1.52, 1.29, 1.2, 1.09, 0.95, 0.84, 0.75, 0.68, 0.62, 0.53, 0.46])
    sc = SplineLineal(T, rho)
    print(sc.evaluar(350))
    sc.graficar(350)

    x = np.array([1., 4., 5, 6.])
    y = np.log(x)
    inter = SplineLineal(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)


if __name__ == '__main__':
    main()
