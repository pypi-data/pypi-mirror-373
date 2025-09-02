from mnspy.ecuaciones_algebraicas_lineales import EcuacionesAlgebraicasLineales
import numpy as np
from tabulate import tabulate
from mnspy.utilidades import es_notebook


class GaussSediel(EcuacionesAlgebraicasLineales):
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
        Soluciona el sistema de cuaciones lineales por el método de GaussSediel y la solución queda guardada en el
        atributo x

    solucion():
        Presenta los resultados de la solución del sistema de ecuaciones

    Examples
    -------
    from mnspy import GaussSediel
    import numpy as np

    A = np.matrix('3 -0.1 -0.2;0.1 7 -0.3; 0.3 -0.2 10')
    print('Matrix A:\n', A)
    b = np.matrix('7.85 ; -19.3; 71.4')
    print('Matrix b:\n', b)
    gj = GaussSediel(A, b)
    print('solución:')
    gj.solucion()
    gj.generar_tabla()
    """

    def __init__(self, A: np.ndarray, b: np.ndarray, val_inicial: float = 0.0, tol_porc: float = 0.1,
                 factor_lambda: float = 1.0, iter_max: int = 20):
        """Constructor de la clase GaussSediel

        Parameters
        ----------
        A: ndarray
            Matrix de los coeficientes del sistema de ecuaciones
        b: ndarray
            Vector columna de los terminos independiantes
        val_inicial: float
            Valor inicial de las variables cuando empieza la iteración, por defecto es 0.0
        tol_porc:: float
            Valor con el máximo porcentaje de error permitido, por defecto es 0.1%
        factor_lambda: float
            Valor con el factor de relajamiento que multiplicará la fórmula de iteración, por defecto es 1.0
        iter_max: int
            Corresponde al número máximo de iteraciones permitidas
        """
        super().__init__(A, b)
        self._aumentada = None
        self._iter_max = iter_max
        self._factor_lambda = factor_lambda
        self._tol_porc = tol_porc
        self._converge = True
        self._iter = 0
        self._v_inicial = val_inicial
        self.x = np.full((self._n, 1), self._v_inicial, dtype=float)
        self._last_x = self.x.copy()
        self._iter_valores = self.x.copy()
        self._EA = []
        self._A_mod = self._A.copy()
        np.fill_diagonal(self._A_mod, 0)
        self._dia = np.diag(self._A).reshape(-1, 1)
        if self._n != self._m:
            print('La matriz A debe ser cuadrada')
            return
        if np.count_nonzero(self._dia) != self._n:
            print('La diagonal de A no puede tener ceros')
            return
        self._calcular()

    def _calcular(self):
        """Soluciona el sistema de ecuaciones lineales por el método de Gauss Sediel

        Returns
        -------
        None
        """
        for k in range(self._iter_max):
            for i in range(self._n):
                self.x[i, 0] = self._factor_lambda * (
                        (self._b[i, 0] - np.sum(np.matmul(self._A_mod[i], self.x))) / self._dia[i, 0]) + (
                                       1 - self._factor_lambda) * self.x[i, 0]
            error = max(abs((self.x - self._last_x) / self.x))[0]
            self._last_x = self.x.copy()
            self._converge = error <= self._tol_porc / 100.0
            self._iter_valores = np.hstack((self._iter_valores, self.x))
            self._EA.append(error * 100)
            if self._converge:
                break

    def generar_tabla(self):
        """Genera la tabla de iteraciones

        Returns
        -------
        Tabla de iteraciones usando el pquete tabulate
        """
        valores = np.hstack((self._iter_valores[:, 1:].transpose(), np.array(self._EA).reshape(-1,1)))
        if es_notebook():
            if self._etiquetas is None:
                indice = ['Iteración'] + ['$x_{' + str(i) + '}$' for i in range(self.x.shape[0])] + [
                    '$\\varepsilon_{a}[\\%]$']
            else:
                if self._etiquetas['es_latex']:
                    indice = ['Iteración'] + ['$' + label + '$' for label in self._etiquetas['label']] + [
                        '$\\varepsilon_{a}$']
                else:
                    indice = ['Iteración'] + self._etiquetas['label'] + ['EA[%]']
            return tabulate(np.array(valores), indice, showindex=list(range(1, valores.shape[0] + 1)),
                            tablefmt='html', colalign=("center",))
        else:
            if self._etiquetas is None:
                indice = ['Iteración'] + ['x_' + str(i) for i in range(self.x.shape[0])] + ['EA']
            else:
                indice = ['Iteración'] + self._etiquetas['label'] + ['EA']
            print(tabulate(np.array(valores), indice, showindex=list(range(1, valores.shape[0] + 1)), tablefmt='simple',
                           colalign=("center",)))
            return None


def main():
    A = np.array([[3, -0.1, -0.2], [0.1, 7, -0.3], [0.3, -0.2, 10]])
    print('Matrix A:\n', A)
    b = np.array([[7.85], [-19.3], [71.4]])
    print('Matrix b:\n', b)
    gj = GaussSediel(A, b)
    print('solución:')
    gj.solucion()
    gj.generar_tabla()


if __name__ == '__main__':
    main()
