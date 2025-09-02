from mnspy.ecuaciones_diferenciales_parciales.mef import Nodo, Elemento, Rigidez
from mnspy.utilidades import es_notebook, _generar_matrix
from IPython.display import display, Math
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
plt.rcParams.update(plt.rcParamsDefault)

class Resorte(Elemento):
    """Representa un elemento de resorte 1D que solo soporta cargas axiales.

    Este es el elemento más simple, definido por una constante de rigidez `k`.
    Puede ser orientado a lo largo de los ejes 'x' o 'y', y cada uno de sus
    nodos tiene un único grado de libertad en esa dirección.

    Attributes
    ----------
    _k : Rigidez
        Objeto `Rigidez` que almacena la matriz de rigidez local del elemento.
    _direccion : float
        Factor de dirección (+1.0 o -1.0) para la visualización.
    _orientacion : str
        Eje a lo largo del cual se orienta el grado de libertad ('x' o 'y').
    """

    def __init__(self, nombre: str, nodo_i: Nodo, nodo_j: Nodo, k: float, direccion: str = 'derecha'):
        """Constructor para el elemento de resorte.

        Parameters
        ----------
        nombre : str
            Nombre o identificador del elemento.
        nodo_i : Nodo
            Nodo inicial del elemento.
        nodo_j : Nodo
            Nodo final del elemento.
        k : float
            Constante de rigidez del resorte.
        direccion : str, optional
            Orientación del resorte. Puede ser 'derecha', 'izquierda' (para el eje 'x'),
            'arriba' o 'abajo' (para el eje 'y'). Por defecto es 'derecha'.
        """
        super().__init__(nombre, nodo_i, nodo_j)
        orientacion = 'x'
        self._direccion = 1.0
        if direccion == 'derecha':
            orientacion = 'x'
            self._direccion = 1.0
        elif direccion == 'izquierda':
            orientacion = 'x'
            self._direccion = -1.0
        elif direccion == 'arriba':
            orientacion = 'y'
            self._direccion = 1.0
        elif direccion == 'abajo':
            orientacion = 'y'
            self._direccion = -1.0
        self._k = Rigidez(np.array([[1, -1], [-1, 1]], dtype=np.double) * k, [self._nodo_i, self._nodo_j],
                          [orientacion])
        self._fuerzas_i = np.zeros((len(self._k.grados), 1))
        self._fuerzas_j = np.zeros((len(self._k.grados), 1))
        self._nodo_i.grados_libertad[orientacion].fuerza += 0.0
        self._nodo_i.grados_libertad[orientacion].label_reaccion = 'F'
        self._nodo_i.grados_libertad[orientacion].label_fuerza = 'f'
        self._nodo_j.grados_libertad[orientacion].fuerza += 0.0
        self._nodo_j.grados_libertad[orientacion].label_reaccion = 'F'
        self._nodo_j.grados_libertad[orientacion].label_fuerza = 'f'
        self._orientacion = orientacion

    def _repr_latex_(self):
        """Representación en LaTeX del sistema local del elemento para notebooks."""
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
        """Representación del objeto como string.

        Returns
        -------
        str
            El nombre del elemento.
        """
        # self.mostrar_sistema()
        return 'Resorte: ' + self.nombre

    def __str__(self):
        """Representación del objeto como string.
        Returns
        -------
        str
            El nombre del elemento.
        """
        return 'Resorte: ' + self.nombre

    def mostrar_sistema(self, reducida: bool = False):
        """Muestra el sistema de ecuaciones del elemento en formato matricial.

        Parameters
        ----------
        reducida : bool
            Si es True, muestra el sistema reducido.
        """
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
        """Calcula y muestra las fuerzas internas en los nodos del elemento.

        Returns
        -------
        str or None
            Una tabla HTML para notebooks de Jupyter, o imprime la tabla en la
            consola y no retorna nada.
        """
        fuerzas_internas = np.matmul(self._k.k, self._obtener_desplazamientos())
        if es_notebook():
            indice = ['$' + label + '$' for label in self._obtener_etiquetas_fuerzas()]
            return tabulate({'Fuerzas internas': fuerzas_internas}, headers='keys', showindex=indice, tablefmt='html')
        else:
            indice = self._obtener_etiquetas_fuerzas()
            print(tabulate({'Fuerzas internas': fuerzas_internas}, headers='keys', showindex=indice, tablefmt='simple'))

    def _obtener_etiquetas_fuerzas(self, reducida: bool = False) -> list[str]:
        """Genera las etiquetas para las fuerzas nodales del elemento.
        """
        if es_notebook():
            etq = ['f^{(' + self.nombre + ')}_{' + nodo.nombre + gl + '}' for nodo in [self._nodo_i, self._nodo_j] for
                   gl in self._k.grados if not reducida or nodo.grados_libertad[gl].valor]
        else:
            etq = ['f^(' + self.nombre + ')_' + nodo.nombre + gl + '' for nodo in [self._nodo_i, self._nodo_j] for
                   gl in self._k.grados if not reducida or nodo.grados_libertad[gl].valor]
        return etq

    def _obtener_desplazamientos(self) -> np.ndarray:
        """Recupera los desplazamientos de los nodos del elemento."""
        desplazamiento = None
        for item in self._k.lista_nodos:
            d_i = [d.desplazamiento for d in item.grados_libertad.values() if d.gl in self._k.grados]
            if desplazamiento is None:
                desplazamiento = d_i
            else:
                desplazamiento = np.hstack((desplazamiento, d_i))
        return np.array(desplazamiento).reshape(-1,1)

    def diagrama_fuerzas_internas(self):
        """Genera un diagrama de cuerpo libre del elemento.

        Muestra el resorte y las fuerzas internas que actúan en cada nodo.
        La dirección de las flechas indica si la fuerza es de tensión (jalando
        el nodo) o compresión (empujando el nodo).

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        def dib_resorte(p_1: tuple, p_2: tuple, t: float):
            l_res = ((p_2[0] - p_1[0]) ** 2 + (p_2[1] - p_1[1]) ** 2) ** 0.5
            x_1, y_1 = p_1
            x_2, y_2 = p_2
            c = (p_2[0] - p_1[0]) / l_res
            s = (p_2[1] - p_1[1]) / l_res
            vertices = np.array([(x_1 + 0.5 * t * s, y_1 - 0.5 * t * c), (x_2 + 0.5 * t * s, y_2 - 0.5 * t * c),
                                 (x_2 + 0.5 * t * s + 0.7 * t * c, y_2 - 0.5 * t * c + 0.7 * t * s),
                                 (x_2 - 0.5 * t * s + 0.7 * t * c, y_2 + 0.5 * t * c + 0.7 * t * s),
                                 (x_2 - 0.5 * t * s, y_2 + 0.5 * t * c), (x_1 - 0.5 * t * s, y_1 + 0.5 * t * c),
                                 (x_1 - 0.5 * t * s - 0.7 * t * c, y_1 + 0.5 * t * c - 0.7 * t * s),
                                 (x_1 + 0.5 * t * s - 0.7 * t * c, y_1 - 0.5 * t * c - 0.7 * t * s),
                                 (x_1 + 0.5 * t * s, y_1 - 0.5 * t * c)])
            codes = [Path.MOVETO, Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO, Path.CURVE4,
                     Path.CURVE4,
                     Path.CURVE4]
            return Path(vertices, codes)

        def resorte():
            x_1, y_1, z_1 = self.get_nodo_inicial().punto
            x_2, y_2, z_2 = self.get_nodo_final().punto
            lon = ((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2) ** 0.5
            c = (x_2 - x_1) / lon
            s = (y_2 - y_1) / lon

            n = 30
            h = 0.1 * lon
            t = 0.25 * h
            x = np.linspace(x_1, x_2, n)
            y = np.linspace(y_1, y_2, n)
            for i in range(n - 4):
                if i % 2 == 0:
                    x[i + 2] -= h * s
                    y[i + 2] += h * c
                else:
                    x[i + 2] += h * s
                    y[i + 2] -= h * c
            for i in range(n - 1):
                if i % 2 == 1:
                    patch = patches.PathPatch(dib_resorte((x[i], y[i]), (x[i + 1], y[i + 1]), t), facecolor='steelblue',
                                              lw=0.25, alpha=0.4)
                    ax.add_patch(patch)
            for i in range(n - 1):
                if i % 2 == 0:
                    patch = patches.PathPatch(dib_resorte((x[i], y[i]), (x[i + 1], y[i + 1]), t), edgecolor='royalblue',
                                              facecolor='lightsteelblue', lw=0.2, alpha=0.4)
                    ax.add_patch(patch)

        fuerzas_internas = np.matmul(self._k.k, self._obtener_desplazamientos())
        etq = self._obtener_etiquetas_fuerzas()
        fig, ax = plt.subplots()
        resorte()
        fuerza = fuerzas_internas[0, 0]
        if self._orientacion == 'x':
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
        else:
            if fuerza <= 0.0:
                pos = 50
                ali = 'bottom'
                sentido = '->'
            else:
                pos = 50
                ali = 'bottom'
                sentido = '<-'
            ax.annotate('$' + etq[0] + '=' + '{:G}$'.format(abs(fuerza)),
                        xy=(self._nodo_i.punto[0:2]), xycoords='data',
                        xytext=(0, pos), textcoords='offset points', va=ali, ha='center', size=12,
                        arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))
        fuerza = fuerzas_internas[1, 0]
        if self._orientacion == 'x':
            if fuerza <= 0.0:
                pos = 50
                ali = 'left'
                sentido = '->'
            else:
                pos = 50
                ali = 'left'
                sentido = '<-'
            ax.annotate('$' + etq[1] + '=' + '{:G}$'.format(abs(fuerza)),
                        xy=(self._nodo_j.punto[0:2]), xycoords='data',
                        xytext=(pos, 0), textcoords='offset points', va='center', ha=ali, size=12,
                        arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))
        else:
            if fuerza <= 0.0:
                pos = -50
                ali = 'top'
                sentido = '<-'
            else:
                pos = -50
                ali = 'top'
                sentido = '->'
            ax.annotate('$' + etq[1] + '=' + '{:G}$'.format(abs(fuerza)),
                        xy=(self._nodo_j.punto[0:2]), xycoords='data',
                        xytext=(0, pos), textcoords='offset points', va=ali, ha='center', size=12,
                        arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))

        ax.scatter([self._nodo_i.punto[0], self._nodo_j.punto[0]], [self._nodo_i.punto[1], self._nodo_j.punto[1]],
                   c='navy', marker='o')
        ax.axis('equal')
        ax.axis('off')
        ax.set_xmargin(0.15)
        ax.set_ymargin(0.15)
        plt.show()


def main():
    n_1 = Nodo('1', grados_libertad={'x': False})
    n_2 = Nodo('2', grados_libertad={'x': False})
    n_3 = Nodo('3', grados_libertad={'x': True})
    n_4 = Nodo('4', grados_libertad={'x': True})

    e_1 = Resorte('1', n_1, n_3, k=200)
    e_2 = Resorte('2', n_3, n_4, k=400)
    e_3 = Resorte('3', n_4, n_2, k=600)

    n_4.agregar_fuerza_externa(25000, 'x')

    from mnspy import Ensamble
    mg = Ensamble([e_1, e_2, e_3])
    mg.diagrama_cargas()

    mg.solucionar_por_gauss_y_calcular_reacciones()

    e_1.fuerzas_internas()
    e_2.fuerzas_internas()
    e_3.fuerzas_internas()
    e_1.diagrama_fuerzas_internas()


if __name__ == '__main__':
    main()
