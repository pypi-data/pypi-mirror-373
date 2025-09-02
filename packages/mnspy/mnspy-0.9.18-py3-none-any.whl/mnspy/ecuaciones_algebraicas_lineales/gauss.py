from mnspy.ecuaciones_algebraicas_lineales import EcuacionesAlgebraicasLineales
import numpy as np


class Gauss(EcuacionesAlgebraicasLineales):
    """Clase para la implementación de la solución de un sistema de ecuaciones por el método de Gauss.

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
        Soluciona el sistema de cuaciones lineales por el método de Gauss y la solución queda guardada en el
        atributo x

    solucion():
        Presenta los resultados de la solución del sistema de ecuaciones

    Examples
    -------
    from mnspy import Gauss
    import numpy as np

    A = np.matrix('3 -0.1 -0.2;0.1 7 -0.3; 0.3 -0.2 10')
    print('Matrix A:\n', A)
    b = np.matrix('7.85 ; -19.3; 71.4')
    print('Matrix b:\n', b)
    g = Gauss(A, b, pivote_parcial=True)
    print('Matrix aumentada:')
    g.mostrar_aumentada(3)
    print('solución:')
    g.solucion()
    """
    def __init__(self, A: np.ndarray, b: np.ndarray, pivote_parcial: bool = False):
        """Constructor de la clase Gauss

        Parameters
        ----------
        A: ndarray
            Matrix de los coeficientes del sistema de ecuaciones
        b: ndarray
            Vector columna de los terminos independiantes
        pivote_parcial: bool
            booleano que indica si al método se le aplica el pivote parcial o no
        """
        super().__init__(A, b)
        self._aumentada = np.hstack((self._A, self._b))
        self._pivote_parcial = pivote_parcial
        if self._n >0:
            self._calcular()

    def _calcular(self):
        """Soluciona el sistema de ecuaciones lineales por el método de Gauss y la solución queda guardada en el
        atributo x

        Returns
        -------
        None
        """
        if self._n != self._m:
            print('La matriz A debe ser cuadrada')
            return
        self.eliminacion_adelante(self._pivote_parcial)
        self.x = self.sustitucion_atras()


def main():
    A = np.array([[3, -0.1, -0.2,], [0.1, 7, -0.3], [0.3, -0.2, 10]])
    print('Matrix A:\n', A)
    b = np.array([[7.85], [-19.3], [71.4]])
    print('Matrix b:\n', b)
    g = Gauss(A, b, pivote_parcial=True)
    print('Matrix aumentada:')
    g.mostrar_aumentada(3)
    print('solución:')
    g.solucion()


if __name__ == '__main__':
    main()
