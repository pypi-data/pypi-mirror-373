from mnspy.interpolación import Interpolacion
from mnspy.ecuaciones_algebraicas_lineales import Tridiagonal, EcuacionesAlgebraicasLineales
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Math
plt.rcParams.update(plt.rcParamsDefault)

class SplineCubica(Interpolacion):
    """Calcula la interpolación por trazadores (splines) cúbicos naturales.

    Este método ajusta polinomios cúbicos por tramos entre los puntos de datos,
    asegurando que la función resultante, su primera derivada y su segunda
    derivada sean continuas en los puntos de unión (nodos).

    Para los splines naturales, se asume que la segunda derivada en los
    extremos es cero.

    Attributes
    ----------
    x : np.ndarray
        Array con los datos de la variable independiente.
    y : np.ndarray
        Array con los datos de la variable dependiente.

    Methods
    -------
    evaluar(x: float):
        Evalúa la interpolación del spline cúbico en un punto `x`.
    obtener_polinomio():
        Genera la expresión simbólica de la función a tramos.
    graficar():
        Genera una gráfica de los splines cúbicos.

    Examples
    -------
    from mnspy import SplineCubica
    import numpy as np

    T = np.array([-40., 0., 20., 50., 100, 150, 200, 250, 300, 400, 500])
    rho = np.array([1.52, 1.29, 1.2, 1.09, 0.95, 0.84, 0.75, 0.68, 0.62, 0.53, 0.46])
    sc = SplineCubica(T, rho)
    print(sc.evaluar(350))
    sc.graficar(350)

    x = np.array([1., 4., 5, 6.])
    y = np.log(x)
    inter = SplineCubica(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)
    """

    def __init__(self, x: np.ndarray, y: np.ndarray):
        """Constructor de la clase SplineCubica.

        Parameters
        ----------
        x: np.ndarray
            Array con los datos de la variable independiente
        y: np.ndarray
            Array con los datos de la variable dependiente
        """
        super().__init__(x, y)
        self._coeficientes = self._calcular_coeficientes()

    def _calcular_coeficientes(self):
        """Calcula los coeficientes de los polinomios cúbicos.

        Resuelve un sistema de ecuaciones tridiagonal para encontrar las segundas
        derivadas en cada nodo, y a partir de ellas, calcula el resto de
        coeficientes (a, b, c, d) para cada tramo del spline.

        Returns
        -------
        dict
            Un diccionario con los arrays de coeficientes 'a', 'b', 'c', 'd'.
        """
        # Paso 1: Calcular los anchos de los intervalos (h) y las pendientes (df)
        h = np.zeros((self._n - 1))
        for i in range(self._n - 1):
            h[i] = self._x[i + 1] - self._x[i]
        df = np.zeros((self._n - 1))
        for i in range(self._n - 1):
            df[i] = (self._y[i + 1] - self._y[i]) / h[i]

        # Paso 2: Montar el sistema de ecuaciones tridiagonal para las segundas derivadas (c)
        e = np.zeros(self._n)
        f = np.zeros(self._n)
        f[0] = 1
        f[self._n - 1] = 1
        g = np.zeros(self._n)
        r = np.zeros(self._n)
        for i in range(1, self._n - 1):
            e[i] = h[i - 1]
            f[i] = 2 * (h[i - 1] + h[i])
            g[i] = h[i]
            r[i] = 3 * (df[i] - df[i - 1])

        # Paso 3: Resolver el sistema para obtener los coeficientes c (c_i = f''(x_i)/2)
        if EcuacionesAlgebraicasLineales is not None:
            tri = Tridiagonal(e, f, g, r)
            c = np.ravel(tri.x)  # Convierte matriz a array
        else:
            # Fallback o manejo de error si Tridiagonal no está disponible
            raise ImportError("La clase Tridiagonal no está disponible para resolver el sistema.")

        # Paso 4: Calcular los coeficientes b y d a partir de c
        b = np.zeros((self._n - 1))
        for i in range(self._n - 1):
            b[i] = (self._y[i + 1] - self._y[i]) / h[i] - (h[i] / 3) * (2 * c[i] + c[i + 1])
        d = np.zeros((self._n - 1))
        for i in range(self._n - 1):
            d[i] = (c[i + 1] - c[i]) / 3 / h[i]

        return {'a': self._y, 'b': b, 'c': c, 'd': d}

    def evaluar(self, x: float) -> float | str:
        """Evalúa el spline cúbico en un punto `x`.

        Parameters
        ----------
        x: float
            Valor de la variable independiente en el que se desea interpolar.

        Returns
        -------
        float or str
            El valor interpolado y(x), o un mensaje de error si `x` está
            fuera del rango.
        """
        if (x < self._x[0]) or (x > self._x[self._n - 1]):
            return "Valor de entrada fuera del rango de la tabla"

        # Encuentra el intervalo correcto para evaluar el polinomio
        i_2 = 0
        for i in range(self._n):
            if x == self._x[i]:
                return float(self._y[i])
            elif self._x[i] > x:
                i_2 = i - 1
                break
        # Evalúa el polinomio cúbico para ese intervalo
        dx = x - self._x[i_2]
        y_int = self._coeficientes['a'][i_2] + self._coeficientes['b'][i_2] * dx + self._coeficientes['c'][i_2] * dx ** 2 + self._coeficientes['d'][i_2] * dx ** 3
        return float(y_int)

    def obtener_polinomio(self):
        """Genera una representación en LaTeX de la función a tramos.

        Returns
        -------
        Retorna la lista de polinomios de grado 3 que pasa por los puntos de los datos de la interpolación
        """
        c = self._coeficientes['c']
        b = self._coeficientes['b']
        d = self._coeficientes['d']

        texto_latex = r'\begin{cases}'
        for i in range(self._n - 1):
            a_0 = self._y[i] - b[i] * self._x[i] + c[i] * self._x[i] ** 2 - d[i] * self._x[i] ** 3
            a_1 = b[i] - 2 * c[i] * self._x[i] + 3 * d[i] * self._x[i] ** 2
            a_2 = c[i] - 3 * d[i] * self._x[i]
            a_3 = d[i] * self._x[i]
            sa_0 = sa_1 = sa_2 = '+'
            if a_0 < 0:
                sa_0 = ''
            if a_1 < 0:
                sa_1 = ''
            if a_2 < 0:
                sa_2 = ''
            if a_3 != 0:
                texto_latex += '{:.8G}'.format(a_3) + 'x^{3}'
            if a_2 != 0:
                texto_latex += sa_2 + '{:.8G}'.format(a_2) + 'x^{2}'
            if a_1 != 0:
                texto_latex += sa_1 + '{:.8G}'.format(a_1) + 'x'
            if a_0 != 0:
                texto_latex += sa_0 + '{:.8G}'.format(a_0)
            if i == self._n - 2:
                texto_latex += r' & ' + str(self._x[i]) + r' \leq  x \leq ' + str(self._x[i + 1]) + r'\\'
            else:
                texto_latex += r' & ' + str(self._x[i]) + r' \leq  x < ' + str(self._x[i + 1]) + r'\\'
        texto_latex += r'\end{cases}'
        return display(Math(texto_latex))

    def graficar(self, x: float) -> None:
        """Genera una gráfica de los trazadores cúbicos.

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
        x_list = np.linspace(x_min, x_max, 50)
        y_list = list(map(self.evaluar, x_list))
        plt.scatter(x, y, c='r', lw=2, label='Interpolación Spline Cúbica')
        plt.plot(x_list, y_list, linestyle='dashed', c='k', lw=1, label='Polinomio')
        plt.annotate('$(' + str(x) + r',\,' + str(y) + ')$', (x, y), c='r', alpha=0.9, textcoords="offset points",
                     xytext=(0, 10), ha='center')
        super()._graficar_datos()


def main():
    T = np.array([-40., 0., 20., 50., 100, 150, 200, 250, 300, 400, 500])
    rho = np.array([1.52, 1.29, 1.2, 1.09, 0.95, 0.84, 0.75, 0.68, 0.62, 0.53, 0.46])
    sc = SplineCubica(T, rho)
    print(sc.evaluar(350))
    sc.graficar(350)

    x = np.array([1., 4., 5, 6.])
    y = np.log(x)
    inter = SplineCubica(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)


if __name__ == '__main__':
    main()
