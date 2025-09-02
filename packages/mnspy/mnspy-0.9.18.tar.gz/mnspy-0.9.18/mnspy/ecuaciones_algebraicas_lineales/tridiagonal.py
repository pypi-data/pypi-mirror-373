from mnspy.ecuaciones_algebraicas_lineales import EcuacionesAlgebraicasLineales
import numpy as np


class Tridiagonal(EcuacionesAlgebraicasLineales):
    """Clase para la implementación de la solución de un sistema de ecuaciones por el método de Tridiagonal.

    Attributes
    ----------
    _A: ndarray
        matrix cuadrada de coeficientes del sistema
    _b: ndarray
        matrix columna de términos independientes
    _etiquetas: dict[str:list[str], str: bool]
        diccionario con etiquetas de la solución
        key: 'label' contiene una lista de etiquetas de la solución
        key: 'es_latex' un boleano que define si el string es en formato Latex o no
    _n: int
        número de filas de la matrix _A
    _m: int
        número de columnas de la matrix _A
    x: ndarray
        matrix columna de la solución del sistema de acuaciones lineales

    Methods
    -------
    _calcular():
        Soluciona el sistema de cuaciones lineales por el método de Tridiagonal y la solución queda guardada en el
        atributo x

    solucion():
        Presenta los resultados de la solución del sistema de ecuaciones

    Examples
    -------
    from mnspy import Tridiagonal
    import numpy as np

    n = 4
    e = np.zeros([n])
    f = np.zeros([n])
    g = np.zeros([n])
    for i in range(n):
        f[i] = 2.04
        if i < n - 1:
            g[i] = -1
        if i > 0:
            e[i] = -1
    r = np.array((40.8, 0.8, 0.8, 200.8))
    print('Matrix e:\n', e)
    print('Matrix f:\n', f)
    print('Matrix g:\n', g)
    print('Matrix r:\n', r)
    T = Tridiagonal(e, f, g, r)
    T.ajustar_etiquetas(['T_0', 'T_1', 'T_2', 'T_3'],
                        )
    T.mostrar_sistema()
    print('Temperaturas en grados Celsius:')
    for i in range(4):
        print(' {0:6.2f}'.format(T.x[i, 0]))
    T.solucion()
    """

    def __init__(self, e: np.ndarray, f: np.ndarray, g: np.ndarray, r: np.ndarray):
        """Constructor de la clase Tridiagonal

        Parameters
        ----------
        e: ndarray
            Vector subdiagonal de longitud n, primer elemento = 0
        f: ndarray
            Vector diagonal de longitud n.
        g: ndarray
            Vector superdiagonal de longitud n, último elemento = 0
        r: ndarray
            Vector terminos independienter de longitud n.
        """
        A = np.zeros((f.shape[0], f.shape[0]))
        # A = np.matrix(A)
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                if i == j:
                    A[i, j] = f[i]
                elif j == i - 1:
                    A[i, j] = e[i]
                elif j == i + 1:
                    A[i, j] = g[i]
        super().__init__(A, r.reshape(-1,1))
        self._aumentada = None
        self._e = e.astype(np.double)
        self._f = f.astype(np.double)
        self._g = g.astype(np.double)
        self._r = r.astype(np.double)
        self._calcular()

    def _calcular(self):
        """Soluciona el sistema de ecuaciones lineales por el método de la Tridiagonal y la solución queda guardada
        en el atributo x

        Returns
        -------
        None
        """
        x = np.zeros([self._n])
        f = self._f.copy()
        r = self._r.copy()
        for k in range(1, self._n):
            factor = self._e[k] / f[k - 1]
            f[k] -= factor * self._g[k - 1]
            r[k] -= factor * r[k - 1]
        x[self._n - 1] = r[self._n - 1] / f[self._n - 1]
        for k in range(self._n - 2, -1, -1):
            x[k] = (r[k] - self._g[k] * x[k + 1]) / f[k]
        self.x = x.reshape(-1,1)


def main():
    n = 4
    e = np.zeros([n])
    f = np.zeros([n])
    g = np.zeros([n])
    for i in range(n):
        f[i] = 2.04
        if i < n - 1:
            g[i] = -1
        if i > 0:
            e[i] = -1
    r = np.array((40.8, 0.8, 0.8, 200.8))
    print('Matrix e:\n', e)
    print('Matrix f:\n', f)
    print('Matrix g:\n', g)
    print('Matrix r:\n', r)
    T = Tridiagonal(e, f, g, r)
    T.ajustar_etiquetas(['T_0', 'T_1', 'T_2', 'T_3'],
                        )
    T.mostrar_sistema()
    print('Temperaturas en grados Celsius:')
    for i in range(4):
        print(' {0:6.2f}'.format(T.x[i, 0]))
    T.solucion()


if __name__ == '__main__':
    main()
