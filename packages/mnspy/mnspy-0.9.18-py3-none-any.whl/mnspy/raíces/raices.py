import numpy as np
import matplotlib.pyplot as plt
from mnspy.utilidades import es_notebook
from tabulate import tabulate
import math
import sys
plt.rcParams.update(plt.rcParamsDefault)

class Raices:
    """
    Clase base para las demás clases que implementan métodos para el cálculo de raíces de ecuaciones.

    Attributes
    ----------
    f : callable
        Función a la que se le hallará la raíz.
    tol : float | int
        Máxima tolerancia del error.
    max_iter : int
        Número máximo de iteraciones permitido.
    x : float
        La última aproximación calculada de la raíz.
    _tabla : dict
        Diccionario que almacena los datos de cada iteración.
    _converge : bool
        Indica si el método convergió a una solución.

    Methods
    -------
    formato_tabla(llave: str, fmt: str):
        Ajusta el formato de una columna en la tabla de resultados.
    generar_tabla(tablefmt:str = None):
        Genera y muestra una tabla con los resultados de las iteraciones.
    _agregar_iteracion():
        Agrega los datos de la iteración actual al diccionario `_tabla`.
    _fin_iteracion():
        Retorna un booleano de acuerdo si debe finalizar las iteraciones
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Realiza la gráfica del cálculo de la raíz según el método.
    _derivada(x: float, h: float):
        Cálculo de la derivada numérica de la función.
    solucion():
        Muestra un resumen de la solución final.

    Examples:
    -------
    from mnspy import Raices
    import numpy as np

    def f(x):
        return 667.38 * (1 - np.exp(-0.146843 * x)) / x - 40

    graf = Raices(f, 12, 16)
    graf.generar_tabla()
    graf.graficar()

    def z(x):
        return x ** 2 - 9

    graf = Raices(z, 0, 5)
    graf.graficar()
    """

    def __init__(self, f: callable, x_min: float = None, x_max: float = None, tol: float | int = 1e-3,
                 max_iter: int = 20, tipo_error: str = '%'):
        """
        Constructor de la clase base raíces.

        Parameters
        ----------
        f: callable
            Función a la que se le hallará la raíz, f(x).
        x_min: float, optional
            Límite inferior del intervalo para métodos cerrados.
        x_max: float, optional
            Límite superior del intervalo para métodos cerrados.
        tol: float | int, optional
            Máxima tolerancia del error.
        max_iter: int, optional
            Número máximo de iteraciones permitido.
        tipo_error: str, optional
            Tipo de error a utilizar para la convergencia:
            - ``'%'``: Error relativo porcentual (por defecto).
            - ``'/'``: Error relativo.
            - ``'n'``: Número de cifras significativas. εs = (0.5 * 10^(2-n)) %  (Scarborough, 1966)
        """
        self._f = f
        self._tol = tol
        # tipo de error es '%' , '/' o 'n'
        match tipo_error:
            case "%":
                self._error_porcentual = True
            case "/":
                self._error_porcentual = False
            case "n":
                self._tol = 0.5 * 10 ** (2 - tol)
                self._error_porcentual = True
            case _:
                print("Tipo de error no valido, las opciones son: '%', '/', 'n'")
                sys.exit()
        self._max_iter = max_iter
        self._x_min = x_min
        self._x_max = x_max
        self.x = 0
        self._x_0 = None
        self._x_1 = None
        self._tabla = {'x_min': [], 'x_max': [], 'x': [], 'Ea': []}
        self._fmt = {'iter': 'd', 'x_l': '.5f', 'x_u': '.5f', 'x': '.10f', 'f': '.8f', 'E_a': '0.5%', 'E_t': '0.5%'}
        self._converge = False
        self._rango = x_min, x_max
        plt.ioff()  # deshabilitada interactividad matplotlib

    def formato_tabla(self, col: str, fmt: str) -> None:
        """
        Ajusta el formato de presentación de los datos en las tablas.

        Por defecto el formato es
        {'iter': 'd', 'x_l': '.5f', 'x_u': '.5f', 'x': '.10f', 'f': '.8f', 'E_a': '0.5%', 'E_t': '0.5%'}

        Parameters
        ----------
        col : str
            Nombre de la columna a la que se le ajustará el formato (e.g., 'x', 'E_a').
        fmt: str
            Formato a aplicar, como '.5f' o '0.5%'.

        Returns
        -------
        None
        """
        if col == 'x_r' or col == 'x_i':
            col = 'x'
        self._fmt[col] = fmt

    def generar_tabla(self, valor_real: float = None, tablefmt=None):
        """
        Genera y muestra una tabla con los resultados de las iteraciones.

        Utiliza el paquete `tabulate` para formatear la salida. En un entorno
        de notebook, la tabla se renderiza como HTML.

        Parameters
        ----------
        valor_real : float, optional
            Si se proporciona, se calcula y muestra el error verdadero (`E_t`) en la tabla.
        tablefmt : str, optional
            Formato de la tabla según `tabulate`. Por defecto, es 'html' en
            notebooks y 'simple' en otros entornos.

        Returns
        -------
        DisplayHandle or None
            Un objeto `DisplayHandle` de IPython si se ejecuta en un notebook,
            o `None` si se imprime en la consola.
        """
        if type(self) is Raices:  # Si la clase es Raíces, no tiene método asociado y solo sirve para graficar
            print('No se generó tabla')
            return None
        render_notebook = ['html', 'unsafehtml']
        if self._x_min is not None:
            valores = np.array(
                [self._tabla['x_min'], self._tabla['x_max'], self._tabla['x'], [self._f(val) for val in self._tabla['x']],
                 self._tabla['Ea']]).transpose()
            if es_notebook() and (tablefmt is None or tablefmt in render_notebook):
                if tablefmt is None:
                    tablefmt = 'html'
                if valor_real is None:
                    return tabulate(valores, ['Iteración', '$x_{l}$', '$x_{u}$', '$x_{r}$', r'$f\left(x_{r}\right)$',
                                              r'$\varepsilon_{a}$'], showindex=list(range(1, len(self._tabla['x']) + 1)),
                                    tablefmt=tablefmt, floatfmt=(
                            self._fmt['iter'], self._fmt['x_l'], self._fmt['x_u'], self._fmt['x'], self._fmt['f'],
                            self._fmt['E_a']), colalign=("center",))
                else:
                    e_t = abs((np.array([self._tabla['x']]).transpose() - valor_real) / valor_real)
                    valores = np.hstack((valores, e_t))
                    return tabulate(valores, ['Iteración', '$x_{l}$', '$x_{u}$', '$x_{r}$', r'$f\left(x_{r}\right)$',
                                              r'$\varepsilon_{a}$', r'$\varepsilon_{t}$'],
                                    showindex=list(range(1, len(self._tabla['x']) + 1)), tablefmt=tablefmt, floatfmt=(
                            self._fmt['iter'], self._fmt['x_l'], self._fmt['x_u'], self._fmt['x'], self._fmt['f'],
                            self._fmt['E_a'], self._fmt['E_t']), colalign=("center",))
            else:
                if tablefmt is None:
                    tablefmt = 'simple'
                if valor_real is None:
                    print(tabulate(valores, ['Iteración', 'x_l', 'x_u', 'x_r', 'f(x_r)', 'E_a'],
                                   showindex=list(range(1, len(self._tabla['x']) + 1)), tablefmt=tablefmt,
                                   floatfmt=(
                                       self._fmt['iter'], self._fmt['x_l'], self._fmt['x_u'], self._fmt['x'], self._fmt['f'],
                                       self._fmt['E_a']), colalign=("center",)))
                else:
                    e_t = abs((np.array([self._tabla['x']]).transpose() - valor_real) / valor_real)
                    valores = np.hstack((valores, e_t))
                    print(tabulate(valores, ['Iteración', 'x_l', 'x_u', 'x_r', 'f(x_r)', 'E_a', 'E_t'],
                                   showindex=list(range(1, len(self._tabla['x']) + 1)), tablefmt=tablefmt,
                                   floatfmt=(
                                       self._fmt['iter'], self._fmt['x_l'], self._fmt['x_u'], self._fmt['x'], self._fmt['f'],
                                       self._fmt['E_a'], self._fmt['E_t']), colalign=("center",)))
        else:
            valores = np.array([self._tabla['x'], self._f(np.array(self._tabla['x'])), self._tabla['Ea']]).transpose()
            if es_notebook() and (tablefmt is None or tablefmt in render_notebook):
                if tablefmt is None:
                    tablefmt = 'html'
                if valor_real is None:
                    return tabulate(valores, ['Iteración', '$x_{i}$', r'$f\left(x_{i}\right)$', r'$\varepsilon_{a}$'],
                                    showindex=list(range(1, len(self._tabla['x']) + 1)), tablefmt=tablefmt,
                                    floatfmt=(self._fmt['iter'], self._fmt['x'], self._fmt['f'], self._fmt['E_a']),
                                    colalign=("center",))
                else:
                    e_t = abs((np.array([self._tabla['x']]).transpose() - valor_real) / valor_real)
                    valores = np.hstack((valores, e_t))
                    return tabulate(valores, ['Iteración', '$x_{i}$', r'$f\left(x_{i}\right)$', r'$\varepsilon_{a}$',
                                              r'$\varepsilon_{t}$'], showindex=list(range(1, len(self._tabla['x']) + 1)),
                                    tablefmt=tablefmt,
                                    floatfmt=(
                                        self._fmt['iter'], self._fmt['x'], self._fmt['f'], self._fmt['E_a'],
                                        self._fmt['E_t']),
                                    colalign=("center",))
            else:
                if tablefmt is None:
                    tablefmt = 'simple'
                if valor_real is None:
                    print(tabulate(valores, ['Iteración', 'x_i', 'f(x_i)', 'E_a'],
                                   showindex=list(range(1, len(self._tabla['x']) + 1)), tablefmt=tablefmt,
                                   floatfmt=(self._fmt['iter'], self._fmt['x'], self._fmt['f'], self._fmt['E_a']),
                                   colalign=("center",)))
                else:
                    e_t = abs((np.array([self._tabla['x']]).transpose() - valor_real) / valor_real)
                    valores = np.hstack((valores, e_t))
                    print(tabulate(valores, ['Iteración', 'x_i', 'f(x_i)', 'E_a', 'E_t'],
                                   showindex=list(range(1, len(self._tabla['x']) + 1)), tablefmt=tablefmt,
                                   floatfmt=(
                                       self._fmt['iter'], self._fmt['x'], self._fmt['f'], self._fmt['E_a'],
                                       self._fmt['E_t']),
                                   colalign=("center",)))

    def _agregar_iteracion(self) -> None:
        """
        Agrega los datos de la iteración actual al diccionario `_tabla`.

        Returns
        -------
        None
        """
        self._tabla['x_min'].append(self._x_min)
        self._tabla['x_max'].append(self._x_max)
        self._tabla['x'].append(self.x)
        if len(self._tabla['x']) > 1:
            self._tabla['Ea'].append(math.fabs((self._tabla['x'][-1] - self._tabla['x'][-2]) / self._tabla['x'][-1]))
        else:
            self._tabla['Ea'].append(math.nan)

    def _fin_iteracion(self) -> bool:
        """Verifica si se debe finalizar el proceso iterativo.

        La iteración termina si se alcanza la tolerancia de error deseada
        o si se supera el número máximo de iteraciones.

        Returns
        -------
        bool
            ``True`` si la iteración debe terminar, ``False`` en caso contrario.
        """
        lon = len(self._tabla['x'])
        if lon >= self._max_iter:
            self._converge = False
            return True
        self._agregar_iteracion()
        if self._error_porcentual:
            lon = len(self._tabla['x'])
            if lon > 1:
                if self._tabla['Ea'][-1] * 100 < self._tol:
                    self._converge = True
                    return True
                else:
                    return False
            else:
                return False
        else:
            lon = len(self._tabla['x'])
            if lon > 1:
                if self._tabla['Ea'][-1] < self._tol:
                    self._converge = True
                    return True
                else:
                    return False
            else:
                return False

    def graficar(self, mostrar_sol: bool = False, mostrar_iter: bool = False, mostrar_lin_iter: bool = False,
                 n_puntos: int = 100):
        """Genera la gráfica base para los métodos de búsqueda de raíces.

        Dibuja la función, la solución encontrada y, opcionalmente, los puntos
        de cada iteración.

        Parameters
        ----------
        mostrar_sol : bool, optional
            Si es ``True``, resalta el punto de la solución final.
        mostrar_iter : bool, optional
            Si es ``True``, muestra los puntos de cada iteración.
        mostrar_lin_iter : bool, optional
            Si es ``True``, muestra las líneas auxiliares específicas de cada método.
        n_puntos : int, optional
            Número de puntos para dibujar la curva de la función.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        if self._rango[0] is None or self._rango[1] is None:
            if self._x_1 is None:
                x = np.linspace(min(self._tabla['x'] + [self._x_0]), max(self._tabla['x'] + [self._x_0]), n_puntos)
            else:
                x = np.linspace(min(self._tabla['x'] + [self._x_0, self._x_1]),
                                max(self._tabla['x'] + [self._x_0, self._x_1]),
                                100)
        else:
            x = np.linspace(self._rango[0], self._rango[1], n_puntos)
        y = [self._f(val) for val in x]
        plt.plot(x, y, c='b', lw=2, label='Función')
        if mostrar_iter and len(self._tabla['x']) > 0:
            plt.scatter(self._tabla['x'], [self._f(val) for val in self._tabla['x']], c='g', alpha=0.5,
                        label='Iteraciones', zorder=3)
            for i, dato in enumerate(self._tabla['x']):
                plt.annotate(str(i + 1), (dato, self._f(dato)), c='g', alpha=0.95, textcoords="offset points",
                             xytext=(0, 10),
                             ha='center', zorder=3)
        if mostrar_sol and len(self._tabla['x']) > 0:
            plt.scatter(self.x, self._f(self.x), c='r', marker='o', label='Solución', zorder=4)
        if mostrar_lin_iter:
            if self._x_0 is not None and self._x_1 is None:
                plt.scatter(self._x_0, self._f(self._x_0), c='purple', marker='X', label='Punto inicial', zorder=3)
            if self._x_0 is not None and self._x_1 is not None:
                plt.scatter([self._x_0, self._x_1], [self._f(self._x_0), self._f(self._x_1)], c='purple', marker='X',
                            label='Puntos iniciales', zorder=3)
        plt.grid()
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.axhline(color='black')
        plt.legend()
        plt.show()

    def _derivada(self, x: float, h: float = 0.001) -> float:
        """
        Calcula la derivada numérica de la función en un punto.

        Utiliza una diferencia finita hacia adelante. Es usada por métodos como
        Newton-Raphson cuando no se proporciona una función de derivada analítica.

        Parameters
        ----------
        x: float
            Punto en el que se evaluará la derivada.
        h: float
            Tamaño del paso para la diferencia finita.

        Returns
        -------
        float
            Valor de la derivada numérica de la función en el punto x.
        """
        return (self._f(x + h) - self._f(x)) / h

    def solucion(self):
        """Presenta un resumen de la solución final.

        Returns
        -------
        Tabla con los resultados finales de la iteración.
        """
        if self._converge:
            if es_notebook():
                valores = [['$x$:', self.x], ['$f(x)$:', self._f(self.x)],
                           ['$\\varepsilon_{a}[\\%]$:', self._tabla['Ea'][-1] * 100],
                           ['Número de iteraciones:', len(self._tabla['x'])]]
                return tabulate(valores, tablefmt='html', colalign=('right', 'left'))
            else:
                valores = [['x:', self.x], ['f(x)', self._f(self.x)],
                           ['εa [%]:', self._tabla['Ea'][-1] * 100],
                           ['Número de iteraciones:', len(self._tabla['x'])]]
                print(tabulate(valores, tablefmt='simple', colalign=('right', 'left')))
        else:
            print("***** No converge a una solución en el máximo de iteraciones definidas *****")


def main():
    """Función principal para demostración."""
    def f(x):
        return 667.38 * (1 - np.exp(-0.146843 * x)) / x - 40

    graf = Raices(f, 12, 16)
    graf.generar_tabla()
    graf.graficar()

    def z(x):
        return x ** 2 - 9

    graf = Raices(z, 0, 5)
    graf.graficar()


if __name__ == '__main__':
    main()
