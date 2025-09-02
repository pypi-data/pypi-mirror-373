from mnspy.ecuaciones_algebraicas_lineales import EcuacionesAlgebraicasLineales
import numpy as np


class DescomposicionCholesky(EcuacionesAlgebraicasLineales):
    """Clase para la implementación de la descomposición de Cholesky.

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
        queda guardada en _U.
    retornar_u():
        Retorna la matrix diagonal superior, resultante de la descomposición Cholesky
    retornar_l():
        Retorna la matrix diagonal inferior, resultante de la descomposición Cholesky
    sustituir(b: np.matrix):
        Calcula los resultados de realizar el proceso de sustitución de la matrix b.
        Los resultados quedan guardados en x.
    solucion():
        Presenta los resultados de al realizar el proceso de sustitución. Los resultados quedan guardados en x

    Examples
    -------
    from mnspy import DescomposicionCholesky
    import numpy as np

    A = np.matrix('6 15 55; 15 55 225; 55 225 979')
    print('Matrix A:\n', A)
    ch = DescomposicionCholesky(A)
    print('Matrix superior u:\n', ch.retornar_u())
    print('Matrix inferior l:\n', ch.retornar_l())
    print('Multiplicación u*l:\n', ch.retornar_l() * ch.retornar_u())
    b = np.matrix('76; 295;1 259')
    ch.sustituir(b)
    print('Matrix b:\n', b)
    print('solución:')
    ch.solucion()
    """

    def __init__(self, A: np.ndarray):
        """Constructor de la clase base DescomposicionCholesky

        Parameters
        ----------
        A: ndarray
            Matrix de los coeficientes del sistema de ecuaciones
        """
        b = np.zeros((A.shape[0], 1))
        super().__init__(A, b)
        self._aumentada = None
        self._U = None
        self._factorizar()

    def _factorizar(self):
        """
        Descompone la matrix A en uno matrix triangular superior y una matrix triangular inferior, la cual
        queda guardada en _U

        Returns
        -------
        None
        """
        if self._n != self._m:
            print('La matriz A debe ser cuadrada')
            return
        self._U = np.zeros(self._A.shape)
        for i in range(self._n):
            suma = 0
            for k in range(i):
                suma += self._U[k, i] ** 2
            self._U[i, i] = np.sqrt(self._A[i, i] - suma)
            for j in range(i + 1, self._n):
                suma = 0
                for k in range(i):
                    suma += self._U[k, i] * self._U[k, j]
                self._U[i, j] = (self._A[i, j] - suma) / self._U[i, i]

    def retornar_u(self):
        """
        Retorna la matrix diagonal superior, resultante de la descomposición Cholesky

        Returns
        -------
        objeto ndarray con la matrix diagonal superior
        """
        return self._U

    def retornar_l(self):
        """
        Retorna la matrix diagonal inferior, resultante de la descomposición Cholesky

        Returns
        -------
        objeto ndarray con la matrix diagonal inferior
        """
        return np.transpose(self.retornar_u())

    def sustituir(self, b: np.ndarray):
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
        self._aumentada = np.hstack((self.retornar_l(), b))
        d = self.sustitucion_adelante()
        self._aumentada = np.hstack((self.retornar_u(), d))
        self.x = self.sustitucion_atras()


def main():
    A = np.array([[6, 15, 55], [15, 55, 225], [55, 225, 979]])
    print('Matrix A:\n', A)
    ch = DescomposicionCholesky(A)
    print('Matrix superior u:\n', ch.retornar_u())
    print('Matrix inferior l:\n', ch.retornar_l())
    print('Multiplicación u*l:\n', ch.retornar_l() @ ch.retornar_u())
    b = np.array([[76], [295], [1259]])
    ch.sustituir(b)
    print('Matrix b:\n', b)
    print('solución:')
    ch.solucion()


if __name__ == '__main__':
    main()
