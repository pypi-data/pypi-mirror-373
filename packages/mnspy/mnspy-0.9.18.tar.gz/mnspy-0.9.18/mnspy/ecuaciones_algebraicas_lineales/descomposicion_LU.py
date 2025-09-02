from mnspy.ecuaciones_algebraicas_lineales import EcuacionesAlgebraicasLineales
import numpy as np


class DescomposicionLU(EcuacionesAlgebraicasLineales):
    """Clase para la implementación de la descomposición LU.

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
    _factorizar():
        Descompone la matrix A en uno matrix triangular superior y una matrix triangular inferior, la cual
        queda guardada en _LU.
    retornar_u():
        Retorna la matrix diagonal superior, resultante de la descomposición LU
    retornar_l():
        Retorna la matrix diagonal inferior, resultante de la descomposición LU
    sustituir(b: np.matrix):
        Calcula los resultados de realizar el proceso de sustitución de la matrix b.
        Los resultados quedan guardados en x.
    solucion():
        Presenta los resultados de al realizar el proceso de sustitución. Los resultados quedan guardados en x

    Examples
    -------
    from mnspy import DescomposicionLU
    import numpy as np

    A = np.matrix('3 -0.1 -0.2;0.1 7 -0.3; 0.3 -0.2 10')
    print('Matrix A:\n', A)
    lu = DescomposicionLU(A)
    # lu.factorizar()
    print('Matrix aumentada:')
    lu.mostrar_aumentada()
    print('Matrix superior u:\n', lu.retornar_u())
    print('Matrix inferior l:\n', lu.retornar_l())
    print('Multiplicación u*l:\n', lu.retornar_l() * lu.retornar_u())
    b = np.matrix('7.85 ; -19.3; 71.4')
    lu.sustituir(b)
    print('Matrix b:\n', b)
    print('solución:')
    lu.solucion()
    """
    def __init__(self, A: np.ndarray):
        """Constructor de la clase base DescomposicionLU

        Parameters
        ----------
        A: ndarray
            Matrix de los coeficientes del sistema de ecuaciones
        """
        # b = np.matrix(np.zeros((A.shape[0], 1)))
        b = np.zeros((A.shape[0], 1))
        super().__init__(A, b)
        self._aumentada = None
        self._LU = None
        self.factorizar()

    def factorizar(self):
        """
        Descompone la matrix A en uno matrix triangular superior y una matrix triangular inferior, la cual
        queda guardada en _LU

        Returns
        -------
        None
        """
        if self._n != self._m:
            print('La matriz A debe ser cuadrada')
            return
        self._aumentada = self._A.copy()
        self.eliminacion_adelante(pivote_parcial=True, guardar_factores=True)
        self._LU = self._aumentada.copy()

    def retornar_u(self):
        """
        Retorna la matrix diagonal superior, resultante de la descomposición Lu

        Returns
        -------
        objeto ndarray con la matrix diagonal superior
        """
        # u = np.matrix(np.zeros(self._A.shape))
        u = np.zeros(self._A.shape)
        for i in range(self._n):
            u[i, i:] = self._LU[i, i:]
        return u

    def retornar_l(self):
        """
        Retorna la matrix diagonal inferior, resultante de la descomposición Lu

        Returns
        -------
        objeto ndarray con la matrix diagonal inferior
        """
        #l = np.matrix(np.identity(self._A.shape[0]))
        l = np.identity(self._A.shape[0])
        for i in range(1, self._n):
            l[i, 0:i] = self._LU[i, 0:i]
        return l

    def sustituir(self, b: np.matrix | np.ndarray):
        """Calcula los resultados de realizar el proceso de sustitución de la matrix b.
        Los resultados quedan guardados en x.

        Parameters
        ----------
        b: ndarray
            Vector columna a la cual se le realizará el proceso de sustitución

        Returns
        -------
        None
        """
        b = np.matmul(self._pivote , b)
        self._aumentada = np.hstack((self.retornar_l(), b))
        d = self.sustitucion_adelante()
        self._aumentada = np.hstack((self.retornar_u(), d))
        self.x = self.sustitucion_atras()


def main():
    A = np.array([[3, -0.1, -0.2], [0.1, 7, -0.3], [0.3, -0.2, 10]])
    print('Matrix A:\n', A)
    lu = DescomposicionLU(A)
    # lu.factorizar()
    print('Matrix aumentada:')
    lu.mostrar_aumentada()
    print('Matrix superior u:\n', lu.retornar_u())
    print('Matrix inferior l:\n', lu.retornar_l())
    print('Multiplicación u*l:\n', lu.retornar_l() * lu.retornar_u())
    b = np.array([[7.85], [-19.3], [71.4]])
    lu.sustituir(b)
    print('Matrix b:\n', b)
    print('solución:')
    lu.solucion()


if __name__ == '__main__':
    main()
