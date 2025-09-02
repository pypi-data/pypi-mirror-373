from mnspy.ecuaciones_diferenciales_parciales.mef import Nodo, Elemento, Rigidez
from mnspy.utilidades import es_notebook, _generar_matrix
from IPython.display import display, Math
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.path import Path
import matplotlib.patches as patches

plt.rcParams.update(plt.rcParamsDefault)


class Armadura(Elemento):
    """Representa un elemento de armadura (truss) en 2D.

    Este elemento solo soporta cargas axiales (tensión y compresión) y se utiliza
    para modelar estructuras de armaduras planas. Cada nodo tiene dos grados de
    libertad (desplazamiento en 'x' y 'y').

    Attributes
    ----------
    A : float
        Área de la sección transversal del elemento.
    E : float
        Módulo de Young del material.
    _c : float
        Coseno del ángulo del elemento con respecto al eje x global.
    _s : float
        Seno del ángulo del elemento con respecto al eje x global.
    _kp : np.ndarray
        Matriz de rigidez local del elemento.
    _T : np.ndarray
        Matriz de transformación de coordenadas locales a globales.
    """
    def __init__(self, nombre: str, nodo_i: Nodo, nodo_j: Nodo, A: float, E: float):
        """Constructor para el elemento de armadura."""
        super().__init__(nombre, nodo_i, nodo_j)
        c = (self._nodo_j.punto[0] - self._nodo_i.punto[0]) / self._L
        s = (self._nodo_j.punto[1] - self._nodo_i.punto[1]) / self._L
        self._c = c
        self._s = s
        self._A = A
        self._E = E
        self._kp = np.array([[1, 0, -1, 0],
                             [0, 0, 0, 0],
                             [-1, 0, 1, 0],
                             [0, 0, 0, 0]],
                            dtype=np.double) * self._A * self._E / self._L
        self._T = np.array([[c, s, 0, 0],
                            [-s, c, 0, 0],
                            [0, 0, c, s],
                            [0, 0, -s, c]], dtype=np.double)
        self._k = Rigidez(np.matmul(np.matmul(self._T.transpose(), self._kp), self._T), [self._nodo_i, self._nodo_j],
                          ['x', 'y'])
        self._fuerzas_i = np.zeros((len(self._k.grados), 1))
        self._fuerzas_j = np.zeros((len(self._k.grados), 1))
        self._nodo_i.grados_libertad['x'].label_reaccion = 'F'
        self._nodo_i.grados_libertad['x'].label_fuerza = 'f'
        self._nodo_i.grados_libertad['y'].label_reaccion = 'F'
        self._nodo_i.grados_libertad['y'].label_fuerza = 'f'
        self._nodo_j.grados_libertad['x'].label_reaccion = 'F'
        self._nodo_j.grados_libertad['x'].label_fuerza = 'f'
        self._nodo_j.grados_libertad['y'].label_reaccion = 'F'
        self._nodo_j.grados_libertad['y'].label_fuerza = 'f'

    def _repr_latex_(self):
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(), dtype=object).reshape(-1,1)
        vec_f = np.array(self._obtener_etiquetas_fuerzas(), dtype=object).reshape(-1,1)
        texto_latex = r'\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_f,
                                       '{:}') + r'\end{array}\right\}_{\{f\}}=\left[\begin{array}{' + 'c' * \
                       self._k.obtener_matriz().shape[1] + '}'
        texto_latex += _generar_matrix(self._k.obtener_matriz(),
                                       '{:G}') + r'\end{array}\right]_{[k]}\cdot\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}_{\{d\}}'
        return '$' + texto_latex + '$'

    def __repr__(self):
        """Overload del método __repr__

        Returns
        -------
        Muestra el nombre del elemento
        """
        # self.mostrar_sistema()
        return 'Armadura: ' + self.nombre

    def __str__(self):
        """Overload del método __str__
        Returns
        -------
        Información del elemento
        """
        return 'Armadura: ' + self.nombre

    def _obtener_valor_fuerza(self):
        return np.matmul(np.array([[-self._c, -self._s, self._c, self._s]]), self._k.obtener_desplazamientos())[
            0, 0] * self._E * self._A / self._L

    def get_matriz_rigidez_local(self):
        return self._kp

    def get_matriz_T(self):
        return self._T

    def fuerza(self):
        if es_notebook():
            indice = [r'$f^{(' + self.nombre + r')}$']
            return tabulate({'Fuerza': [self._obtener_valor_fuerza()]}, headers='keys', showindex=indice,
                            tablefmt='html')
        else:
            return self._obtener_valor_fuerza()

    def esfuerzo(self):
        if es_notebook():
            indice = [r'$\sigma^{(' + self.nombre + r')}$']
            return tabulate({'Esfuerzo': [self._obtener_valor_fuerza() / self._A]}, headers='keys', showindex=indice,
                            tablefmt='html')
        else:
            return self._obtener_valor_fuerza() / self._A

    def mostrar_sistema(self, reducida: bool = False):
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(reducida), dtype=object).reshape(-1,1)
        vec_f = np.array(self._obtener_etiquetas_fuerzas(reducida), dtype=object).reshape(-1,1)
        if es_notebook():
            texto_latex = r'\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_f,
                                           '{:}') + r'\end{array}\right\}_{\{f\}}=\left[\begin{array}{' + 'c' * \
                           self._k.obtener_matriz(reducida).shape[1] + '}'
            texto_latex += _generar_matrix(self._k.obtener_matriz(reducida),
                                           '{:G}') + r'\end{array}\right]_{[k]}\cdot\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}_{\{d\}}'
            display(Math(texto_latex))
        else:
            return np.array2string(self._k.obtener_matriz(reducida),
                                   formatter={'float_kind': lambda x: '{:}'.format(x)})

    def fuerzas_internas(self):
        fuerzas_internas = np.matmul(self._k.k, self._obtener_desplazamientos())
        if es_notebook():
            indice = ['$' + label + '$' for label in self._obtener_etiquetas_fuerzas()]
            return tabulate({'Fuerzas internas': fuerzas_internas}, headers='keys', showindex=indice, tablefmt='html')
        else:
            print(fuerzas_internas)

    def fuerzas_internas_local(self):
        fuerzas_internas = np.matmul(self._T[[0, 2], :], np.matmul(self._k.k, self._obtener_desplazamientos()))
        if es_notebook():
            indice = ['$' + label + '$' for label in self._obtener_etiquetas_fuerzas_local()]
            return tabulate({'Fuerzas internas local': fuerzas_internas}, headers='keys', showindex=indice,
                            tablefmt='html')
        else:
            print(fuerzas_internas)

    def _obtener_etiquetas_fuerzas(self, reducida: bool = False):
        etq = [nodo.grados_libertad[gl].label_fuerza + '^{(' + self.nombre + ')}_{' + nodo.nombre + gl + '}' for nodo
               in [self._nodo_i, self._nodo_j] for gl in self._k.grados if
               not reducida or nodo.grados_libertad[gl].valor]
        return etq

    def _obtener_etiquetas_fuerzas_local(self, reducida: bool = False):
        etq = [nodo.grados_libertad['x'].label_fuerza + r'^{\prime(' + self.nombre + ')}_{' + nodo.nombre + 'x}' for
               nodo in [self._nodo_i, self._nodo_j] if not reducida or nodo.grados_libertad['x'].valor]
        return etq

    def _obtener_desplazamientos(self) -> np.ndarray:
        desplazamiento = None
        for item in self._k.lista_nodos:
            d_i = [d.desplazamiento for d in item.grados_libertad.values() if d.gl in self._k.grados]
            if desplazamiento is None:
                desplazamiento = d_i
            else:
                desplazamiento = np.hstack((desplazamiento, d_i))
        return np.array(desplazamiento).reshape(-1,1)

    def __obtener_path_elemento(self, espesor: np.double) -> Path:
        """Genera la ruta SVG para dibujar el elemento de armadura."""
        x_1, y_1, Z_1 = self._nodo_i.punto
        x_2, y_2, Z_2 = self._nodo_j.punto
        c = self._c
        s = self._s
        t = espesor

        vertices = np.array([(x_1 + 0.5 * t * s, y_1 - 0.5 * t * c), (x_2 + 0.5 * t * s, y_2 - 0.5 * t * c),
                             (x_2 + 0.5 * t * s + 0.7 * t * c, y_2 - 0.5 * t * c + 0.7 * t * s),
                             (x_2 - 0.5 * t * s + 0.7 * t * c, y_2 + 0.5 * t * c + 0.7 * t * s),
                             (x_2 - 0.5 * t * s, y_2 + 0.5 * t * c), (x_1 - 0.5 * t * s, y_1 + 0.5 * t * c),
                             (x_1 - 0.5 * t * s - 0.7 * t * c, y_1 + 0.5 * t * c - 0.7 * t * s),
                             (x_1 + 0.5 * t * s - 0.7 * t * c, y_1 - 0.5 * t * c - 0.7 * t * s),
                             (x_1 + 0.5 * t * s, y_1 - 0.5 * t * c)])
        codes = [Path.MOVETO, Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO, Path.CURVE4, Path.CURVE4,
                 Path.CURVE4]
        return Path(vertices, codes)

    def diagrama_fuerzas_internas(self):
        """Dibuja un diagrama de cuerpo libre del elemento con sus fuerzas internas globales."""
        fuerzas_internas = np.matmul(self._k.k, self._obtener_desplazamientos())
        etq = self._obtener_etiquetas_fuerzas()
        fig, ax = plt.subplots()
        ax.add_patch(patches.PathPatch(self.__obtener_path_elemento(self._L / 20), edgecolor='royalblue',
                                       facecolor='lightsteelblue', lw=0.2))
        fuerza = fuerzas_internas[0, 0]
        if fuerza <= 0.0:
            pos = -50
            ali = 'right'
            sentido = '<-'
        else:
            pos = -50
            ali = 'right'
            sentido = '->'
        ax.annotate('$' + etq[0] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_i.punto[0:2]), xycoords='data',
                    xytext=(pos, 0), textcoords='offset points', va='center', ha=ali, size=12,
                    arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))
        fuerza = fuerzas_internas[1, 0]
        if fuerza <= 0.0:
            pos = -50
            ali = 'top'
            sentido = '<-'
        else:
            pos = -50
            ali = 'top'
            sentido = '->'
        ax.annotate('$' + etq[1] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_i.punto[0:2]), xycoords='data',
                    xytext=(0, pos), textcoords='offset points', va=ali, ha='center', size=12,
                    arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))
        fuerza = fuerzas_internas[2, 0]
        if fuerza <= 0.0:
            pos = 50
            ali = 'left'
            sentido = '->'
        else:
            pos = 50
            ali = 'left'
            sentido = '<-'
        ax.annotate('$' + etq[2] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_j.punto[0:2]), xycoords='data',
                    xytext=(pos, 0), textcoords='offset points', va='center', ha=ali, size=12,
                    arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))
        fuerza = fuerzas_internas[3, 0]
        if fuerza <= 0.0:
            pos = 50
            ali = 'bottom'
            sentido = '->'
        else:
            pos = 50
            ali = 'bottom'
            sentido = '<-'
        ax.annotate('$' + etq[3] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_j.punto[0:2]), xycoords='data',
                    xytext=(0, pos), textcoords='offset points', va=ali, ha='center', size=12,
                    arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))
        plt.scatter([self._nodo_i.punto[0], self._nodo_j.punto[0]], [self._nodo_i.punto[1], self._nodo_j.punto[1]],
                    c='navy',
                    marker='o')

        ax.axis('equal')
        ax.axis('off')
        plt.show()

    def diagrama_fuerzas_internas_local(self):
        """Dibuja un diagrama de cuerpo libre con las fuerzas internas locales (axiales)."""
        fuerzas_internas = np.matmul(self._T[[0, 2], :], np.matmul(self._k.k, self._obtener_desplazamientos()))
        etq = self._obtener_etiquetas_fuerzas_local()
        fig, ax = plt.subplots()
        ax.add_patch(patches.PathPatch(self.__obtener_path_elemento(self._L / 20), edgecolor='royalblue',
                                       facecolor='lightsteelblue', lw=0.2))
        ang = np.degrees(np.arccos(self.get_coseno())) * np.sign(self.get_seno())
        fuerza = fuerzas_internas[0, 0]
        if fuerza <= 0.0:
            pos_x = -50 * self._c
            pos_y = -50 * self._s
            ali_v = 'center'
            ali_h = 'right'
            sentido = '<-'
        else:
            pos_x = -50 * self._c
            pos_y = -50 * self._s
            ali_v = 'center'
            ali_h = 'right'
            sentido = '->'
        ax.annotate('',
                    xy=(self._nodo_i.punto[0:2]), xycoords='data',
                    xytext=(pos_x, pos_y), textcoords='offset points', va=ali_v, ha=ali_h, size=12,
                    arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))
        ax.annotate('$' + etq[0] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_i.punto[0:2]), xycoords='data',
                    xytext=(pos_x, pos_y), textcoords='offset points', va=ali_v, ha=ali_h, size=12, rotation=ang,
                    rotation_mode='anchor')
        fuerza = fuerzas_internas[1, 0]
        if fuerza <= 0.0:
            pos_x = 50 * self._c
            pos_y = 50 * self._s
            ali_v = 'center'
            ali_h = 'left'
            sentido = '->'
        else:
            pos_x = 50 * self._c
            pos_y = 50 * self._s
            ali_v = 'center'
            ali_h = 'left'
            sentido = '<-'
        ax.annotate('',
                    xy=(self._nodo_j.punto[0:2]), xycoords='data',
                    xytext=(pos_x, pos_y), textcoords='offset points', va=ali_v, ha=ali_h, size=12,
                    arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))
        ax.annotate('$' + etq[1] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_j.punto[0:2]), xycoords='data',
                    xytext=(pos_x, pos_y), textcoords='offset points', va=ali_v, ha=ali_h, size=12, rotation=ang,
                    rotation_mode='anchor')
        plt.scatter([self._nodo_i.punto[0], self._nodo_j.punto[0]], [self._nodo_i.punto[1], self._nodo_j.punto[1]],
                    c='navy',
                    marker='o')

        ax.axis('equal')
        ax.axis('off')
        plt.show()
