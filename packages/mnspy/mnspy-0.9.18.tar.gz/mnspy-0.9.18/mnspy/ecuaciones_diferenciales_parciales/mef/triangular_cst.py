from mnspy.ecuaciones_diferenciales_parciales.mef import Nodo, Elemento, Rigidez
from mnspy.utilidades import es_notebook, _generar_matrix
from IPython.display import display, Math
from tabulate import tabulate
import numpy as np

class TriangularCST(Elemento):
    """Representa un elemento Triangular de Deformación Constante (CST) para análisis 2D.

    Este elemento se utiliza para modelar problemas de **tensión plana**, donde se asume
    que los esfuerzos en la dirección del espesor (z) son cero (σ_z = τ_xz = τ_yz = 0).
    Es la base para el análisis de placas delgadas sometidas a cargas en su plano.

    El nombre "Deformación Constante" se debe a que las deformaciones (y por lo tanto
    los esfuerzos) son uniformes en todo el elemento.

    Cada nodo del elemento tiene dos grados de libertad:
    1. Desplazamiento en la dirección 'x' global.
    2. Desplazamiento en la dirección 'y' global.

    Attributes
    ----------
    _E : float
        Módulo de Young del material.
    _t : float
        Espesor del elemento.
    _coef_poisson : float
        Coeficiente de Poisson del material.
    _A : float
        Área del elemento en el plano xy.
    _B : np.ndarray
        Matriz de deformación-desplazamiento [B], que relaciona las deformaciones
        en el elemento con los desplazamientos nodales: `{ε} = [B]{d}`.
    _D : np.ndarray
        Matriz constitutiva (esfuerzo-deformación) [D] para tensión plana, que
        relaciona los esfuerzos con las deformaciones: `{σ} = [D]{ε}`.
    _k : Rigidez
        Objeto `Rigidez` que contiene la matriz de rigidez del elemento en
        coordenadas globales.
    """

    def __init__(self, nombre: str, nodo_i: Nodo, nodo_j: Nodo, nodo_m: Nodo, E: float, espesor: float,
                 coef_poisson: float = 0.3):
        """Constructor para el elemento Triangular de Deformación Constante.

        Parameters
        ----------
        nombre : str
            Nombre o identificador del elemento.
        nodo_i : Nodo
            Primer nodo del elemento (orden antihorario).
        nodo_j : Nodo
            Segundo nodo del elemento (orden antihorario).
        nodo_m : Nodo
            Tercer nodo del elemento (orden antihorario).
        E : float
            Módulo de Young del material.
        espesor : float
            Espesor del elemento (t).
        coef_poisson : float, optional
            Coeficiente de Poisson (ν). Por defecto es 0.3.
        """
        super().__init__(nombre, nodo_i, nodo_j, nodo_m)
        self._E = E
        self._t = espesor
        self._coef_poisson = coef_poisson
        x_i, y_i, z = nodo_i.punto
        x_j, y_j, z = nodo_j.punto
        x_m, y_m, z = nodo_m.punto

        # --- Cálculo de coeficientes geométricos para las funciones de forma ---
        # alfa_i = x_j * y_m - y_j * x_m
        # alfa_j = y_i * x_m - x_i * y_m
        # alfa_m = x_i * y_j - y_i * x_j
        beta_i = y_j - y_m
        beta_j = y_m - y_i
        beta_m = y_i - y_j
        gamma_i = x_m - x_j
        gamma_j = x_i - x_m
        gamma_m = x_j - x_i
        self._A = (x_i * (y_j - y_m) + x_j * (y_m - y_i) + x_m * (y_i - y_j)) / 2

        # --- Matriz de deformación-desplazamiento [B] ---
        self._B = (1 / (2 * self._A)) * np.array([[beta_i, 0, beta_j, 0, beta_m, 0],
                            [0, gamma_i, 0, gamma_j, 0, gamma_m],
                            [gamma_i, beta_i, gamma_j, beta_j, gamma_m, beta_m]],
                           dtype=np.double)
        # --- Matriz constitutiva [D] para Tensión Plana ---
        self._D = (E / (1 - coef_poisson ** 2)) * np.array([[1, coef_poisson, 0],
                            [coef_poisson, 1, 0],
                            [0, 0, (1 - coef_poisson) / 2]],
                           dtype=np.double)

        # --- Matriz de rigidez [k] = t * A * [B]^T * [D] * [B] ---
        k_matrix = self._t * abs(self._A) * self._B.T @ self._D @ self._B

        self._k = Rigidez(k_matrix,
                          [self._nodo_i, self._nodo_j, self._nodo_m],
                          ['x', 'y'])
        self._fuerzas_i = np.zeros((len(self._k.grados), 1))
        self._fuerzas_j = np.zeros((len(self._k.grados), 1))
        self._fuerzas_m = np.zeros((len(self._k.grados), 1))
        self._nodo_i.grados_libertad['x'].label_reaccion = 'F'
        self._nodo_i.grados_libertad['x'].label_fuerza = 'f'
        self._nodo_i.grados_libertad['y'].label_reaccion = 'F'
        self._nodo_i.grados_libertad['y'].label_fuerza = 'f'
        self._nodo_j.grados_libertad['x'].label_reaccion = 'F'
        self._nodo_j.grados_libertad['x'].label_fuerza = 'f'
        self._nodo_j.grados_libertad['y'].label_reaccion = 'F'
        self._nodo_j.grados_libertad['y'].label_fuerza = 'f'
        self._nodo_m.grados_libertad['x'].label_reaccion = 'F'
        self._nodo_m.grados_libertad['x'].label_fuerza = 'f'
        self._nodo_m.grados_libertad['y'].label_reaccion = 'F'
        self._nodo_m.grados_libertad['y'].label_fuerza = 'f'

    def _repr_latex_(self):
        """Representación en LaTeX del sistema local del elemento para notebooks."""
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(), dtype=object).reshape(-1, 1)
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
        """Representación del objeto como string."""
        return f'TriangularCST: {self.nombre}'

    def __str__(self):
        """Representación del objeto como string."""
        return 'TriangularCST: ' + self.nombre

    def mostrar_sistema(self, reducida: bool = False):
        """Muestra el sistema de ecuaciones del elemento en formato matricial."""
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(reducida), dtype=object).reshape(-1, 1)
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

    def _obtener_etiquetas_fuerzas(self, reducida: bool = False) -> list[str]:
        """Genera las etiquetas para las fuerzas nodales del elemento."""
        etq = [nodo.grados_libertad[gl].label_fuerza + '^{(' + self.nombre + ')}_{' + nodo.nombre + gl + '}' for nodo
               in [self._nodo_i, self._nodo_j, self._nodo_m] for gl in self._k.grados if
               not reducida or nodo.grados_libertad[gl].valor]
        return etq

    def _calcular_esfuerzos(self) -> np.ndarray:
        """Calcula el vector de esfuerzos {σ} = [D][B]{d} para el elemento.

        Returns
        -------
        np.ndarray
            Vector de esfuerzos [σ_x, σ_y, τ_xy]^T.
        """
        return np.matmul(np.matmul(self._D, self._B), self._obtener_desplazamientos())

    def _calcular_esfuerzos_principales(self) -> list:
        """Calcula los esfuerzos principales y la orientación del plano principal.

        Se basa en las ecuaciones del círculo de Mohr para tensión plana.

        Returns
        -------
        list[float, float, float]
            Una lista con el esfuerzo principal máximo (σ₁), el esfuerzo principal
            mínimo (σ₂) y el ángulo del plano principal (θ_p) en grados.
        """
        esfuerzos = self._calcular_esfuerzos()
        s_x = esfuerzos[0, 0]
        s_y = esfuerzos[1, 0]
        t_xy = esfuerzos[2, 0]

        # Cálculo de los esfuerzos principales
        a = np.sqrt(((s_x - s_y) / 2) ** 2 + t_xy ** 2)
        s_1 = (s_x + s_y) / 2 + a  # Esfuerzo máximo
        s_2 = (s_x + s_y) / 2 - a  # Esfuerzo mínimo

        # Cálculo del ángulo del plano principal
        if s_x == s_y:
            teta = 45
        else:
            teta = np.degrees(0.5 * np.arctan2(2 * t_xy, (s_x - s_y)))
        return [s_1, s_2, teta]

    def esfuerzos(self):
        """Calcula y muestra los componentes de esfuerzo (σ_x, σ_y, τ_xy).

        Returns
        -------
        str or np.ndarray
            Una tabla HTML para notebooks de Jupyter, o imprime y retorna el
            vector de esfuerzos en otros entornos.
        """
        esfuerzos = self._calcular_esfuerzos()
        if es_notebook():
            indice = ['$' + label + '$' for label in [r'\sigma_{x}', r'\sigma_{y}', r'\tau_{xy}']]
            return tabulate({'Esfuerzos': esfuerzos}, headers='keys', showindex=indice, tablefmt='html')
        else:
            print(esfuerzos)
            return esfuerzos

    def esfuerzos_principales(self):
        """Calcula y muestra los esfuerzos principales (σ_max, σ_min) y el ángulo.

        Returns
        -------
        str or list
            Una tabla HTML para notebooks de Jupyter, o imprime y retorna los
            resultados en una lista.
        """
        s_principales = self._calcular_esfuerzos_principales()
        if es_notebook():
            indice = ['$' + label + '$' for label in [r'\sigma_{max}', r'\sigma_{min}', r'\theta_{p}']]
            return tabulate({'Esfuerzos Principales': s_principales}, headers='keys', showindex=indice, tablefmt='html')
        else:
            print(s_principales)
            return s_principales

    def _calcular_esfuerzo_von_mises(self) -> float:
        """Calcula el esfuerzo equivalente de von Mises para tensión plana.

        El esfuerzo de von Mises es un criterio de fluencia para materiales dúctiles.
        Se asume un estado de tensión plana (σ₃ = 0).

        Returns
        -------
        float
            El valor del esfuerzo de von Mises.
        """
        s_principales = self._calcular_esfuerzos_principales()
        s_1, s_2, a = s_principales
        s_3 = 0
        return np.sqrt((s_1 - s_2) ** 2 + (s_2 - s_3) ** 2 + (s_3 - s_1) ** 2) / np.sqrt(2)

    def esfuerzo_von_mises(self):
        """Calcula y muestra el esfuerzo equivalente de von Mises.

        Returns
        -------
        str or float
            Una tabla HTML para notebooks de Jupyter, o imprime y retorna el valor.
        """
        s_vm = self._calcular_esfuerzo_von_mises()
        if es_notebook():
            indice = [r'$\sigma_{vm}$']
            return tabulate({'Esfuerzo de Von Mises': [s_vm]}, headers='keys', showindex=indice, tablefmt='html')
        else:
            print(s_vm)
            return s_vm

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
