import matplotlib.pyplot as plt
import numpy as np
plt.rcParams.update(plt.rcParamsDefault)

class EcuacionesDiferencialesParciales:
    """Clase base para los solucionadores de EDPs en mallas estructuradas.

    Esta clase gestiona la creación de la malla, la aplicación de condiciones
    de frontera y los métodos de visualización para problemas de EDPs en
    dominios rectangulares.

    Attributes
    ----------
    U : np.ndarray
        Matriz con los valores de la solución en cada nodo de la malla.
    X : np.ndarray
        Matriz con las coordenadas 'x' de cada nodo.
    Y : np.ndarray
        Matriz con las coordenadas 'y' de cada nodo.
    frontera : dict
        Diccionario que define las condiciones de frontera ('norte', 'sur',
        'este', 'oeste').
    q_x : np.ndarray
        Matriz con los flujos calculados en la dirección x.
    q_y : np.ndarray
        Matriz con los flujos calculados en la dirección y.

    Methods
    -------
    _calcular_campos():
        Calcula los campos secundarios (ej. flujos de calor) a partir de la solución.
    _graficar_datos():
        Genera una gráfica de contorno de la solución.
    graficar_valores():
        Muestra la malla con los valores de la solución en cada nodo.
    graficar_coordenadas():
        Muestra la malla con las coordenadas de cada nodo.
    _graficar_campos():
        Genera una gráfica de vectores (quiver plot) para los campos calculados.
    """
    def __init__(self, n: int | tuple[int, int], frontera: dict[str, float | str | list[float]], val_inicial: float,
                 k_x: float = 1, k_y: float = 1):
        """Constructor de la clase EcuacionesDiferencialesParciales

        Parameters
        ----------
        n: int | tuple[int, int]
            Número de nodos en cada dirección. Si es un entero, la malla será de
            n x n. Si es una tupla (n_filas, n_columnas), la malla será de
            n_filas x n_columnas.
        frontera: dict[str, float | str | list[float]]
            Condiciones de frontera de la placa con las siguientes llaves permitidas:
            'norte', 'sur', 'este', 'oeste'. Los valores pueden ser:
            - ``float``: Condición de Dirichlet (valor constante).
            - ``list[float]``: Condición de Dirichlet (valor variable a lo largo de la frontera).
            - ``str``: Condición de Neumann. Actualmente solo se soporta 'aislado' (flujo cero).
        val_inicial: float
            Valor inicial que tendrá cada uno de los puntos de la placa
        k_x: float, optional
            Coeficiente de conductividad térmica en la dirección x. Por defecto es 1.
        k_y: float, optional
            Coeficiente de conductividad térmica en la dirección y. Por defecto es 1.
        """
        if isinstance(n, tuple):
            self._n, self._m = n
        else:
            self._n = self._m = n
        self._X, self._Y = np.meshgrid(np.arange(0, self._m), np.arange(0, self._n))
        self._v_inicial = val_inicial
        self.U = np.full((self._n, self._m), self._v_inicial, dtype=float)
        self.q_x = np.zeros((self._n, self._m), dtype=float)
        self.q_y = np.zeros((self._n, self._m), dtype=float)
        self._k_x = k_x
        self._k_y = k_y
        self._frontera = frontera
        # Aplicar condiciones de frontera de Dirichlet
        if not self._frontera['norte'] == 'aislado':
            if isinstance(self._frontera['norte'], list):
                self.U[self._n - 1:, :] = np.matrix(self._frontera['norte'])
            else:
                self.U[self._n - 1:, :] = self._frontera['norte']
        if not self._frontera['sur'] == 'aislado':
            if isinstance(self._frontera['sur'], list):
                self.U[:1, :] = np.matrix(self._frontera['sur'])
            else:
                self.U[:1, :] = self._frontera['sur']
        if not self._frontera['oeste'] == 'aislado':
            if isinstance(self._frontera['oeste'], list):
                self.U[:, :1] = np.matrix(self._frontera['oeste']).transpose()
            else:
                self.U[:, :1] = self._frontera['oeste']
        if not self._frontera['este'] == 'aislado':
            if isinstance(self._frontera['este'], list):
                self.U[:, self._m - 1:] = np.matrix(self._frontera['este']).transpose()
            else:
                self.U[:, self._m - 1:] = self._frontera['este']
        plt.ioff()  # deshabilitada interactividad matplotlib

    def _calcular_campos(self):
        """Calcula los campos de flujo (q_x, q_y) a partir de la solución U.

        Utiliza diferencias finitas centradas para aproximar el gradiente.
        """
        for i in range(1, self._n - 1):
            for j in range(1, self._m - 1):
                self.q_x[i, j] = -self._k_x * (self.U[i, j + 1] - self.U[i, j - 1]) / 2
                self.q_y[i, j] = -self._k_y * (self.U[i + 1, j] - self.U[i - 1, j]) / 2

    def _graficar_datos(self):
        """Dibuja un mapa de contorno de la solución `U`.

        Returns
        -------
        Grafica los resultados interpolados, para ello se utiliza el paquete matplotlib
        """
        plt.contourf(self._X, self._Y, self.U, 25, cmap=plt.jet())
        plt.colorbar()
        plt.xlabel('Sur')
        plt.ylabel('Oeste')
        plt.show()

    def graficar_valores(self):
        """Dibuja la malla y muestra el valor de la solución `U` en cada nodo.

        Returns
        -------
        Grafica los valores resultantes en cada punto, para ello se utiliza el paquete matplotlib
        """
        plt.scatter(self._X, self._Y)
        plt.margins(0.1)
        for i in range(self._n):
            for j in range(self._m):
                plt.annotate('{:.2f}'.format(self.U[i, j]), (j, i), xytext=(0, 4), textcoords='offset points',
                         ha='center', va='bottom')
        plt.xlabel('Sur')
        plt.ylabel('Oeste')
        plt.show()

    def graficar_coordenadas(self):
        """Dibuja la malla y muestra las coordenadas `(i, j)` de cada nodo.

        Returns
        -------
        Grafica las coordenadas en cada punto, para ello se utiliza el paquete matplotlib
        """
        plt.scatter(self._X, self._Y)
        plt.margins(0.1)
        for i in range(self._n):
            for j in range(self._m):
                plt.annotate('(' + str(i) + ',' + str(j) + ')', (i, j), xytext=(0, 4), textcoords='offset points',
                         ha='center', va='bottom')
        plt.xlabel('Sur')
        plt.ylabel('Oeste')
        plt.show()

    def _graficar_campos(self):
        """Dibuja un campo de vectores para los flujos (q_x, q_y).

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib (quiver plot).
        """
        plt.quiver(self._X, self._Y, self.q_x, self.q_y, color='g', pivot='mid')
        plt.xlabel('Sur')
        plt.ylabel('Oeste')
        plt.show()
