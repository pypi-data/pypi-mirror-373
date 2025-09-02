from mnspy.utilidades import es_notebook, mostrar_matrix, _generar_matrix
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
from IPython.display import display, Math

plt.rcParams.update(plt.rcParamsDefault)


class EcuacionesAlgebraicasLineales:
    """
    Clase base para las demás clases que implementan métodos para el cálculo de ecuaciones algebraícas lineales.

    Attributes
    ----------
    _A: ndarray
        matrix cuadrada de coeficientes del sistema
    _b: ndarray
        matrix columna de términos independientes
    _aumentada: ndarray
        matrix combinanada para solución del sistema de ecuaciones lineales
    _etiquetas: dict[str:list[str], str: bool]
        diccionario con etiquetas de la solución
        key: 'label' contiene una lista de etiquetas de la solución
        key: 'es_latex' un boleano que define si el string es en formato Latex o no
    _n: int
        número de filas de la matrix _A
    _m: int
        número de columnas de la matrix _A
    _pivote: ndarray
        Solo se usa en la Descomposición LU y es una matrix cuadrada de pivotes
    x: ndarray
        matrix columna de la solución del sistema de acuaciones lineales

    Methods
    -------
    graficar():
        presenta la solución gráfica del sistema de ecuaciones, solo aplica para un sistema de 2x2

    eliminacion_gauss_jordan():
        ejecuta la eliminación de Gauss-Jordan a la matrix self._aumentada

    eliminacion_adelante():
        ejecuta la eliminación hacia adelante a la matrix self._aumentada, usada en el método de Gauss

    sustitucion_atras():
        ejecuta la sustitución hacia atrás a la matrix self._aumentada, usada en el método de Gauss

    sustitucion_adelante():
        ejecuta la sustitución hacia adelante a la matrix self._aumentada, usada en los métodos de descomposición
        de Cholesky y en la descomposición LU

    solucion():
        Presenta los resultados de la solución del sistema de ecuaciones

    Examples:
    -------
    from mnspy import EcuacionesAlagebraicasLineales
    from mnspy.utilidades import mostrar_matrix
    import numpy as np

    A = np.matrix('3 2;-1 2')
    mostrar_matrix(A)
    b = np.matrix('18 ; 2')
    sol = EcuacionesAlagebraicasLineales(A, b)
    sol.mostrar_A()
    sol.mostrar_b()
    sol.graficar()
    sol.mostrar_sistema()
    """

    def __init__(self, A: np.ndarray, b: np.ndarray):
        """Constructor de la clase base EcuacionesAlagebraicasLineales

        Parameters
        ----------
        A: ndarray
            Matrix de los coeficientes del sistema de ecuaciones
        b: ndarray
            Vector columna de los terminos independiantes
        """
        self._A = A.astype(np.double)
        self._b = b.astype(np.double)
        self._n, self._m = self._A.shape  # Se obtiene las dimensiones
        self.x = np.zeros(self._b.shape)
        # self.x = np.matrix(self.x)
        self._aumentada = np.hstack((self._A, self._b))
        self._etiquetas = None
        self._pivote = np.eye(self._n)  # Solo se usa en la Descomposición LU
        plt.ioff()  # deshabilitada interactividad matplotlib

    def graficar(self, x_min: float = None, x_max: float = None, max_rango: float = 10.0):
        """

        Parameters
        ----------
        x_min : float
            valor mínimo en x de la gráfica, por defecto es None
        x_max : float
            valor máximo en x de la gráfica, por defecto es None
        max_rango : float
            si alguno de los valores x_min o x_max es None, el rango en x de la gráfica sería max_rango con
            la solución en el centro

        Returns
        -------
        gráfica usando el paquete matplotlib
        """
        if self._A.shape[0] == 2 and self._A.shape[1] == 2:
            def f1(var):
                return -(self._A[0, 0] / self._A[0, 1]) * var + self._b[0, 0] / self._A[0, 1]

            def f2(var):
                return -(self._A[1, 0] / self._A[1, 1]) * var + self._b[1, 0] / self._A[1, 1]

            singular = False
            div = self._A[1, 0] / self._A[1, 1] - self._A[0, 0] / self._A[0, 1]
            if div != 0:
                sol_x = (self._b[1, 0] / self._A[1, 1] - self._b[0, 0] / self._A[0, 1]) / div
            else:
                sol_x = 0
                singular = True
            sol_y = f1(sol_x)
            if x_min is None or x_max is None:
                x_min = sol_x - max_rango / 2
                x_max = sol_x + max_rango / 2
            x = np.linspace(x_min, x_max, 100)
            y_1 = f1(x)
            y_2 = f2(x)
            plt.plot(x, y_1, c='b', lw=2, label='$f_{1}(x)$')
            plt.plot(x, y_2, c='g', lw=2, label='$f_{2}(x)$')
            if not singular:
                plt.scatter(sol_x, sol_y, c='r', lw=2, label='Solución')
                plt.annotate('$(' + str(sol_x) + r',\,' + str(sol_y) + ')$', (sol_x, sol_y), c='r', alpha=0.9,
                             textcoords="offset points",
                             xytext=(0, 10), ha='center')
            plt.grid()
            plt.legend()
            plt.show()
        else:
            print('Solo gráfica sistemas de ecuaciones de 2 x 2')

    def eliminacion_gauss_jordan(self):
        """
        aplica el algoritmo de Gauss-Jordan sobre la matrix _aumentada

        Returns
        -------
        None
        """
        for k in range(self._n):
            self._pivoteo_parcial(k)
            # Normalización de la fila
            self._aumentada[k, k:] /= self._aumentada[k, k]
            for i in range(self._n):
                if i != k:
                    self._aumentada[i, k:] -= self._aumentada[i, k] * self._aumentada[k, k:]

    def eliminacion_adelante(self, pivote_parcial: bool = False, guardar_factores: bool = False):
        """Ejecuta la eliminación hacia adelante a la matrix _aumentada

        Parameters
        ----------
        pivote_parcial: bool
            Si es verdadero aplica elimicación hacia adelante de Gauss con pivote parcial a la matrix _aumentada,
            en caso de ser falso no aplica el pivote parcial
        guardar_factores: bool
            Si es verdadero aplica eliminación hacia adelante de Gauss a la matrix _aumentada, guardando los valores
            en la matrix, es usada por la Descomposición LU, en caso de ser falso no guarda los valores
        Returns
        -------
        None
        """
        for k in range(self._n - 1):
            if pivote_parcial:
                self._pivoteo_parcial(k)
            for i in range(k + 1, self._n):
                factor = self._aumentada[i, k] / self._aumentada[k, k]
                self._aumentada[i, k:] = self._aumentada[i, k:] - factor * self._aumentada[k, k:]
                if guardar_factores:
                    self._aumentada[i, k] = factor

    def sustitucion_atras(self) -> np.matrix | np.ndarray:
        """Ejecuta la sustitució hacia atrás a la matrix _aumentada

        Returns
        -------
        ndarray que corresponde al vector columna del resultado de la sustitución hacia atrás
        """
        x = np.zeros([self._n, 1])  # Se crea array en cero
        # x = np.matrix(x)  # Se convierte a matrix
        x[self._n - 1] = self._aumentada[self._n - 1, self._n] / self._aumentada[self._n - 1, self._n - 1]
        for i in range(self._n - 2, -1, -1):
            x[i] = (self._aumentada[i, self._n] - np.matmul(self._aumentada[[i], i + 1:self._n],
                                                            x[i + 1:self._n, [0]])) / \
                   self._aumentada[i, i]
        return x

    def sustitucion_adelante(self) -> np.matrix | np.ndarray:
        """Ejecuta la sustitució hacia adelante a la matrix _aumentada

        Returns
        -------
        ndarray que corresponde al vector columna del resultado de la sustitución hacia adelante
        """
        x = np.zeros([self._n, 1])  # Se crea array en cero
        # x = np.matrix(x)  # Se convierte a matrix
        # el término aii=1 para LU
        x[0] = self._aumentada[0, self._n] / self._aumentada[0, 0]
        for i in range(1, self._n):
            x[i] = (self._aumentada[i, self._n] - np.matmul(self._aumentada[[i], 0:i + 1], x[0:i + 1, [0]])) / \
                   self._aumentada[i, i]
        return x

    def _pivoteo_parcial(self, fila: int) -> None:
        """Realiza un pivoteo parcial al número de la fila indicada en la matrix _aumentada, busca hacia adelante
        la fila que contiene el mayor valor abasoluto para esa diagonal y la intercambia.

        Parameters
        ----------
        fila: int
            Fila a la que se le realizará el pivoteo parcial.

        Returns
        -------
        None
        """
        for piv in range(fila + 1, self._n):
            if abs(self._aumentada[piv, fila]) > abs(self._aumentada[fila, fila]):
                self._aumentada[[piv, fila]] = self._aumentada[[fila, piv]]  # Intercambio de filas
                self._pivote[[piv, fila]] = self._pivote[[fila, piv]]  # Intercambio de filas pivote

    def solucion(self):
        """Muestra la solución del sistema de ecuaciones lineales de acuerdo a las etiquetas definidas

        Returns
        -------
        Tabla de resultados usando el paquete tabulate
        """
        if es_notebook():
            if self._etiquetas is None:
                indice = ['$x_{' + str(i) + '}$' for i in range(self.x.shape[0])]
            else:
                if self._etiquetas['es_latex']:
                    indice = ['$' + label + '$' for label in self._etiquetas['label']]
                else:
                    indice = self._etiquetas['label']
            return tabulate({'Solución': self.x}, headers='keys', showindex=indice, tablefmt='html')
        else:
            if self._etiquetas is None:
                indice = ['x_' + str(i) for i in range(self.x.shape[0])]
            else:
                indice = self._etiquetas['label']
            print(tabulate({'Solución': self.x}, headers='keys', showindex=indice, tablefmt='simple'))

    def ajustar_etiquetas(self, etiquetas: list, es_latex: bool = True):
        """Ajusta el nombre de las etiquetas de la solución

        Parameters
        ----------
        etiquetas: list[str]
            Diccionario con etiquetas de la solución
        es_latex: bool
            Un boleano que define si el string es en formato Latex o no

        Returns
        -------
        None
        """
        self._etiquetas = {'label': etiquetas, 'es_latex': es_latex}

    def mostrar_aumentada(self, n_decimal=None):
        """Muestra la matrix aumentada

        Parameters
        ----------
        n_decimal: int
            Número de decimales que tendrá los elementos de la matrix

        Returns
        -------
        Render de la matrix en Latex si se encuentra en un notebook de jupyter o en caso contrario mostrará la
        impresión de la matrix
        """
        i, j = self._aumentada.shape
        return mostrar_matrix(self._aumentada, n_decimal, j - i)

    def mostrar_A(self, n_decimal=None):
        """Muestra la matrix de coeficientes A

        Parameters
        ----------
        n_decimal: int
            Número de decimales que tendrá los elementos de la matrix

        Returns
        -------
        Render de la matrix en Latex si se encuentra en un notebook de jupyter o en caso contrario mostrará la
        impresión de la matrix
        """
        return mostrar_matrix(self._A, n_decimal)

    def mostrar_b(self, n_decimal=None):
        """Muestra la matrix de terminos independientes b

        Parameters
        ----------
        n_decimal: int
            Número de decimales que tendrá los elementos de la matrix

        Returns
        -------
        Render de la matrix en Latex si se encuentra en un notebook de jupyter o en caso contrario mostrará la
        impresión de la matrix
        """
        return mostrar_matrix(self._b, n_decimal)

    def mostrar_sistema(self, n_decimal=None):
        """Muestra el sistema de ecuaciones formado en forma matricial

        Parameters
        ----------
        n_decimal: int
            Número de decimales que tendrá los elementos de la matrix

        Returns
        -------
        Render del sistema de ecuaciones formado en forma matricial en Latex si se encuentra en un notebook de jupyter
        o en caso contrario mostrará la impresión del sistema de ecuaciones
        """
        if n_decimal is None:
            fmt = '{:G}'
        else:
            fmt = '{:.' + str(n_decimal) + 'f}'
        if self._etiquetas is None:
            vec_x = np.array(['x_{' + str(i) + '}' for i in range(self.x.shape[0])], dtype=object).reshape(-1, 1)
            vec_x_plano = np.array(['x_' + str(i) for i in range(self.x.shape[0])], dtype=object).reshape(-1, 1)
        else:
            if self._etiquetas['es_latex']:
                vec_x = np.array([label for label in self._etiquetas['label']], dtype=object).reshape(-1, 1)
            else:
                vec_x = np.array([r'\textrm{' + label + '}' for label in self._etiquetas['label']],
                                 dtype=object).reshape(-1, 1)
            vec_x_plano = np.array([label for label in self._etiquetas['label']], dtype=object).reshape(-1, 1)
        texto_latex = r'\left[\begin{array}{' + 'c' * self._A.shape[1] + '}'
        if es_notebook():
            texto_latex += _generar_matrix(self._A, fmt) + r'\end{array}\right]\cdot\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_x, '{:}') + r'\end{array}\right\}=\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(self._b, fmt) + r'\end{array}\right\}'
            return display(Math(texto_latex))
        else:
            print(np.array2string(self._A, formatter={'float_kind': lambda x: fmt.format(x)}))
            print('x')
            print(vec_x_plano)
            print('=')
            print(np.array2string(self._b, formatter={'float_kind': lambda x: fmt.format(x)}))

    def mostrar_determinantes(self, n_decimal=None):
        """Muestra los determinantes del sistema y el de cada variable (método de cramer), solo para un notebook de jupyter

        Parameters
        ----------
        n_decimal: int
            Número de decimales que tendrá los elementos de la matrix

        Returns
        -------
        Render del sistema de los determinantes en Latex si se encuentra en un notebook de jupyter, en caso contrario
        no se mostrará nada
        """
        if n_decimal is None:
            fmt = '{:}'
        else:
            fmt = '{:.' + str(n_decimal) + 'g}'
        if es_notebook():
            det = np.linalg.det(self._A)
            texto_latex = r'\begin{flalign}\Delta S=\begin{vmatrix}'
            texto_latex += _generar_matrix(self._A, fmt) + r'\end{vmatrix}&=' + fmt.format(det) + r'&&\\'
            for i in range(self._A.shape[1]):
                if self._etiquetas is None:
                    texto_latex += r'\Delta x_{' + str(i) + r'}=\begin{vmatrix}'
                else:
                    texto_latex += r'\Delta ' + self._etiquetas['label'][i] + r'=\begin{vmatrix}'
                mat_i = self._A.copy()
                mat_i[:, [i]] = self._b
                texto_latex += _generar_matrix(mat_i, fmt) + r'\end{vmatrix}&=' + fmt.format(
                    np.linalg.det(mat_i)) + r'&&\\'
            for i in range(self._A.shape[1]):
                if self._etiquetas is None:
                    texto_latex += 'x_{' + str(i) + r'}=\dfrac{\Delta x_{' + str(i) + r'}}{\Delta S}&=' + fmt.format(
                        self.x[i, 0]) + r'&&\\'
                else:
                    texto_latex += self._etiquetas['label'][i] + r'=\dfrac{\Delta ' + self._etiquetas['label'][
                        i] + r'}{\Delta S}&=' + fmt.format(self.x[i, 0]) + r'&&\\'
            texto_latex += r'\end{flalign}'
            return display(Math(texto_latex))
        else:
            return None


def main():
    A = np.array([[3, 2], [-1, 2]])
    mostrar_matrix(A)
    b = np.array([[18], [2]])
    sol = EcuacionesAlgebraicasLineales(A, b)
    sol.mostrar_A()
    sol.mostrar_b()
    sol.graficar()
    sol.mostrar_sistema()


if __name__ == '__main__':
    main()
