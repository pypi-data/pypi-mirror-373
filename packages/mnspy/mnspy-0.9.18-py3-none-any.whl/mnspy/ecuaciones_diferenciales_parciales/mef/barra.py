from mnspy.ecuaciones_diferenciales_parciales.mef import Nodo, Elemento, Rigidez
from mnspy.utilidades import es_notebook, _generar_matrix
from IPython.display import display, Math
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

plt.rcParams.update(plt.rcParamsDefault)


class Barra(Elemento):
    """Representa un elemento de barra 1D que solo soporta cargas axiales.

    Este elemento es la unidad fundamental para analizar sistemas de barras
    conectadas a lo largo de un único eje (por ejemplo, el eje 'x'). Cada nodo
    tiene un solo grado de libertad de traslación en la dirección axial.

    Attributes
    ----------
    A : float
        Área de la sección transversal de la barra.
    E : float
        Módulo de Young del material de la barra.
    _k : Rigidez
        Objeto Rigidez que almacena la matriz de rigidez local del elemento.
    """

    def __init__(self, nombre: str, nodo_i: Nodo, nodo_j: Nodo, A: float, E: float, orientacion: str = 'x'):
        """Constructor para el elemento de barra.

        Parameters
        ----------
        nombre : str
            Nombre o identificador del elemento.
        nodo_i : Nodo
            Nodo inicial del elemento.
        nodo_j : Nodo
            Nodo final del elemento.
        A : float
            Área de la sección transversal de la barra.
        E : float
            Módulo de Young del material.
        orientacion : str, optional
            Eje a lo largo del cual se orienta el grado de libertad axial
            del elemento ('x', 'y' o 'z'). Por defecto es 'x'.
        """
        super().__init__(nombre, nodo_i, nodo_j)
        # Matriz de rigidez local para un elemento de barra 1D [k] = (AE/L) * [[1, -1], [-1, 1]]
        self._k = Rigidez(np.array([[1, -1], [-1, 1]], dtype=np.double) * A * E / self._L,
                          [self._nodo_i, self._nodo_j],
                          [orientacion])
        self._fuerzas_i = np.zeros((len(self._k.grados), 1))
        self._fuerzas_j = np.zeros((len(self._k.grados), 1))
        self._nodo_i.grados_libertad[orientacion].label_reaccion = 'F'
        self._nodo_i.grados_libertad[orientacion].label_fuerza = 'f'
        self._nodo_j.grados_libertad[orientacion].label_reaccion = 'F'
        self._nodo_j.grados_libertad[orientacion].label_fuerza = 'f'

    def _repr_latex_(self):
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(), dtype=object).reshape(-1, 1)
        vec_f = np.array(self._obtener_etiquetas_fuerzas(), dtype=object).reshape(-1, 1)
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
        return 'Barra: ' + self.nombre

    def __str__(self):
        """Representación del objeto como string.
        Returns
        -------
        str
            El nombre del elemento.
        """
        return 'Barra: ' + self.nombre

    def mostrar_sistema(self, reducida: bool = False):
        """Muestra el sistema de ecuaciones del elemento en formato matricial."""
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(reducida), dtype=object).reshape(-1, 1)
        vec_f = np.array(self._obtener_etiquetas_fuerzas(reducida), dtype=object).reshape(-1, 1)
        if es_notebook():
            texto_latex = r'\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_f,
                                           '{:}') + r'\end{array}\right\}=\left[\begin{array}{' + 'c' * \
                           self._k.obtener_matriz(reducida).shape[1] + '}'
            texto_latex += _generar_matrix(self._k.obtener_matriz(reducida),
                                           '{:G}') + r'\end{array}\right]\cdot\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}'
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
            print(fuerzas_internas)

    def _obtener_etiquetas_fuerzas(self, reducida: bool = False) -> list[str]:
        """Genera las etiquetas para las fuerzas nodales del elemento."""
        etq = ['f^{(' + self.nombre + ')}_{' + nodo.nombre + gl + '}' for nodo in [self._nodo_i, self._nodo_j] for gl in
               self._k.grados if not reducida or nodo.grados_libertad[gl].valor]
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
        return np.array(desplazamiento).reshape(-1, 1)

    def __obtener_path_elemento(self, espesor: float) -> Path:
        """Genera la ruta SVG para dibujar el elemento de barra."""
        t = espesor
        x_1, y_1, Z_1 = self._nodo_i.punto
        x_2, y_2, Z_2 = self._nodo_j.punto
        vertices = np.array([(x_1, y_1 - 0.5 * t), (x_2, y_2 - 0.5 * t), (x_2, y_2 + 0.5 * t), (x_1, y_1 + 0.5 * t),
                             (x_1, y_1 - 0.5 * t)])
        codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
        return Path(vertices, codes)

    def diagrama_fuerzas_internas(self):
        """Genera un diagrama de cuerpo libre del elemento.

        Muestra el elemento y las fuerzas internas (axiales) que actúan en
        cada uno de sus nodos. La dirección de las flechas indica si la fuerza
        es de tensión (jalando el nodo) o compresión (empujando el nodo).

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
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
        ax.scatter([self._nodo_i.punto[0], self._nodo_j.punto[0]], [self._nodo_i.punto[1], self._nodo_j.punto[1]],
                   c='navy', marker='o')
        ax.axis('equal')
        ax.axis('off')
        ax.set_xmargin(0.15)
        ax.set_ymargin(0.15)
        plt.show()


def main():
    """Función principal para demostración."""
    # from mnspy import Nodo, Barra

    # Creación de los Nodos
    n_1 = Nodo('1', 0, grados_libertad={'x': False})
    n_2 = Nodo('2', 0.6, grados_libertad={'x': True})
    n_3 = Nodo('3', 1.2, grados_libertad={'x': True})
    n_4 = Nodo('4', 1.8, grados_libertad={'x': False})
    # Creación de los Elementos
    e_1 = Barra('1', n_1, n_2, A=6E-4, E=2E11)
    e_2 = Barra('2', n_2, n_3, A=6E-4, E=2E11)
    e_3 = Barra('3', n_3, n_4, A=12E-4, E=1E11)
    # Cargas
    n_2.agregar_fuerza_externa(15000, 'x')
    # Matriz Global
    from mnspy import Ensamble
    mg = Ensamble([e_1, e_2, e_3])
    mg.diagrama_cargas()
    # Solución del sistema de ecuaciones
    mg.solucionar_por_gauss_y_calcular_reacciones()
    mg.solucion()
    e_1.diagrama_fuerzas_internas()


if __name__ == '__main__':
    main()
