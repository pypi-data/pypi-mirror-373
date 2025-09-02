from mnspy.ecuaciones_algebraicas_lineales import EcuacionesAlgebraicasLineales
import numpy as np


class Cramer(EcuacionesAlgebraicasLineales):
    """Clase para la implementación de la solución de un sistema de ecuaciones por el método de Cramer.

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
        Soluciona el sistema de cuaciones lineales por el método de Cramer y la solución queda guardada en el
        atributo x

    solucion():
        Presenta los resultados de la solución del sistema de ecuaciones

    Examples
    -------
    from mnspy import Cramer
    import numpy as np

    A = np.matrix('3 -0.1 -0.2;0.1 7 -0.3; 0.3 -0.2 10')
    b = np.matrix('7.85 ; -19.3; 71.4')
    cr = Cramer(A, b)
    cr.solucion()
    """
    def __init__(self, A: np.ndarray, b: np.ndarray):
        """Constructor de la clase Cramer

        Parameters
        ----------
        A: ndarray
            Matrix de los coeficientes del sistema de ecuaciones
        b: ndarray
            Vector columna de los terminos independientes
        """
        super().__init__(A, b)
        self._calcular()

    def _calcular(self):
        """Soluciona el sistema de ecuaciones lineales por el método de Cramer y la solución queda guardada en el
        atributo x

        Returns
        -------
        None
        """
        det = np.linalg.det(self._A)
        if det == 0:
            print('Matriz Singular')
            self.x = None
            return
        for i in range(self._A.shape[1]):
            mat_i = self._A.copy()
            mat_i[:, [i]] = self._b
            self.x[i, 0] = np.linalg.det(mat_i) / det


def main():
    A = np.array('3 -0.1 -0.2;0.1 7 -0.3; 0.3 -0.2 10')
    b = np.array('7.85 ; -19.3; 71.4')
    cr = Cramer(A, b)
    cr.solucion()


if __name__ == '__main__':
    main()
