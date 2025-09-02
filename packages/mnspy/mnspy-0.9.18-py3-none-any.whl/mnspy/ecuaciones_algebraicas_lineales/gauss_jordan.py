from mnspy.ecuaciones_algebraicas_lineales import EcuacionesAlgebraicasLineales
import numpy as np


class GaussJordan(EcuacionesAlgebraicasLineales):
    """Clase para la implementación de la solución de un sistema de ecuaciones por el método de Gauss_Jordan.

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
        Soluciona el sistema de cuaciones lineales por el método de Gauss-Jordan y la solución queda guardada en el
        atributo x

    solucion():
        Presenta los resultados de la solución del sistema de ecuaciones

    Examples
    -------
    from mnspy import GaussJordan
    import numpy as np

    A = np.matrix('3 -0.1 -0.2;0.1 7 -0.3; 0.3 -0.2 10')
    print('Matrix A:\n', A)
    b = np.matrix('7.85 ; -19.3; 71.4')
    print('Matrix b:\n', b)
    gj = GaussJordan(A, b)
    print('Matrix aumentada:')
    gj.mostrar_aumentada()
    print('solución:')
    gj.solucion()
    """
    def __init__(self, A: np.ndarray, b: np.ndarray):
        """Constructor de la clase Gauss-Jordan

        Parameters
        ----------
        A: ndarray
            Matrix de los coeficientes del sistema de ecuaciones
        b: ndarray
            Vector columna de los terminos independiantes
        """
        super().__init__(A, b)
        self._aumentada = np.hstack((self._A, self._b))
        self._calcular()

    def _calcular(self):
        """Soluciona el sistema de ecuaciones lineales por el método de Gauss-Jordan y la solución queda guardada en el
        atributo x

        Returns
        -------
        None
        """
        if self._n != self._m:
            print('La matriz A debe ser cuadrada')
            return
        self.eliminacion_gauss_jordan()
        self.x = self._aumentada[:, self._n]


def main():
    A = np.array([[3, -0.1, -0.2, ], [0.1, 7, -0.3], [0.3, -0.2, 10]])
    print('Matrix A:\n', A)
    b = np.array([[7.85], [-19.3], [71.4]])
    print('Matrix b:\n', b)
    gj = GaussJordan(A, b)
    print('Matrix aumentada:')
    gj.mostrar_aumentada()
    print('solución:')
    gj.solucion()


if __name__ == '__main__':
    main()
