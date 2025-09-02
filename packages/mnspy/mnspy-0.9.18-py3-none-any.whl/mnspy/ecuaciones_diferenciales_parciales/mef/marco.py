from mnspy.ecuaciones_diferenciales_parciales.mef import Nodo, Elemento, Rigidez
from mnspy.utilidades import es_notebook, _generar_matrix
from mnspy.ecuaciones_algebraicas_lineales import Gauss
from IPython.display import display, Math
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import sympy as sp

TOL_CERO = 1E-10
sp.init_printing(use_latex=True)

# plt.rcParams.update({
#     "text.usetex": True,
#     "font.family": "sans-serif",
#     "font.sans-serif": "Helvetica",
# })
plt.rcParams.update(plt.rcParamsDefault)


class Marco(Elemento):
    """Representa un elemento de marco plano (frame) en 2D.

    Este elemento combina el comportamiento de una viga y una armadura, ya que
    puede soportar cargas axiales, cortantes y momentos flectores. Se utiliza
    para modelar estructuras como pórticos y marcos rígidos.

    Cada nodo del elemento tiene tres grados de libertad:
    1. Desplazamiento en la dirección 'x' global.
    2. Desplazamiento en la dirección 'y' global.
    3. Rotación alrededor del eje 'z' global.

    El elemento puede tener una rótula (articulación) en el nodo final (`nodo_j`),
    lo que significa que no transmite momento en ese punto.

    Attributes
    ----------
    A : float
        Área de la sección transversal del elemento.
    E : float
        Módulo de Young del material.
    I : float
        Momento de inercia de la sección transversal.
    _c : float
        Coseno del ángulo del elemento con respecto al eje x global.
    _s : float
        Seno del ángulo del elemento con respecto al eje x global.
    _kp : np.ndarray
        Matriz de rigidez local del elemento (6x6).
    _T : np.ndarray
        Matriz de transformación de coordenadas (6x6).
    _k : Rigidez
        Objeto `Rigidez` que contiene la matriz de rigidez global del elemento.
    _cargas : dict
        Diccionario que almacena las cargas aplicadas sobre el elemento.
    """

    def __init__(self, nombre: str, nodo_i: Nodo, nodo_j: Nodo, A: float, E: float, I: float):
        """Constructor para el elemento de marco plano.

        Parameters
        ----------
        nombre : str
            Nombre o identificador del elemento.
        nodo_i : Nodo
            Nodo inicial del elemento.
        nodo_j : Nodo
            Nodo final del elemento. Puede ser una rótula si `nodo_j.es_rotula` es True.
        A : float
            Área de la sección transversal.
        E : float
            Módulo de Young del material.
        I : float
            Momento de inercia de la sección transversal.
        """
        super().__init__(nombre, nodo_i, nodo_j)
        c = (self._nodo_j.punto[0] - self._nodo_i.punto[0]) / self._L
        s = (self._nodo_j.punto[1] - self._nodo_i.punto[1]) / self._L
        self._c = c
        self._s = s
        self._A = A
        self._E = E

        # --- Cálculo de la matriz de rigidez local [kp] ---
        # Constantes para las fórmulas de rigidez de viga y barra
        c_1 = A * E / self._L  # Rigidez axial (AE/L)
        c_2 = E * I / self._L ** 3  # Constante de rigidez a flexión (EI/L^3)

        # Se selecciona la matriz de rigidez local apropiada
        # si el nodo final es una rótula (articulación).
        if nodo_j.es_rotula:
            # Matriz de rigidez local para un marco con rótula en el extremo j (articulado-empotrado)
            self._kp = np.array([[c_1, 0, 0, -c_1, 0, 0],
                                 [0, 3 * c_2, 3 * c_2 * self._L, 0, -3 * c_2, 0],
                                 [0, 3 * c_2 * self._L, 3 * c_2 * self._L ** 2, 0, -3 * c_2 * self._L, 0],
                                 [-c_1, 0, 0, c_1, 0, 0],
                                 [0, -3 * c_2, -3 * c_2 * self._L, 0, 3 * c_2, 0],
                                 [0, 0, 0, 0, 0, 0]],
                                dtype=np.double)
        else:
            # Matriz de rigidez local para un marco estándar (empotrado-empotrado)
            self._kp = np.array([[c_1, 0, 0, -c_1, 0, 0],
                                 [0, 12 * c_2, 6 * c_2 * self._L, 0, -12 * c_2, 6 * c_2 * self._L],
                                 [0, 6 * c_2 * self._L, 4 * c_2 * self._L ** 2, 0, -6 * c_2 * self._L,
                                  2 * c_2 * self._L ** 2],
                                 [-c_1, 0, 0, c_1, 0, 0],
                                 [0, -12 * c_2, -6 * c_2 * self._L, 0, 12 * c_2, -6 * c_2 * self._L],
                                 [0, 6 * c_2 * self._L, 2 * c_2 * self._L ** 2, 0, -6 * c_2 * self._L,
                                  4 * c_2 * self._L ** 2]],
                                dtype=np.double)

        # --- Matriz de transformación de coordenadas [T] ---
        self._T = np.array([[c, s, 0, 0, 0, 0],
                            [-s, c, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0],
                            [0, 0, 0, c, s, 0],
                            [0, 0, 0, -s, c, 0],
                            [0, 0, 0, 0, 0, 1]], dtype=np.double)

        # --- Matriz de rigidez en coordenadas globales [k] = [T]^T * [kp] * [T] ---
        self._k = Rigidez(np.matmul(np.matmul(self._T.transpose(), self._kp), self._T), [self._nodo_i, self._nodo_j],
                          ['x', 'y', 'eje_z'])

        # Inicialización de vectores de fuerzas nodales equivalentes
        self._fuerzas_i = np.zeros((len(self._k.grados), 1))
        self._fuerzas_j = np.zeros((len(self._k.grados), 1))
        # Fuerzas de corrección por rótula
        self._fuerzas_i_rot = np.zeros((len(self._k.grados), 1))
        self._fuerzas_j_rot = np.zeros((len(self._k.grados), 1))

        # Asignación de etiquetas para fuerzas y reacciones
        self._nodo_i.grados_libertad['x'].label_reaccion = 'F'
        self._nodo_i.grados_libertad['x'].label_fuerza = 'f'
        self._nodo_i.grados_libertad['y'].label_reaccion = 'F'
        self._nodo_i.grados_libertad['y'].label_fuerza = 'f'
        self._nodo_i.grados_libertad['eje_z'].label_reaccion = 'M'
        self._nodo_i.grados_libertad['eje_z'].label_fuerza = 'm'
        self._nodo_j.grados_libertad['x'].label_reaccion = 'F'
        self._nodo_j.grados_libertad['x'].label_fuerza = 'f'
        self._nodo_j.grados_libertad['y'].label_reaccion = 'F'
        self._nodo_j.grados_libertad['y'].label_fuerza = 'f'
        self._nodo_j.grados_libertad['eje_z'].label_reaccion = 'M'
        self._nodo_j.grados_libertad['eje_z'].label_fuerza = 'm'

        # Diccionario para almacenar cargas en el elemento
        self._cargas = {'distribuida': [], 'puntual': [], 'axial': [],
                        'momento': []}
        # Diccionario para coeficientes de ecuaciones de diagramas
        self._coef = {'A': 0.0, 'B': 0.0, 'c_1': 0.0, 'c_2': 0.0, 'c_3': 0.0, 'c_4': 0.0}
        self._A = A
        self._E = E
        self._I = I

    def _repr_latex_(self):
        """Representación en LaTeX del sistema local del elemento para notebooks."""
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(), dtype=object).reshape(-1, 1)
        vec_f = np.array(self._obtener_etiquetas_fuerzas(), dtype=object).reshape(-1, 1)
        texto_latex = r'\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_f,
                                       '{:}') + r'\end{array}\right\}_{\{f\}}=\left[\begin{array}{' + 'c' * \
                       self._k.obtener_matriz().shape[1] + '}'
        texto_latex += _generar_matrix(self._k.obtener_matriz(),
                                       '{:G}') + r'\end{array}\right]_{[k]}\cdot\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}_{\{d\}}-\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(self._obtener_fuerzas(),
                                       '{:}') + r'\end{array}\right\}_{\{f_{o}\}}'
        if self._nodo_j.es_rotula:
            texto_latex += r'-\left\{\begin{array}{c}' + _generar_matrix(self._obtener_fuerzas_por_rotula(),
                                                                         '{:}') + r'\end{array}\right\}_{\{f_{rot}\}}'
        return '$' + texto_latex + '$'

    def __repr__(self):
        """Representación del objeto como string."""
        return 'Marco: ' + self.nombre

    def __str__(self):
        """Representación del objeto como string."""
        return 'Marco: ' + self.nombre

    def agregar_carga_distribuida(self, q: float):
        """Agrega una carga uniformemente distribuida perpendicular al elemento.

        Calcula las fuerzas y momentos de empotramiento perfecto (fixed-end actions)
        correspondientes y los suma a los vectores de fuerza nodal del elemento.
        Si el nodo final es una rótula, se aplica una corrección para liberar
        el momento.

        Parameters
        ----------
        q : float
            Magnitud de la carga distribuida. Un valor positivo indica que la carga
            actúa en la dirección positiva del eje 'y' local del elemento.
        """
        # Fuerzas y momentos de empotramiento perfecto para carga distribuida
        self._nodo_i.grados_libertad['x'].fuerza += -q * self._L * self._s / 2
        self._fuerzas_i[0, 0] += -q * self._L * self._s / 2
        self._nodo_i.grados_libertad['y'].fuerza += q * self._L * self._c / 2
        self._fuerzas_i[1, 0] += q * self._L * self._c / 2
        self._nodo_i.grados_libertad['eje_z'].fuerza += q * self._L ** 2 / 12
        self._fuerzas_i[2, 0] += q * self._L ** 2 / 12
        self._nodo_j.grados_libertad['x'].fuerza += -q * self._L * self._s / 2
        self._fuerzas_j[0, 0] += -q * self._L * self._s / 2
        self._nodo_j.grados_libertad['y'].fuerza += q * self._L * self._c / 2
        self._fuerzas_j[1, 0] += q * self._L * self._c / 2
        self._nodo_j.grados_libertad['eje_z'].fuerza += -q * self._L ** 2 / 12
        self._fuerzas_j[2, 0] += -q * self._L ** 2 / 12

        self._cargas['distribuida'].append([q, q])

        # Si el nodo j es una rótula, se debe liberar el momento en ese extremo.
        # Esto se hace aplicando un momento corrector en el nodo i y las fuerzas
        # cortantes correspondientes en ambos nodos para mantener el equilibrio.
        if self._nodo_j.es_rotula:
            self._nodo_i.grados_libertad['x'].fuerza -= -self._s * (-q * self._L ** 2 / 12) * 3.0 / (2.0 * self._L)
            self._fuerzas_i_rot[0, 0] -= -self._s * (-q * self._L ** 2 / 12) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['y'].fuerza -= self._c * (-q * self._L ** 2 / 12) * 3.0 / (2.0 * self._L)
            self._fuerzas_i_rot[1, 0] -= self._c * (-q * self._L ** 2 / 12) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['eje_z'].fuerza -= 0.5 * (-q * self._L ** 2 / 12)
            self._fuerzas_i_rot[2, 0] -= 0.5 * (-q * self._L ** 2 / 12)
            self._nodo_j.grados_libertad['x'].fuerza -= -self._s * -(-q * self._L ** 2 / 12) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[0, 0] -= -self._s * -(-q * self._L ** 2 / 12) * 3.0 / (2.0 * self._L)
            self._nodo_j.grados_libertad['y'].fuerza -= self._c * -(-q * self._L ** 2 / 12) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[1, 0] -= self._c * -(-q * self._L ** 2 / 12) * 3.0 / (2.0 * self._L)
            self._nodo_j.grados_libertad['eje_z'].fuerza -= -q * self._L ** 2 / 12
            self._fuerzas_j_rot[2, 0] -= -q * self._L ** 2 / 12

    def agregar_carga_trapezoidal(self, q_1: float, q_2: float):
        """Agrega una carga trapezoidalmente distribuida perpendicular al elemento.

        Calcula las fuerzas y momentos de empotramiento perfecto (fixed-end actions)
        correspondientes y los suma a los vectores de fuerza nodal del elemento.
        Si el nodo final es una rótula, se aplica una corrección.

        Parameters
        ----------
        q_1 : float
            Magnitud de la carga en el nodo inicial (i).
        q_2 : float
            Magnitud de la carga en el nodo final (j).
        """
        self._nodo_i.grados_libertad['x'].fuerza += -q_1 * self._L * self._s / 2 - 3 * (
                q_2 - q_1) * self._L * self._s / 20
        self._fuerzas_i[0, 0] += -q_1 * self._L * self._s / 2 - 3 * (q_2 - q_1) * self._L * self._s / 20
        self._nodo_i.grados_libertad['y'].fuerza += q_1 * self._L * self._c / 2 + 3 * (
                q_2 - q_1) * self._L * self._c / 20
        self._fuerzas_i[1, 0] += q_1 * self._L * self._c / 2 + 3 * (q_2 - q_1) * self._L * self._c / 20
        self._nodo_i.grados_libertad['eje_z'].fuerza += q_1 * self._L ** 2 / 12 + (q_2 - q_1) * self._L ** 2 / 30
        self._fuerzas_i[2, 0] += q_1 * self._L ** 2 / 12 + (q_2 - q_1) * self._L ** 2 / 30
        self._nodo_j.grados_libertad['x'].fuerza += -q_1 * self._L * self._s / 2 - 7 * (
                q_2 - q_1) * self._L * self._s / 20
        self._fuerzas_j[0, 0] += -q_1 * self._L * self._s / 2 - 7 * (q_2 - q_1) * self._L * self._s / 20
        self._nodo_j.grados_libertad['y'].fuerza += q_1 * self._L * self._c / 2 + 7 * (
                q_2 - q_1) * self._L * self._c / 20
        self._fuerzas_j[1, 0] += q_1 * self._L * self._c / 2 + 7 * (q_2 - q_1) * self._L * self._c / 20
        self._nodo_j.grados_libertad['eje_z'].fuerza += -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20
        self._fuerzas_j[2, 0] += -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20

        self._cargas['distribuida'].append([q_1, q_2])

        # Corrección por rótula en el nodo j
        if self._nodo_j.es_rotula:
            self._nodo_i.grados_libertad['x'].fuerza -= -self._s * (-q_1 * self._L ** 2 / 12 - (
                    q_2 - q_1) * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._fuerzas_i_rot[0, 0] -= -self._s * (
                    -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20) * 3.0 / (
                                                 2.0 * self._L)
            self._nodo_i.grados_libertad['y'].fuerza -= self._c * (-q_1 * self._L ** 2 / 12 - (
                    q_2 - q_1) * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._fuerzas_i_rot[1, 0] -= self._c * (
                    -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20) * 3.0 / (
                                                 2.0 * self._L)
            self._nodo_i.grados_libertad['eje_z'].fuerza -= 0.5 * (
                    -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20)
            self._fuerzas_i_rot[2, 0] -= 0.5 * (-q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20)
            self._nodo_j.grados_libertad['x'].fuerza -= -self._s * -(
                    -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[0, 0] -= -self._s * -(
                    -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20) * 3.0 / (
                                                 2.0 * self._L)
            self._nodo_j.grados_libertad['y'].fuerza -= self._c * -(
                    -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[1, 0] -= self._c * -(
                    -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20) * 3.0 / (
                                                 2.0 * self._L)
            self._nodo_j.grados_libertad['eje_z'].fuerza -= -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20
            self._fuerzas_j_rot[2, 0] -= -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20

    def agregar_carga_puntual(self, p: float, a: float = None):
        """Agrega una carga puntual perpendicular al elemento a una distancia 'a'.

        Calcula las fuerzas y momentos de empotramiento perfecto (fixed-end actions)
        y los suma a los vectores de fuerza nodal. Si el nodo final es una rótula,
        se aplica una corrección.

        Parameters
        ----------
        p : float
            Magnitud de la carga puntual. Un valor positivo indica que la carga
            actúa en la dirección positiva del eje 'y' local del elemento.
        a : float, optional
            Distancia desde el nodo inicial (i) a la que se aplica la carga.
            Si es None, la carga se aplica en el centro del elemento (L/2).
            Por defecto es None.
        """
        if a is None:
            a = self._L / 2

        # Fuerzas y momentos de empotramiento perfecto para carga puntual
        self._nodo_i.grados_libertad['x'].fuerza += -p * (self._L - a) ** 2 * (self._L + 2 * a) * self._s / self._L ** 3
        self._fuerzas_i[0, 0] += -p * (self._L - a) ** 2 * (self._L + 2 * a) * self._s / self._L ** 3
        self._nodo_i.grados_libertad['y'].fuerza += p * (self._L - a) ** 2 * (self._L + 2 * a) * self._c / self._L ** 3
        self._fuerzas_i[1, 0] += p * (self._L - a) ** 2 * (self._L + 2 * a) * self._c / self._L ** 3
        self._nodo_i.grados_libertad['eje_z'].fuerza += p * a * (self._L - a) ** 2 / self._L ** 2
        self._fuerzas_i[2, 0] += p * a * (self._L - a) ** 2 / self._L ** 2
        self._nodo_j.grados_libertad['x'].fuerza += -p * a ** 2 * (self._L + 2 * (self._L - a)) * self._s / self._L ** 3
        self._fuerzas_j[0, 0] += -p * a ** 2 * (self._L + 2 * (self._L - a)) * self._s / self._L ** 3
        self._nodo_j.grados_libertad['y'].fuerza += p * a ** 2 * (self._L + 2 * (self._L - a)) * self._c / self._L ** 3
        self._fuerzas_j[1, 0] += p * a ** 2 * (self._L + 2 * (self._L - a)) * self._c / self._L ** 3
        self._nodo_j.grados_libertad['eje_z'].fuerza += -p * (self._L - a) * a ** 2 / self._L ** 2
        self._fuerzas_j[2, 0] += -p * (self._L - a) * a ** 2 / self._L ** 2

        self._cargas['puntual'].append([p, a])
        self._cargas['puntual'].sort(key=lambda l: l[1])

        # Corrección por rótula en el nodo j
        if self._nodo_j.es_rotula:
            self._nodo_i.grados_libertad['x'].fuerza -= -self._s * (
                    -p * (self._L - a) * a ** 2 / self._L ** 2) * 3.0 / (
                                                                2.0 * self._L)
            self._fuerzas_i_rot[0, 0] -= -self._s * (-p * (self._L - a) * a ** 2 / self._L ** 2) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['y'].fuerza -= self._c * (-p * (self._L - a) * a ** 2 / self._L ** 2) * 3.0 / (
                    2.0 * self._L)
            self._fuerzas_i_rot[1, 0] -= self._c * (-p * (self._L - a) * a ** 2 / self._L ** 2) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['eje_z'].fuerza -= 0.5 * (-p * (self._L - a) * a ** 2 / self._L ** 2)
            self._fuerzas_i_rot[2, 0] -= 0.5 * (-p * (self._L - a) * a ** 2 / self._L ** 2)
            self._nodo_j.grados_libertad['x'].fuerza -= -self._s * -(
                    -p * (self._L - a) * a ** 2 / self._L ** 2) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[0, 0] -= -self._s * -(-p * (self._L - a) * a ** 2 / self._L ** 2) * 3.0 / (
                    2.0 * self._L)
            self._nodo_j.grados_libertad['y'].fuerza -= self._c * -(
                    -p * (self._L - a) * a ** 2 / self._L ** 2) * 3.0 / (
                                                                2.0 * self._L)
            self._fuerzas_j_rot[1, 0] -= self._c * -(-p * (self._L - a) * a ** 2 / self._L ** 2) * 3.0 / (2.0 * self._L)
            self._nodo_j.grados_libertad['eje_z'].fuerza -= -p * (self._L - a) * a ** 2 / self._L ** 2
            self._fuerzas_j_rot[2, 0] -= -p * (self._L - a) * a ** 2 / self._L ** 2

    def agregar_momento(self, m: float, a: float = None):
        m *= -1.0
        if a is None:
            a = self._L / 2
        self._nodo_i.grados_libertad['x'].fuerza += -6 * m * a * (self._L - a) * self._s / self._L ** 3
        self._fuerzas_i[0, 0] += -6 * m * a * (self._L - a) * self._s / self._L ** 3
        self._nodo_i.grados_libertad['y'].fuerza += 6 * m * a * (self._L - a) * self._c / self._L ** 3
        self._fuerzas_i[1, 0] += 6 * m * a * (self._L - a) * self._c / self._L ** 3
        self._nodo_i.grados_libertad['eje_z'].fuerza += m * (self._L - a) * (3 * a - self._L) / self._L ** 2
        self._fuerzas_i[2, 0] += m * (self._L - a) * (3 * a - self._L) / self._L ** 2
        self._nodo_j.grados_libertad['x'].fuerza += 6 * m * a * (self._L - a) * self._s / self._L ** 3
        self._fuerzas_j[0, 0] +=  6 * m * a * (self._L - a) * self._s / self._L ** 3
        self._nodo_j.grados_libertad['y'].fuerza += - 6 * m * a * (self._L - a) * self._c / self._L ** 3
        self._fuerzas_j[1, 0] += - 6 * m * a * (self._L - a) * self._c / self._L ** 3
        self._nodo_j.grados_libertad['eje_z'].fuerza += m * a * (2 * self._L - 3 * a) / self._L ** 2
        self._fuerzas_j[2, 0] += m * a * (2 * self._L - 3 * a) / self._L ** 2

        self._cargas['momento'].append([-m, a])
        self._cargas['momento'].sort(key=lambda l: l[1])

        if self._nodo_j.es_rotula:
            self._nodo_i.grados_libertad['x'].fuerza -= -self._s * (m * a * (2 * self._L - 3 * a) / self._L ** 2) * 3.0 / (
                                                                2.0 * self._L)
            self._fuerzas_i_rot[0, 0] -= -self._s * (m * a * (2 * self._L - 3 * a) / self._L ** 2) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['y'].fuerza -= self._c * (m * a * (2 * self._L - 3 * a) / self._L ** 2) * 3.0 / (
                    2.0 * self._L)
            self._fuerzas_i_rot[1, 0] -= self._c * (m * a * (2 * self._L - 3 * a) / self._L ** 2) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['eje_z'].fuerza -= 0.5 * (m * a * (2 * self._L - 3 * a) / self._L ** 2)
            self._fuerzas_i_rot[2, 0] -= 0.5 * (m * a * (2 * self._L - 3 * a) / self._L ** 2)
            self._nodo_j.grados_libertad['x'].fuerza -= -self._s * -(m * a * (2 * self._L - 3 * a) / self._L ** 2) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[0, 0] -= -self._s * -(m * a * (2 * self._L - 3 * a) / self._L ** 2) * 3.0 / (
                    2.0 * self._L)
            self._nodo_j.grados_libertad['y'].fuerza -= self._c * -(m * a * (2 * self._L - 3 * a) / self._L ** 2) * 3.0 / (
                                                                2.0 * self._L)
            self._fuerzas_j_rot[1, 0] -= self._c * -(m * a * (2 * self._L - 3 * a) / self._L ** 2) * 3.0 / (2.0 * self._L)
            self._nodo_j.grados_libertad['eje_z'].fuerza -= m * a * (2 * self._L - 3 * a) / self._L ** 2
            self._fuerzas_j_rot[2, 0] -= m * a * (2 * self._L - 3 * a) / self._L ** 2

    def agregar_carga_triangular_descendente(self, q: float):
        self._nodo_i.grados_libertad['x'].fuerza += -7 * q * self._L * self._s / 20
        self._fuerzas_i[0, 0] += -7 * q * self._L * self._s / 20
        self._nodo_i.grados_libertad['y'].fuerza += 7 * q * self._L * self._c / 20
        self._fuerzas_i[1, 0] += 7 * q * self._L * self._c / 20
        self._nodo_i.grados_libertad['eje_z'].fuerza += q * self._L ** 2 / 20
        self._fuerzas_i[2, 0] += q * self._L ** 2 / 20
        self._nodo_j.grados_libertad['x'].fuerza += -3 * q * self._L * self._s / 20
        self._fuerzas_j[0, 0] += -3 * q * self._L * self._s / 20
        self._nodo_j.grados_libertad['y'].fuerza += 3 * q * self._L * self._c / 20
        self._fuerzas_j[1, 0] += 3 * q * self._L * self._c / 20
        self._nodo_j.grados_libertad['eje_z'].fuerza += -q * self._L ** 2 / 30
        self._fuerzas_j[2, 0] += -q * self._L ** 2 / 30

        self._cargas['distribuida'].append([q, 0])

        if self._nodo_j.es_rotula:
            self._nodo_i.grados_libertad['x'].fuerza -= -self._s * (-q * self._L ** 2 / 30) * 3.0 / (2.0 * self._L)
            self._fuerzas_i_rot[0, 0] -= -self._s * (-q * self._L ** 2 / 30) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['y'].fuerza -= self._c * (-q * self._L ** 2 / 30) * 3.0 / (2.0 * self._L)
            self._fuerzas_i_rot[1, 0] -= self._c * (-q * self._L ** 2 / 30) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['eje_z'].fuerza -= 0.5 * (-q * self._L ** 2 / 30)
            self._fuerzas_i_rot[2, 0] -= 0.5 * (-q * self._L ** 2 / 30)
            self._nodo_j.grados_libertad['x'].fuerza -= -self._s * -(-q * self._L ** 2 / 30) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[0, 0] -= -self._s * -(-q * self._L ** 2 / 30) * 3.0 / (2.0 * self._L)
            self._nodo_j.grados_libertad['y'].fuerza -= self._c * -(-q * self._L ** 2 / 30) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[1, 0] -= self._c * -(-q * self._L ** 2 / 30) * 3.0 / (2.0 * self._L)
            self._nodo_j.grados_libertad['eje_z'].fuerza -= -q * self._L ** 2 / 30
            self._fuerzas_j_rot[2, 0] -= -q * self._L ** 2 / 30

    def agregar_carga_triangular_ascendente(self, q: float):
        self._nodo_i.grados_libertad['x'].fuerza += -3 * q * self._L * self._s / 20
        self._fuerzas_i[0, 0] += -3 * q * self._L * self._s / 20
        self._nodo_i.grados_libertad['y'].fuerza += 3 * q * self._L * self._c / 20
        self._fuerzas_i[1, 0] += 3 * q * self._L * self._c / 20
        self._nodo_i.grados_libertad['eje_z'].fuerza += q * self._L ** 2 / 30
        self._fuerzas_i[2, 0] += q * self._L ** 2 / 30
        self._nodo_j.grados_libertad['x'].fuerza += -7 * q * self._L * self._s / 20
        self._fuerzas_j[0, 0] += -7 * q * self._L * self._s / 20
        self._nodo_j.grados_libertad['y'].fuerza += 7 * q * self._L * self._c / 20
        self._fuerzas_j[1, 0] += 7 * q * self._L * self._c / 20
        self._nodo_j.grados_libertad['eje_z'].fuerza += - q * self._L ** 2 / 20
        self._fuerzas_j[2, 0] += - q * self._L ** 2 / 20

        self._cargas['distribuida'].append([0, q])

        if self._nodo_j.es_rotula:
            self._nodo_i.grados_libertad['x'].fuerza -= -self._s * (-q * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._fuerzas_i_rot[0, 0] -= -self._s * (-q * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['y'].fuerza -= self._c * (-q * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._fuerzas_i_rot[1, 0] -= self._c * (-q * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['eje_z'].fuerza -= 0.5 * (-q * self._L ** 2 / 20)
            self._fuerzas_i_rot[2, 0] -= 0.5 * (-q * self._L ** 2 / 20)
            self._nodo_j.grados_libertad['x'].fuerza -= -self._s * -(-q * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[0, 0] -= -self._s * -(-q * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._nodo_j.grados_libertad['y'].fuerza -= self._c * -(-q * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[1, 0] -= self._c * -(-q * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._nodo_j.grados_libertad['eje_z'].fuerza -= -q * self._L ** 2 / 20
            self._fuerzas_j_rot[2, 0] -= -q * self._L ** 2 / 20

    def agregar_carga_axial(self, p: float, a: float = None):
        if a is None:
            a = self._L / 2
        self._nodo_i.grados_libertad['x'].fuerza += p * self._c / 2
        self._fuerzas_i[0, 0] += p * self._c / 2
        self._nodo_i.grados_libertad['y'].fuerza += p * self._s / 2
        self._fuerzas_i[1, 0] += p * self._s / 2
        self._nodo_j.grados_libertad['x'].fuerza += p * self._c / 2
        self._fuerzas_j[0, 0] += p * self._c / 2
        self._nodo_j.grados_libertad['y'].fuerza += p * self._s / 2
        self._fuerzas_j[1, 0] += p * self._s / 2

        self._cargas['axial'].append([p, a])
        self._cargas['axial'].sort(key=lambda l: l[1])

    def _obtener_cargas(self) -> dict:
        return self._cargas

    def _calcular_coeficientes_diagramas(self):
        x_1 = 0.0
        x_2 = self._L
        q_1 = q_2 = 0
        for c in self._cargas['distribuida']:
            q_1 += c[0]
            q_2 += c[1]
        q = [0.0, 0.0]
        for c in self._cargas['puntual']:
            q[0] -= c[0] * (self._L - c[1]) ** 3 / 6
            q[1] -= c[0] * (self._L - c[1]) ** 2 / 2
        for m in self._cargas['momento']:
            q[0] -= -m[0] * (self._L - m[1]) ** 2 / 2
            q[1] -= -m[0] * (self._L - m[1])
        self._coef['A'] = -(q_2 - q_1) / (x_2 - x_1)
        self._coef['B'] = -q_1 - self._coef['A'] * x_1
        A = np.array([[x_1 ** 3 / 6.0, x_1 ** 2 / 2.0, x_1, 1.0], [x_1 ** 2 / 2.0, x_1, 1.0, 0.0],
                      [x_2 ** 3 / 6.0, x_2 ** 2 / 2.0, x_2, 1.0], [x_2 ** 2 / 2.0, x_2, 1.0, 0.0]], dtype=np.double)
        # Se rota los desplazamientos y eliminan los desplazamientos en x
        b = np.matmul(self._T, self._obtener_desplazamientos())[(1, 2, 4, 5), :] * self._E * self._I
        b += np.array([[self._coef['A'] * x_1 ** 5 / 120 + self._coef['B'] * x_1 ** 4 / 24],
                       [self._coef['A'] * x_1 ** 4 / 24 + self._coef['B'] * x_1 ** 3 / 6],
                       [self._coef['A'] * x_2 ** 5 / 120 + self._coef['B'] * x_2 ** 4 / 24 + q[0]],
                       [self._coef['A'] * x_2 ** 4 / 24 + self._coef['B'] * x_2 ** 3 / 6 + q[1]]])
        sol = Gauss(A, b, pivote_parcial=True)
        sol.x[abs(sol.x) < TOL_CERO] = 0.0
        self._coef['c_1'] = sol.x[0, 0]
        self._coef['c_2'] = sol.x[1, 0]
        self._coef['c_3'] = sol.x[2, 0]
        self._coef['c_4'] = sol.x[3, 0]

    def ecuacion_de_axial(self):
        x = sp.symbols('x')
        N = sp.Function('N')(x)
        x_1 = 0.0
        x_2 = self._L
        fuerzas_internas = (np.matmul(np.matmul(self._kp, self._T), self._obtener_desplazamientos()) -
                            np.matmul(self._T, self._obtener_fuerzas() + self._obtener_fuerzas_por_rotula()))
        ec = -fuerzas_internas[0, 0]
        if len(self._cargas['axial']) == 0:
            return sp.Eq(N, sp.Piecewise((ec, (x >= x_1) & (x <= x_2))))
        else:
            dis = [float(x_1)] + [float(x_1 + c[1]) for c in self._cargas['axial']] + [float(x_2)]
            car = [ec]
            for c in self._cargas['axial']:
                car.append(car[-1] - c[0])
            tramos = []
            for i in range(len(dis) - 1):
                tramos.append((car[i], (dis[i] <= x) & (x <= dis[i + 1])))
            return sp.Eq(N, sp.Piecewise(*tramos))

    def ecuacion_de_cortante(self):
        x = sp.symbols('x')
        V = sp.Function('V')(x)
        self._calcular_coeficientes_diagramas()
        x_1 = 0.0
        x_2 = self._L
        ec = -self._coef['A'] * x ** 2 / 2 - self._coef['B'] * x + self._coef['c_1']
        if len(self._cargas['puntual']) == 0:
            return sp.Eq(V, sp.Piecewise((ec, (x >= x_1) & (x <= x_2))))
        else:
            dis = [float(x_1)] + [float(x_1 + c[1]) for c in self._cargas['puntual']] + [float(x_2)]
            car = [ec]
            for c in self._cargas['puntual']:
                car.append(car[-1] + c[0])
            tramos = []
            for i in range(len(dis) - 1):
                tramos.append((car[i], (dis[i] <= x) & (x <= dis[i + 1])))
            return sp.Eq(V, sp.Piecewise(*tramos))

    def ecuacion_de_momento(self):
        x = sp.symbols('x')
        M = sp.Function('M')(x)
        self._calcular_coeficientes_diagramas()
        x_1 = 0.0
        x_2 = self._L
        ec = -self._coef['A'] * x ** 3 / 6 - self._coef['B'] * x ** 2 / 2 + self._coef['c_1'] * x + self._coef[
            'c_2']
        if len(self._cargas['puntual']) == 0 and len(self._cargas['momento']) == 0:
            return sp.Eq(M, sp.Piecewise((ec, (x >= x_1) & (x <= x_2))))
        else:
            cargas_ele = dict()
            for c in self._cargas['puntual']:
                cargas_ele[c[1]] = sp.expand(c[0] * (x - (x_1 + c[1])))
            for m in self._cargas['momento']:
                cargas_ele[m[1]] = sp.expand(cargas_ele.get(m[1], 0.0) - m[0])
            if len(cargas_ele) > 0:
                cargas_ele = dict(sorted(cargas_ele.items(), key=lambda item: item[0]))
            dis = [float(x_1)] + [float(x_1 + c) for c in cargas_ele.keys()] + [float(x_2)]
            #dis = [float(x_1)] + [float(x_1 + c[1]) for c in self._cargas['puntual']] + [float(x_2)]
            car = [ec]
            for c in cargas_ele.values():
                car.append(sp.expand(car[-1] + c))
            tramos = []
            for i in range(len(dis) - 1):
                tramos.append((car[i], (dis[i] <= x) & (x <= dis[i + 1])))
            return sp.Eq(M, sp.Piecewise(*tramos))

    def ecuacion_de_giro(self):
        x = sp.symbols('x')
        phi = sp.Function('phi')(x)
        self._calcular_coeficientes_diagramas()
        x_1 = 0.0
        x_2 = self._L
        ec = (-self._coef['A'] * x ** 4 / 24 - self._coef['B'] * x ** 3 / 6 + self._coef['c_1'] * x ** 2 / 2 +
              self._coef['c_2'] * x + self._coef['c_3']) / self._E / self._I
        if len(self._cargas['puntual']) == 0 and len(self._cargas['momento']) == 0:
            return sp.Eq(phi, sp.Piecewise((ec, (x >= x_1) & (x <= x_2))))
        else:
            cargas_ele = dict()
            for c in self._cargas['puntual']:
                cargas_ele[c[1]] = sp.expand((c[0] * (x - (x_1 + c[1])) ** 2 / 2) / self._E / self._I)
            for m in self._cargas['momento']:
                cargas_ele[m[1]] = sp.expand(cargas_ele.get(m[1], 0.0) - m[0] * (x - (x_1 + m[1])) / self._E / self._I)
            if len(cargas_ele) > 0:
                cargas_ele = dict(sorted(cargas_ele.items(), key=lambda item: item[0]))
            dis = [float(x_1)] + [float(x_1 + c) for c in cargas_ele.keys()] + [float(x_2)]
            # dis = [float(x_1)] + [float(x_1 + c[1]) for c in self._cargas['puntual']] + [float(x_2)]
            car = [ec]
            for c in cargas_ele.values():
                car.append(sp.expand(car[-1] + c))
            # for c in self._cargas['puntual']:
            #     car.append(sp.expand(car[-1] + (c[0] * (x - (x_1 + c[1])) ** 2 / 2) / self._E / self._I))
            tramos = []
            for i in range(len(dis) - 1):
                tramos.append((car[i], (dis[i] <= x) & (x <= dis[i + 1])))
            return sp.Eq(phi, sp.Piecewise(*tramos))

    def ecuacion_de_deflexion(self):
        x = sp.symbols('x')
        y = sp.Function('y')(x)
        self._calcular_coeficientes_diagramas()
        x_1 = 0.0
        x_2 = self._L
        ec = (-self._coef['A'] * x ** 5 / 120 - self._coef['B'] * x ** 4 / 24 + self._coef['c_1'] * x ** 3 / 6 +
              self._coef['c_2'] * x ** 2 / 2 + self._coef['c_3'] * x + self._coef['c_4']) / self._E / self._I
        x = sp.symbols('x')
        if len(self._cargas['puntual']) == 0 and len(self._cargas['momento']) == 0:
            return sp.Eq(y, sp.Piecewise((ec, (x >= x_1) & (x <= x_2))))
        else:
            cargas_ele = dict()
            for c in self._cargas['puntual']:
                cargas_ele[c[1]] = sp.expand((c[0] * (x - (x_1 + c[1])) ** 3 / 6) / self._E / self._I)
            for m in self._cargas['momento']:
                cargas_ele[m[1]] = sp.expand(
                    cargas_ele.get(m[1], 0.0) - (m[0] * (x - (x_1 + m[1])) ** 2 / 2) / self._E / self._I)
            if len(cargas_ele) > 0:
                cargas_ele = dict(sorted(cargas_ele.items(), key=lambda item: item[0]))
            dis = [float(x_1)] + [float(x_1 + c) for c in cargas_ele.keys()] + [float(x_2)]
            # dis = [float(x_1)] + [float(x_1 + c[1]) for c in self._cargas['puntual']] + [float(x_2)]
            car = [ec]
            for c in cargas_ele.values():
                car.append(sp.expand(car[-1] + c))

            # car = [ec]
            # for c in self._cargas['puntual']:
            #     car.append(sp.expand(car[-1] + (c[0] * (x - (x_1 + c[1])) ** 3 / 6) / self._E / self._I))
            tramos = []
            for i in range(len(dis) - 1):
                tramos.append((car[i], (dis[i] <= x) & (x <= dis[i + 1])))
            return sp.Eq(y, sp.Piecewise(*tramos))

    def _obtener_arrays_axiales(self, n_puntos: int = 100):
        x = sp.symbols('x')
        f = self.ecuacion_de_axial()
        x_1 = 0.0
        x_2 = self._L
        lista_x = np.linspace(x_1, x_2, n_puntos)
        ev = sp.lambdify(x, f.args[1], 'numpy')
        lista_n = ev(lista_x)
        lista_p = []
        for c in self._cargas['axial']:
            for fun in f.args[1].args:
                val, b = fun.subs(x, x_1 + c[1])
                if b:
                    lista_p.append((x_1 + c[1], val.evalf()))
        lista_p = [(x_1, ev(x_1))] + lista_p + [(x_2, ev(x_2))]
        lista_p = np.array(lista_p, dtype=float)
        lista_p[:, 1][abs(lista_p[:, 1]) < TOL_CERO] = 0.0
        return lista_x, lista_n, lista_p

    def _obtener_arrays_cortantes(self, n_puntos: int = 100):
        x = sp.symbols('x')
        f = self.ecuacion_de_cortante()
        x_1 = 0.0
        x_2 = self._L
        lista_x = np.linspace(x_1, x_2, n_puntos)
        ev = sp.lambdify(x, f.args[1], 'numpy')
        lista_v = ev(lista_x)
        der = sp.diff(f.args[1])
        p_crit = []
        for i in der.args:
            if sp.degree(i[0]) >= 1:
                p_crit += sp.real_roots(i[0], x)
        #lista_p = [[x_1 + c[1], ev(x_1 + c[1])] for c in self._cargas['puntual']]
        lista_p = []
        for c in self._cargas['puntual']:
            for fun in f.args[1].args:
                val, b = fun.subs(x, x_1 + c[1])
                if b:
                    lista_p.append((x_1 + c[1], val.evalf()))
        lista_p = [(x_1, ev(x_1))] + lista_p + [(x_2, ev(x_2))]
        for item in p_crit:
            lista_p.append((item, f.args[1].subs(x, item).evalf()))
        lista_p = np.array(lista_p, dtype=float)
        lista_p[:, 1][abs(lista_p[:, 1]) < TOL_CERO] = 0.0
        return lista_x, lista_v, lista_p

    def _obtener_arrays_momentos(self, n_puntos: int = 100):
        x = sp.symbols('x')
        f = self.ecuacion_de_momento()
        x_1 = 0.0
        x_2 = self._L
        lista_x = np.linspace(x_1, x_2, n_puntos)
        ev = sp.lambdify(x, f.args[1], 'numpy')
        lista_m = ev(lista_x)
        der = sp.diff(f.args[1])
        p_crit = []
        for i in der.args:
            if sp.degree(i[0]) >= 1:
                p_crit += sp.real_roots(i[0], x)
        lista_p = [(x_1 + c[1], ev(x_1 + c[1])) for c in self._cargas['puntual']]
        for m in self._cargas['momento']:
            for fun in f.args[1].args:
                val, b = fun.subs(x, x_1 + m[1])
                if b:
                    lista_p.append((x_1 + m[1], val.evalf()))
        # lista_p = []
        # for c in self._cargas['puntual']:
        #     for fun in f.args[1].args:
        #         val, b = fun.subs(x, x_1 + c[1])
        #         if b:
        #             lista_p.append((x_1 + c[1], val.evalf()))
        lista_p = [(x_1, ev(x_1))] + lista_p + [(x_2, ev(x_2))]
        for item in p_crit:
            lista_p.append((item, f.args[1].subs(x, item).evalf()))
        lista_p = np.array(lista_p, dtype=float)
        lista_p[:, 1][abs(lista_p[:, 1]) < TOL_CERO] = 0.0
        return lista_x, lista_m, lista_p

    def _obtener_arrays_angulos(self, n_puntos: int = 100):
        x = sp.symbols('x')
        f = self.ecuacion_de_giro()
        x_1 = 0.0
        x_2 = self._L
        lista_x = np.linspace(x_1, x_2, n_puntos)
        ev = sp.lambdify(x, f.args[1], 'numpy')
        lista_o = ev(lista_x)
        der = sp.diff(f.args[1])
        p_crit = []
        for i in der.args:
            if sp.degree(i[0]) >= 1:
                p_crit += sp.real_roots(i[0], x)
        lista_p = [[x_1 + c[1], ev(x_1 + c[1])] for c in self._cargas['puntual']]
        lista_p += [(x_1 + m[1], ev(x_1 + m[1])) for m in self._cargas['momento']]
        # lista_p = []
        # for c in self._cargas['puntual']:
        #     for fun in f.args[1].args:
        #         val, b = fun.subs(x, x_1 + c[1])
        #         if b:
        #             lista_p.append((x_1 + c[1], val.evalf()))
        lista_p = [(x_1, ev(x_1))] + lista_p + [(x_2, ev(x_2))]
        for item in p_crit:
            lista_p.append((item, f.args[1].subs(x, item).evalf()))
        lista_p = np.array(lista_p, dtype=float)
        lista_p[:, 1][abs(lista_p[:, 1]) < TOL_CERO] = 0.0
        return lista_x, lista_o, lista_p

    def _obtener_arrays_deflexion(self, n_puntos: int = 100):
        x = sp.symbols('x')
        f = self.ecuacion_de_deflexion()
        x_1 = 0.0
        x_2 = self._L
        lista_x = np.linspace(x_1, x_2, n_puntos)
        ev = sp.lambdify(x, f.args[1], 'numpy')
        lista_y = ev(lista_x)
        der = sp.diff(f.args[1])
        p_crit = []
        for i in der.args:
            if sp.degree(i[0]) >= 1:
                p_crit += sp.real_roots(i[0], x)
        lista_p = [[x_1 + c[1], ev(x_1 + c[1])] for c in self._cargas['puntual']]
        lista_p += [(x_1 + m[1], ev(x_1 + m[1])) for m in self._cargas['momento']]
        # lista_p = []
        # for c in self._cargas['puntual']:
        #     for fun in f.args[1].args:
        #         val, b = fun.subs(x, x_1 + c[1])
        #         if b:
        #             lista_p.append((x_1 + c[1], val.evalf()))
        lista_p = [(x_1, ev(x_1))] + lista_p + [(x_2, ev(x_2))]
        for item in p_crit:
            lista_p.append((item, f.args[1].subs(x, item).evalf()))
        lista_p = np.array(lista_p, dtype=float)
        lista_p[:, 1][abs(lista_p[:, 1]) < TOL_CERO] = 0.0
        return lista_x, lista_y, lista_p

    def diagrama_de_axial(self, n_puntos: int = 100, local: bool = True):
        l_x, l_y, l_z = self._obtener_arrays_axiales(n_puntos)
        fig, ax = plt.subplots()
        if local:
            plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.5)
            for i in l_z:
                pos_y = 5  # offset escritura
                val_x, val_y = i
                if val_y < 0:
                    pos_y = -5
                plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
                             textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
        else:
            ax.add_patch(patches.PathPatch(self.__obtener_path_elemento(self._L / 20), edgecolor='royalblue',
                                           facecolor='lightsteelblue', lw=0.2))
            max_val = max(abs(l_y))
            if abs(max_val) < 1E-12:
                factor = 0.0
            else:
                factor = 0.5 * self._L / max_val
            x = self._nodo_i.punto[0] + l_x * self._c
            y = self._nodo_i.punto[1] + l_x * self._s
            ly_prima = l_y * factor
            f_x = x - ly_prima * self._s
            f_y = y + ly_prima * self._c
            plt.plot(f_x, f_y, c='g', lw=0.1)
            for i in range(len(x)):
                plt.plot([f_x[i], x[i]], [f_y[i], y[i]], c='g', lw=0.1)
            for i in l_z:
                ang = np.degrees(np.arccos(self._c)) * np.sign(self._s)
                pos_y = 5  # offset escritura
                val_x, val_y = i
                if val_y < 0:
                    pos_y = -5
                x = self._nodo_i.punto[0] + val_x * self._c - val_y * factor * self._s
                y = self._nodo_i.punto[1] + val_x * self._s + val_y * factor * self._c
                plt.annotate(f'${float(val_y):.4G}$', (x, y), c='black',
                             textcoords="offset points", xytext=(-pos_y * self._s, pos_y * self._c), va='center',
                             ha='center', fontsize=8,
                             rotation=ang, rotation_mode='anchor')
            ax.axis('equal')
        plt.grid()
        plt.title('Diagrama de axiales')
        plt.xlabel('$x$')
        plt.ylabel('$N$')
        plt.show()

    def diagrama_de_cortante(self, n_puntos: int = 100, local: bool = True):
        l_x, l_y, l_z = self._obtener_arrays_cortantes(n_puntos)
        fig, ax = plt.subplots()
        if local:
            plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.5)
            for i in l_z:
                pos_y = 5  # offset escritura
                val_x, val_y = i
                if val_y < 0:
                    pos_y = -5
                plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
                             textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
        else:
            ax.add_patch(patches.PathPatch(self.__obtener_path_elemento(self._L / 20), edgecolor='royalblue',
                                           facecolor='lightsteelblue', lw=0.2))
            max_val = max(abs(l_y))
            if abs(max_val) < 1E-12:
                factor = 0.0
            else:
                factor = 0.5 * self._L / max_val
            x = self._nodo_i.punto[0] + l_x * self._c
            y = self._nodo_i.punto[1] + l_x * self._s
            ly_prima = l_y * factor
            f_x = x - ly_prima * self._s
            f_y = y + ly_prima * self._c
            plt.plot(f_x, f_y, c='r', lw=0.1)
            for i in range(len(x)):
                plt.plot([f_x[i], x[i]], [f_y[i], y[i]], c='r', lw=0.1)
            for i in l_z:
                ang = np.degrees(np.arccos(self._c)) * np.sign(self._s)
                pos_y = 5  # offset escritura
                val_x, val_y = i
                if val_y < 0:
                    pos_y = -5
                x = self._nodo_i.punto[0] + val_x * self._c - val_y * factor * self._s
                y = self._nodo_i.punto[1] + val_x * self._s + val_y * factor * self._c
                plt.annotate(f'${float(val_y):.4G}$', (x, y), c='black',
                             textcoords="offset points", xytext=(-pos_y * self._s, pos_y * self._c), va='center',
                             ha='center', fontsize=8,
                             rotation=ang, rotation_mode='anchor')
            ax.axis('equal')
        plt.grid()
        plt.title('Diagrama de cortantes')
        plt.xlabel('$x$')
        plt.ylabel('$V$')
        plt.show()

    def diagrama_de_momento(self, n_puntos: int = 100, local: bool = True):
        l_x, l_y, l_z = self._obtener_arrays_momentos(n_puntos)
        fig, ax = plt.subplots()
        if local:
            plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.5)
            for i in l_z:
                pos_y = 5  # offset escritura
                val_x, val_y = i
                if val_y < 0:
                    pos_y = -5
                plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
                             textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
        else:
            ax.add_patch(patches.PathPatch(self.__obtener_path_elemento(self._L / 20), edgecolor='royalblue',
                                           facecolor='lightsteelblue', lw=0.2))
            max_val = max(abs(l_y))
            if abs(max_val) < 1E-12:
                factor = 0.0
            else:
                factor = 0.5 * self._L / max_val
            x = self._nodo_i.punto[0] + l_x * self._c
            y = self._nodo_i.punto[1] + l_x * self._s
            ly_prima = l_y * factor
            f_x = x - ly_prima * self._s
            f_y = y + ly_prima * self._c
            plt.plot(f_x, f_y, c='r', lw=0.1)
            for i in range(len(x)):
                plt.plot([f_x[i], x[i]], [f_y[i], y[i]], c='r', lw=0.1)
            for i in l_z:
                ang = np.degrees(np.arccos(self._c)) * np.sign(self._s)
                pos_y = 5  # offset escritura
                val_x, val_y = i
                if val_y < 0:
                    pos_y = -5
                x = self._nodo_i.punto[0] + val_x * self._c - val_y * factor * self._s
                y = self._nodo_i.punto[1] + val_x * self._s + val_y * factor * self._c
                plt.annotate(f'${float(val_y):.4G}$', (x, y), c='black',
                             textcoords="offset points", xytext=(-pos_y * self._s, pos_y * self._c), va='center',
                             ha='center', fontsize=8,
                             rotation=ang, rotation_mode='anchor')
            ax.axis('equal')
        plt.grid()
        plt.title('Diagrama de momentos')
        plt.xlabel('$x$')
        plt.ylabel('$M$')
        plt.show()

    def diagrama_de_giro(self, n_puntos: int = 100, local: bool = True):
        l_x, l_y, l_z = self._obtener_arrays_angulos(n_puntos)
        fig, ax = plt.subplots()
        if local:
            plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.5)
            for i in l_z:
                pos_y = 5  # offset escritura
                val_x, val_y = i
                if val_y < 0:
                    pos_y = -5
                plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
                             textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
        else:
            ax.add_patch(patches.PathPatch(self.__obtener_path_elemento(self._L / 20), edgecolor='royalblue',
                                           facecolor='lightsteelblue', lw=0.2))
            max_val = max(abs(l_y))
            if abs(max_val) < 1E-12:
                factor = 0.0
            else:
                factor = 0.5 * self._L / max_val
            x = self._nodo_i.punto[0] + l_x * self._c
            y = self._nodo_i.punto[1] + l_x * self._s
            ly_prima = l_y * factor
            f_x = x - ly_prima * self._s
            f_y = y + ly_prima * self._c
            plt.plot(f_x, f_y, c='r', lw=0.1)
            for i in range(len(x)):
                plt.plot([f_x[i], x[i]], [f_y[i], y[i]], c='r', lw=0.1)
            for i in l_z:
                ang = np.degrees(np.arccos(self._c)) * np.sign(self._s)
                pos_y = 5  # offset escritura
                val_x, val_y = i
                if val_y < 0:
                    pos_y = -5
                x = self._nodo_i.punto[0] + val_x * self._c - val_y * factor * self._s
                y = self._nodo_i.punto[1] + val_x * self._s + val_y * factor * self._c
                plt.annotate(f'${float(val_y):.4G}$', (x, y), c='black',
                             textcoords="offset points", xytext=(-pos_y * self._s, pos_y * self._c), va='center',
                             ha='center', fontsize=8,
                             rotation=ang, rotation_mode='anchor')
            ax.axis('equal')
        plt.grid()
        plt.title('Diagrama de giro')
        plt.xlabel('$x$')
        plt.ylabel(r'$\phi$')
        plt.show()

    def diagrama_de_deflexion(self, n_puntos: int = 100, local: bool = True):
        l_x, l_y, l_z = self._obtener_arrays_deflexion(n_puntos)
        fig, ax = plt.subplots()
        if local:
            plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.5)
            for i in l_z:
                pos_y = 5  # offset escritura
                val_x, val_y = i
                if val_y < 0:
                    pos_y = -5
                plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
                             textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
        else:
            ax.add_patch(patches.PathPatch(self.__obtener_path_elemento(self._L / 20), edgecolor='royalblue',
                                           facecolor='lightsteelblue', lw=0.2))
            max_val = max(abs(l_y))
            if abs(max_val) < 1E-12:
                factor = 0.0
            else:
                factor = 0.5 * self._L / max_val
            x = self._nodo_i.punto[0] + l_x * self._c
            y = self._nodo_i.punto[1] + l_x * self._s
            ly_prima = l_y * factor
            f_x = x - ly_prima * self._s
            f_y = y + ly_prima * self._c
            plt.plot(f_x, f_y, c='r', lw=0.1)
            for i in range(len(x)):
                plt.plot([f_x[i], x[i]], [f_y[i], y[i]], c='r', lw=0.1)
            for i in l_z:
                ang = np.degrees(np.arccos(self._c)) * np.sign(self._s)
                pos_y = 5  # offset escritura
                val_x, val_y = i
                if val_y < 0:
                    pos_y = -5
                x = self._nodo_i.punto[0] + val_x * self._c - val_y * factor * self._s
                y = self._nodo_i.punto[1] + val_x * self._s + val_y * factor * self._c
                plt.annotate(f'${float(val_y):.4G}$', (x, y), c='black',
                             textcoords="offset points", xytext=(-pos_y * self._s, pos_y * self._c), va='center',
                             ha='center', fontsize=8,
                             rotation=ang, rotation_mode='anchor')
            ax.axis('equal')
        plt.grid()
        plt.title('Diagrama de deflexión')
        plt.xlabel('$x$')
        plt.ylabel('$y$')
        plt.show()

    def fuerzas_internas(self):
        fuerzas_internas = np.matmul(self._k.k,
                                     self._obtener_desplazamientos()) - self._obtener_fuerzas() - self._obtener_fuerzas_por_rotula()
        fuerzas_internas[abs(fuerzas_internas) < TOL_CERO] = 0.0
        if es_notebook():
            indice = ['$' + label + '$' for label in self._obtener_etiquetas_fuerzas()]
            return tabulate({'Fuerzas internas': fuerzas_internas}, headers='keys', showindex=indice, tablefmt='html')
        else:
            print(fuerzas_internas)

    def _obtener_etiquetas_fuerzas(self, reducida: bool = False):
        def ajustar_cadena(s: str) -> str:
            if s == 'eje_z':
                return ''
            else:
                return s

        etq = [nodo.grados_libertad[
                   gl].label_fuerza + '^{(' + self.nombre + ')}_{' + nodo.nombre + ajustar_cadena(gl) + '}'
               for nodo in [self._nodo_i, self._nodo_j] for gl in self._k.grados if
               not reducida or nodo.grados_libertad[gl].valor]
        return etq

    def _obtener_etiquetas_fuerzas_local(self, reducida: bool = False):
        def ajustar_cadena(s: str) -> str:
            if s == 'eje_z':
                return ''
            else:
                return s

        etq = [nodo.grados_libertad[
                   gl].label_fuerza + r'^{\prime(' + self.nombre + ')}_{' + nodo.nombre + ajustar_cadena(gl) + '}'
               for nodo in [self._nodo_i, self._nodo_j] for gl in self._k.grados if
               not reducida or nodo.grados_libertad[gl].valor]
        return etq

    def fuerzas_internas_local(self):
        fuerzas_internas = (np.matmul(np.matmul(self._kp, self._T), self._obtener_desplazamientos()) -
                            np.matmul(self._T, self._obtener_fuerzas() + self._obtener_fuerzas_por_rotula()))
        fuerzas_internas[abs(fuerzas_internas) < TOL_CERO] = 0.0
        if es_notebook():
            indice = ['$' + label + '$' for label in self._obtener_etiquetas_fuerzas_local()]
            return tabulate({'Fuerzas internas local': fuerzas_internas}, headers='keys', showindex=indice,
                            tablefmt='html')
        else:
            print(fuerzas_internas)

    def _obtener_desplazamientos(self) -> np.ndarray:
        desplazamiento = None
        for item in self._k.lista_nodos:
            d_i = [d.desplazamiento for d in item.grados_libertad.values() if d.gl in self._k.grados]
            if desplazamiento is None:
                desplazamiento = d_i
            else:
                desplazamiento = np.hstack((desplazamiento, d_i))
        b = np.array(desplazamiento).reshape(-1, 1)
        # Si hay una rotula en el nodo derecho, se ajusta el ángulo
        if self._nodo_j.es_rotula:
            b[5] = (self._fuerzas_j[2] * self._L / self._E - np.matmul(np.array(
                [[- 6 * self._I * self._s / self._L, 6 * self._I * self._c / self._L, 2 * self._I,
                  6 * self._I * self._s / self._L, -6 * self._I * self._c / self._L]]), b[0:5, ])) / 4 / self._I
        return b

    def mostrar_sistema(self, reducida: bool = False):
        """Muestra el sistema de ecuaciones del elemento en formato matricial."""
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(reducida), dtype=object).reshape(-1, 1)
        vec_f = np.array(self._obtener_etiquetas_fuerzas(reducida), dtype=object).reshape(-1, 1)
        if es_notebook():
            texto_latex = r'\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_f,
                                           '{:}') + r'\end{array}\right\}_{\{f\}}=\left[\begin{array}{' + 'c' * \
                           self._k.obtener_matriz(reducida).shape[1] + '}'
            texto_latex += _generar_matrix(self._k.obtener_matriz(reducida),
                                           '{:G}') + r'\end{array}\right]_{[k]}\cdot\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}_{\{d\}}-\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(self._obtener_fuerzas(reducida),
                                           '{:}') + r'\end{array}\right\}_{\{fo\}}'
            display(Math(texto_latex))
        else:
            return np.array2string(self._k.obtener_matriz(reducida),
                                   formatter={'float_kind': lambda x: '{:}'.format(x)})

    def get_matriz_rigidez_local(self):
        return self._kp

    def get_matriz_T(self):
        return self._T

    def __obtener_path_elemento(self, espesor: np.double) -> Path:
        t = espesor
        x_1, y_1, Z_1 = self._nodo_i.punto
        x_2, y_2, Z_2 = self._nodo_j.punto
        c = self._c
        s = self._s
        vertices = np.array([(x_1 + 0.5 * t * s, y_1 - 0.5 * t * c), (x_2 + 0.5 * t * s, y_2 - 0.5 * t * c),
                             (x_2 - 0.5 * t * s, y_2 + 0.5 * t * c), (x_1 - 0.5 * t * s, y_1 + 0.5 * t * c),
                             (x_1 + 0.5 * t * s, y_1 - 0.5 * t * c)])
        codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
        return Path(vertices, codes)

    def diagrama_fuerzas_internas(self):
        def dibujar_momento(p: tuple[float, float], r: float, teta_1: float = 0, teta_2: float = 90, ejes=None,
                            **kwargs):
            c_x, c_y = p
            r /= 72
            alfa = 0
            teta_flecha = teta_2
            if teta_2 < teta_1:
                teta_1, teta_2 = (teta_2, teta_1)
                alfa = 180
                teta_flecha = teta_1
            trans = (fig.dpi_scale_trans + transforms.ScaledTranslation(c_x, c_y, ejes.transData))
            arc = patches.Arc((0, 0), r, r, angle=0, theta1=teta_1, theta2=teta_2, transform=trans
                              , capstyle='round', linestyle='-', **kwargs)
            ejes.add_patch(arc)
            p_x = (r / 2) * np.cos(np.radians(teta_flecha))
            p_y = (r / 2) * np.sin(np.radians(teta_flecha))
            ejes.add_patch(
                patches.RegularPolygon(xy=(p_x, p_y), numVertices=3, radius=r / 20,
                                       orientation=np.radians(teta_flecha + alfa), transform=trans, **kwargs))

        fuerzas_internas = np.matmul(self._k.k,
                                     self._obtener_desplazamientos()) - self._obtener_fuerzas() - self._obtener_fuerzas_por_rotula()
        fuerzas_internas[abs(fuerzas_internas) < TOL_CERO] = 0.0
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
            dibujar_momento((self._nodo_i.punto[0], self._nodo_i.punto[1]), 50, 255, 30, ejes=ax, color='b', lw=2)
            pos = -20
            ali = 'right'
        else:
            dibujar_momento((self._nodo_i.punto[0], self._nodo_i.punto[1]), 50, -75, 150, ejes=ax, color='b', lw=2)
            pos = 20
            ali = 'left'
        ax.annotate('$' + etq[2] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_i.punto[0:2]), xycoords='data',
                    xytext=(pos, 20), textcoords='offset points', va='bottom', ha=ali, size=12)
        fuerza = fuerzas_internas[3, 0]
        if fuerza <= 0.0:
            pos = 50
            ali = 'left'
            sentido = '->'
        else:
            pos = 50
            ali = 'left'
            sentido = '<-'
        ax.annotate('$' + etq[3] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_j.punto[0:2]), xycoords='data',
                    xytext=(pos, 0), textcoords='offset points', va='center', ha=ali, size=12,
                    arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))
        fuerza = fuerzas_internas[4, 0]
        if fuerza <= 0.0:
            pos = 50
            ali = 'bottom'
            sentido = '->'
        else:
            pos = 50
            ali = 'bottom'
            sentido = '<-'
        ax.annotate('$' + etq[4] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_j.punto[0:2]), xycoords='data',
                    xytext=(0, pos), textcoords='offset points', va=ali, ha='center', size=12,
                    arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))
        fuerza = fuerzas_internas[5, 0]
        if fuerza <= 0.0:
            dibujar_momento((self._nodo_j.punto[0], self._nodo_j.punto[1]), 50, 255, 30, ejes=ax, color='b', lw=2)
            pos = -20
            ali = 'right'
        else:
            dibujar_momento((self._nodo_j.punto[0], self._nodo_j.punto[1]), 50, -75, 150, ejes=ax, color='b', lw=2)
            pos = 20
            ali = 'left'
        ax.annotate('$' + etq[5] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_j.punto[0:2]), xycoords='data',
                    xytext=(pos, 20), textcoords='offset points', va='bottom', ha=ali, size=12)
        ax.scatter([self._nodo_i.punto[0], self._nodo_j.punto[0]], [self._nodo_i.punto[1], self._nodo_j.punto[1]],
                   c='navy', marker='o')

        ax.axis('equal')
        ax.axis('off')
        ax.set_xmargin(0.15)
        ax.set_ymargin(0.15)
        plt.show()

    def diagrama_fuerzas_internas_local(self):
        def dibujar_momento(p: tuple[float, float], r: float, teta_1: float = 0, teta_2: float = 90, ejes=None,
                            **kwargs):
            c_x, c_y = p
            r /= 72
            alfa = 0
            teta_flecha = teta_2
            if teta_2 < teta_1:
                teta_1, teta_2 = (teta_2, teta_1)
                alfa = 180
                teta_flecha = teta_1
            trans = (fig.dpi_scale_trans + transforms.ScaledTranslation(c_x, c_y, ejes.transData))
            arc = patches.Arc((0, 0), r, r, angle=0, theta1=teta_1, theta2=teta_2, transform=trans
                              , capstyle='round', linestyle='-', **kwargs)
            ejes.add_patch(arc)
            p_x = (r / 2) * np.cos(np.radians(teta_flecha))
            p_y = (r / 2) * np.sin(np.radians(teta_flecha))
            ejes.add_patch(
                patches.RegularPolygon(xy=(p_x, p_y), numVertices=3, radius=r / 20,
                                       orientation=np.radians(teta_flecha + alfa), transform=trans, **kwargs))

        fuerzas_internas = (np.matmul(np.matmul(self._kp, self._T), self._obtener_desplazamientos()) -
                            np.matmul(self._T, self._obtener_fuerzas() + self._obtener_fuerzas_por_rotula()))
        fuerzas_internas[abs(fuerzas_internas) < TOL_CERO] = 0.0
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
            pos_x = 50 * self._s
            pos_y = -50 * self._c
            ali_v = 'top'
            ali_h = 'center'
            sentido = '<-'
        else:
            pos_x = 50 * self._s
            pos_y = -50 * self._c
            ali_v = 'top'
            ali_h = 'center'
            sentido = '->'
        ax.annotate('',
                    xy=(self._nodo_i.punto[0:2]), xycoords='data',
                    xytext=(pos_x, pos_y), textcoords='offset points', va=ali_v, ha=ali_h, size=12,
                    arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))
        ax.annotate('$' + etq[1] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_i.punto[0:2]), xycoords='data',
                    xytext=(pos_x, pos_y), textcoords='offset points', va=ali_v, ha=ali_h, size=12, rotation=ang,
                    rotation_mode='anchor')
        fuerza = fuerzas_internas[2, 0]
        if fuerza <= 0.0:
            dibujar_momento((self._nodo_i.punto[0], self._nodo_i.punto[1]), 50, 255, 30, ejes=ax, color='b', lw=2)
            pos = -20
            ali = 'right'
        else:
            dibujar_momento((self._nodo_i.punto[0], self._nodo_i.punto[1]), 50, -75, 150, ejes=ax, color='b', lw=2)
            pos = 20
            ali = 'left'
        ax.annotate('$' + etq[2] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_i.punto[0:2]), xycoords='data',
                    xytext=(pos, 20), textcoords='offset points', va='bottom', ha=ali, size=12, rotation=ang,
                    rotation_mode='anchor')

        fuerza = fuerzas_internas[3, 0]
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
        ax.annotate('$' + etq[3] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_j.punto[0:2]), xycoords='data',
                    xytext=(pos_x, pos_y), textcoords='offset points', va=ali_v, ha=ali_h, size=12, rotation=ang,
                    rotation_mode='anchor')

        fuerza = fuerzas_internas[4, 0]
        if fuerza <= 0.0:
            pos_x = -50 * self._s
            pos_y = 50 * self._c
            ali_v = 'bottom'
            ali_h = 'center'
            sentido = '->'
        else:
            pos_x = -50 * self._s
            pos_y = 50 * self._c
            ali_v = 'bottom'
            ali_h = 'center'
            sentido = '<-'
        ax.annotate('',
                    xy=(self._nodo_j.punto[0:2]), xycoords='data',
                    xytext=(pos_x, pos_y), textcoords='offset points', va=ali_v, ha=ali_h, size=12,
                    arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))
        ax.annotate('$' + etq[4] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_j.punto[0:2]), xycoords='data',
                    xytext=(pos_x, pos_y), textcoords='offset points', va=ali_v, ha=ali_h, size=12, rotation=ang,
                    rotation_mode='anchor')
        fuerza = fuerzas_internas[5, 0]
        if fuerza <= 0.0:
            dibujar_momento((self._nodo_j.punto[0], self._nodo_j.punto[1]), 50, 255, 30, ejes=ax, color='b', lw=2)
            pos = -20
            ali = 'right'
        else:
            dibujar_momento((self._nodo_j.punto[0], self._nodo_j.punto[1]), 50, -75, 150, ejes=ax, color='b', lw=2)
            pos = 20
            ali = 'left'
        ax.annotate('$' + etq[5] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_j.punto[0:2]), xycoords='data',
                    xytext=(pos, 20), textcoords='offset points', va='bottom', ha=ali, size=12, rotation=ang,
                    rotation_mode='anchor')
        plt.scatter([self._nodo_i.punto[0], self._nodo_j.punto[0]], [self._nodo_i.punto[1], self._nodo_j.punto[1]],
                    c='navy',
                    marker='o')

        ax.axis('equal')
        ax.axis('off')
        ax.set_xmargin(0.15)
        ax.set_ymargin(0.15)
        plt.show()
