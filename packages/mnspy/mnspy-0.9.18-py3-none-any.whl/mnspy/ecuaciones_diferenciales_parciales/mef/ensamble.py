from typing import Any

from mnspy.ecuaciones_diferenciales_parciales.mef.mef import Nodo, Elemento
from mnspy.ecuaciones_diferenciales_parciales.mef.resorte import Resorte
from mnspy.ecuaciones_diferenciales_parciales.mef.barra import Barra
from mnspy.ecuaciones_diferenciales_parciales.mef.armadura import Armadura
from mnspy.ecuaciones_diferenciales_parciales.mef.viga import Viga
from mnspy.ecuaciones_diferenciales_parciales.mef.marco import Marco
from mnspy.ecuaciones_diferenciales_parciales.mef.triangular_cst import TriangularCST
from mnspy.ecuaciones_algebraicas_lineales import Gauss
from mnspy.utilidades import es_notebook, _generar_matrix
from tabulate import tabulate
import gmsh

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from matplotlib import tri
import sympy as sp

sp.init_printing(use_latex=True)


def mallado_estructurado_triangular(ancho: float, altura: float, n_filas: int, n_columnas: int, E: float,
                                    espesor: float, coef_poisson: float = 0.3) -> (
        dict[str, Nodo], list[TriangularCST]):
    """Genera una malla estructurada de elementos triangulares para un dominio rectangular.

    Parameters
    ----------
    ancho : float
        Ancho del dominio rectangular.
    altura : float
        Altura del dominio rectangular.
    n_filas : int
        Número de divisiones en la dirección vertical.
    n_columnas : int
        Número de divisiones en la dirección horizontal.
    E : float
        Módulo de Young del material.
    espesor : float
        Espesor del elemento.
    coef_poisson : float, optional
        Coeficiente de Poisson del material. Por defecto es 0.3.

    Returns
    -------
    tuple[dict[str, Nodo], list[TriangularCST]]
        Un diccionario con los nodos generados y una lista con los elementos
        triangulares (CST).
    """
    lista_nodos = []
    delta_x = ancho / n_columnas
    delta_y = altura / n_filas
    for j in range(n_filas + 1):
        for i in range(n_columnas + 1):
            lista_nodos.append(Nodo(str(i + (n_columnas + 1) * j + 1), i * delta_x, j * delta_y,
                                    grados_libertad={'x': True, 'y': True}))
    lista_elementos = []
    for j in range(n_filas):
        for i in range(n_columnas):
            lista_elementos.append(
                TriangularCST(str(2 * i + 2 * n_columnas * j + 1), lista_nodos[(n_columnas + 1) * j + i],
                              lista_nodos[(n_columnas + 1) * (j + 1) + i + 1],
                              lista_nodos[(n_columnas + 1) * (j + 1) + i], espesor=espesor, E=E,
                              coef_poisson=coef_poisson))  # Elemento inferior izquierdo
            lista_elementos.append(
                TriangularCST(str(2 * i + 2 * n_columnas * j + 2), lista_nodos[(n_columnas + 1) * j + i],
                              lista_nodos[(n_columnas + 1) * j + i + 1],
                              lista_nodos[(n_columnas + 1) * (j + 1) + i + 1], espesor=espesor, E=E,
                              coef_poisson=coef_poisson))  # Elemento superior derecho
    return {n.nombre: n for n in lista_nodos}, lista_elementos


def es_resorte(ele: Elemento) -> bool:
    """Verifica si un elemento es de tipo Resorte.

    Parameters
    ----------
    ele : Elemento
        El elemento a verificar.

    Returns
    -------
    bool
        True si el elemento es una instancia de Resorte.
    """
    return isinstance(ele, Resorte)


def es_barra(ele: Elemento) -> bool:
    """Verifica si un elemento es de tipo Barra.

    Parameters
    ----------
    ele : Elemento
        El elemento a verificar.

    Returns
    -------
    bool
        True si el elemento es una instancia de Barra.
    """
    return isinstance(ele, Barra)


def es_armadura(ele: Elemento) -> bool:
    """Verifica si un elemento es de tipo Armadura.

    Parameters
    ----------
    ele : Elemento
        El elemento a verificar.

    Returns
    -------
    bool
        True si el elemento es una instancia de Armadura.
    """
    return isinstance(ele, Armadura)


def es_viga(ele: Elemento) -> bool:
    """Método estático para identificar si el elemento es una viga

    Parameters
    ----------
    ele: Elemento
        Objeto de tipo Elemento

    Returns
    -------
    True: Si el elemento es una viga
    False: Si el elemento no es una viga
    """
    return isinstance(ele, Viga)


def es_marco(ele: Elemento) -> bool:
    """Verifica si un elemento es de tipo Marco.

    Parameters
    ----------
    ele : Elemento
        El elemento a verificar.

    Returns
    -------
    bool
        True si el elemento es una instancia de Marco.
    """
    return isinstance(ele, Marco)


def es_triangular_cst(ele: Elemento) -> bool:
    """Verifica si un elemento es de tipo TriangularCST.

    Parameters
    ----------
    ele : Elemento
        El elemento a verificar.

    Returns
    -------
    bool
        True si el elemento es una instancia de TriangularCST.
    """
    return isinstance(ele, TriangularCST)


def importar_gmsh(ruta: str, E: float, espesor: float, coef_poisson: float = 0.3) -> (dict, list, dict):
    """Importa una malla 2D desde un archivo .msh generado por Gmsh.

    Lee los nodos y elementos triangulares del archivo y los convierte en
    objetos `Nodo` y `TriangularCST` de `mnspy`. También extrae los grupos
    físicos definidos en Gmsh, que son útiles para aplicar condiciones de
    frontera.

    Parameters
    ----------
    ruta : str
        Ruta al archivo .msh.
    E : float
        Módulo de Young del material.
    espesor : float
        Espesor de los elementos 2D.
    coef_poisson : float, optional
        Coeficiente de Poisson del material. Por defecto es 0.3.

    Returns
    -------
    tuple[dict, list, dict]
        - Un diccionario de nodos.
        - Una lista de elementos `TriangularCST`.
        - Un diccionario de grupos físicos con las etiquetas de los nodos que pertenecen a cada grupo.
    """
    dict_nodos = dict()
    lista_elementos = []
    dict_grupos_fisicos = dict()
    gmsh.initialize()
    gmsh.open(ruta)

    # Extraer nodos
    nodo_etq, nodo_coord, nodo_par = gmsh.model.mesh.getNodes(-1, -1)
    for i in range(len(nodo_etq)):
        n_id = int(nodo_etq[i])
        x, y, z = nodo_coord[3 * i:3 * (i + 1)]
        dict_nodos[n_id] = Nodo(str(n_id), float(x), float(y), float(z), grados_libertad={'x': True, 'y': True})

    # Extraer elementos triangulares (tipo 2 en Gmsh)
    elem_tipo, elem_etq, elem_nodo_etq = gmsh.model.mesh.getElements(-1, -1)
    for i in range(len(elem_tipo)):
        if elem_tipo[i] == 2:
            for j in range(elem_etq[i].size):
                e_id = elem_etq[i][j]
                p_i, p_j, p_m = elem_nodo_etq[i][3 * j:3 * (j + 1)]
                lista_elementos.append(
                    TriangularCST(str(e_id), dict_nodos[p_i], dict_nodos[p_j], dict_nodos[p_m], E, espesor,
                                  coef_poisson))

    # Extraer grupos físicos
    entidades = gmsh.model.getEntities()
    for ent in entidades:
        dim = ent[0]
        tag = ent[1]
        etiquetas = gmsh.model.getPhysicalGroupsForEntity(dim, tag)
        if len(etiquetas):
            for p in etiquetas:
                nombre = gmsh.model.getPhysicalName(dim, p)
                nodo_etq, node_coord, nodo_par = gmsh.model.mesh.getNodes(dim, tag, includeBoundary=True,
                                                                          returnParametricCoord=False)
                dict_grupos_fisicos[nombre] = nodo_etq.tolist()
    gmsh.finalize()
    return dict_nodos, lista_elementos, dict_grupos_fisicos


def obtener_path_viga(x_i: float, x_j: float) -> Path:
    """Genera la ruta SVG para dibujar un elemento de viga."""
    t = (x_j - x_i) / 50
    vertices = np.array([(x_i, - 0.5 * t), (x_j, - 0.5 * t), (x_j, 0.5 * t), (x_i, 0.5 * t), (x_i, - 0.5 * t)])
    codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
    return Path(vertices, codes)


def obtener_path_barra(x_i: float, x_j: float, espesor: float) -> Path:
    """Genera la ruta SVG para dibujar un elemento de barra."""
    t = espesor
    vertices = np.array([(x_i, - 0.5 * t), (x_j, - 0.5 * t), (x_j, 0.5 * t), (x_i, 0.5 * t), (x_i, - 0.5 * t)])
    codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
    return Path(vertices, codes)


def obtener_path_marco(ele: Elemento, espesor: float) -> Path:
    """Genera la ruta SVG para dibujar un elemento de marco 2D."""
    esp = espesor
    x_1, y_1, Z_1 = ele.get_nodo_inicial().punto
    x_2, y_2, Z_2 = ele.get_nodo_final().punto
    lon = np.sqrt((y_2 - y_1) ** 2 + (x_2 - x_1) ** 2)
    # Coseno y seno directores
    c = (x_2 - x_1) / lon
    s = (y_2 - y_1) / lon
    vertices = np.array([(x_1 + 0.5 * esp * s, y_1 - 0.5 * esp * c), (x_2 + 0.5 * esp * s, y_2 - 0.5 * esp * c),
                         (x_2 - 0.5 * esp * s, y_2 + 0.5 * esp * c), (x_1 - 0.5 * esp * s, y_1 + 0.5 * esp * c),
                         (x_1 + 0.5 * esp * s, y_1 - 0.5 * esp * c)])
    codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
    return Path(vertices, codes)


def obtener_path_soporte(x_i: float, h: float, y_i: float = 0.0, estilo: int = 0) -> Path:
    """Genera la ruta SVG para dibujar un soporte estructural."""
    if estilo == 2:
        vertices = np.array([(x_i, y_i), (x_i + 0.5 * h, y_i + h), (x_i - 0.5 * h, y_i + h), (x_i, y_i)])
    elif estilo == 4:
        vertices = np.array([(x_i, y_i), (x_i - h, y_i + 0.5 * h), (x_i - h, y_i - 0.5 * h), (x_i, y_i)])
    elif estilo == 6:
        vertices = np.array([(x_i, y_i), (x_i + h, y_i + 0.5 * h), (x_i + h, y_i - 0.5 * h), (x_i, y_i)])
    else:
        vertices = np.array([(x_i, y_i), (x_i + 0.5 * h, y_i - h), (x_i - 0.5 * h, y_i - h), (x_i, y_i)])
    codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
    return Path(vertices, codes)


def dibujar_fuerza(carga: float, distancia: list[float], ejes, orientacion: str, mostrar_valor: bool = False,
                   color: str = 'b', mag: float = 50):
    """Dibuja una flecha que representa una fuerza nodal en un gráfico."""
    cadena = ""
    if orientacion == 'y':
        ah = 'center'
        if carga < 0:
            pos = (0, mag)
            av = 'bottom'
        elif carga > 0:
            pos = (0, -mag)
            av = 'top'
        else:
            pos = (0, 0)
            av = 'center'
    else:
        av = 'center'
        if carga < 0:
            pos = (mag, 0)
            ah = 'left'
        elif carga > 0:
            pos = (-mag, 0)
            ah = 'right'
        else:
            pos = (0, 0)
            ah = 'center'
    if mostrar_valor:
        cadena = '$' + f'{abs(carga):.5g}' + '$'
        # cadena = '$' + str(abs(carga)) + '$'
    ejes.annotate(cadena, xy=distancia, xycoords='data', xytext=pos,
                  textcoords='offset points', va=av, ha=ah, size=10, c=color,
                  arrowprops=dict(arrowstyle='->', connectionstyle="arc3", color=color))


def dibujar_carga_axial(carga: float, d: float, p_ele: list[list[float]], ejes, factor: float, mostrar_valor: bool = False,
                        color: str = 'b'):
    """Dibuja una flecha que representa una carga axial sobre un elemento."""
    lon = np.sqrt((p_ele[1][0] - p_ele[0][0]) ** 2 + (p_ele[1][1] - p_ele[0][1]) ** 2)
    s = (p_ele[1][1] - p_ele[0][1]) / lon
    c = (p_ele[1][0] - p_ele[0][0]) / lon
    pos = [p_ele[0][0] + d * c, p_ele[0][1] + d * s]
    fuerza = carga * factor
    if abs(fuerza) < 10.0:
        fuerza = np.sign(fuerza) * 10
    if carga < 0:
        dir_a= '<-'
        ah = 'right'
    elif carga > 0:
        dir_a = '<-'
        ah = 'left'
    else:
        dir_a = '-'
        ah = 'center'
    ejes.annotate('', xy=pos, xycoords='data', xytext=(fuerza * c, fuerza * s),
                  textcoords='offset points', va='center', ha='center', size=10, c=color,
                  arrowprops=dict(arrowstyle=dir_a, connectionstyle="arc3", color=color, alpha=0.4))
    if mostrar_valor:
        ang = np.degrees(np.arccos(c)) * np.sign(s)
        cadena = '$' + f'{abs(carga):.5g}' + '$'
        ejes.annotate(cadena, xy=pos, xycoords='data', xytext=(fuerza * c, fuerza * s),
                      textcoords='offset points', va='center', ha=ah, size=10, c=color,
                      rotation=ang, rotation_mode='anchor')


def dibujar_carga_puntual(carga: float, d: float, p_ele: list[list[float]], ejes, factor: float,
                          mostrar_valor: bool = False,
                          color: str = 'b'):
    """Dibuja una flecha que representa una carga puntual sobre un elemento."""
    lon = np.sqrt((p_ele[1][0] - p_ele[0][0]) ** 2 + (p_ele[1][1] - p_ele[0][1]) ** 2)
    s = (p_ele[1][1] - p_ele[0][1]) / lon
    c = (p_ele[1][0] - p_ele[0][0]) / lon
    pos = [p_ele[0][0] + d * c, p_ele[0][1] + d * s]
    fuerza = carga * factor
    if abs(fuerza) < 10.0:
        fuerza = np.sign(fuerza) * 10
    if carga < 0:
        av = 'bottom'
    elif carga > 0:
        av = 'top'
    else:
        av = 'center'
    ejes.annotate('', xy=pos, xycoords='data', xytext=(fuerza * s, -fuerza * c),
                  textcoords='offset points', va=av, ha='center', size=10, c=color,
                  arrowprops=dict(arrowstyle='->', connectionstyle="arc3", color=color, alpha=0.4))
    if mostrar_valor:
        ang = np.degrees(np.arccos(c)) * np.sign(s)
        cadena = '$' + f'{abs(carga):.5g}' + '$'
        ejes.annotate(cadena, xy=pos, xycoords='data', xytext=(fuerza * s, -fuerza * c),
                      textcoords='offset points', va=av, ha='center', size=10, c=color,
                      rotation=ang, rotation_mode='anchor')


def dibujar_carga_distribuida(carga: list[float], p_ele: list[list[float]], ejes,
                              factor: list[int | float]):
    """Dibuja una serie de flechas para representar una carga distribuida."""
    lon = np.sqrt((p_ele[1][0] - p_ele[0][0]) ** 2 + (p_ele[1][1] - p_ele[0][1]) ** 2)
    puntos = np.linspace(0, lon, factor[0])
    for p in puntos:
        c = carga[0] + p * (carga[1] - carga[0]) / lon
        dibujar_carga_puntual(c, p, p_ele, ejes, factor[1], color='black')
    dibujar_carga_puntual(carga[0], 0, p_ele, ejes, factor[1], True, color='black')
    dibujar_carga_puntual(carga[1], lon, p_ele, ejes, factor[1], True, color='black')


class Ensamble:
    """Clase principal para el ensamblaje y análisis de una estructura mediante MEF.

    Esta clase toma una lista de elementos (`Resorte`, `Barra`, `Viga`, etc.),
    ensambla la matriz de rigidez global, resuelve el sistema de ecuaciones
    `[K]{d} = {F}` para encontrar los desplazamientos nodales y calcula las
    reacciones en los soportes. Además, proporciona múltiples métodos para
    visualizar la estructura, las cargas y los resultados (diagramas de
    fuerzas, deformada, esfuerzos, etc.).

    Attributes
    ----------
    _lista_elementos : list[Elemento]
        La lista de todos los elementos que componen la estructura.
    _union : Elemento
        Un objeto `Elemento` que contiene la matriz de rigidez global ensamblada.
    _lista_nodos : list[Nodo]
        La lista de todos los nodos únicos en la estructura.
    """
    def __init__(self, lista_elementos: list[Elemento]):
        """Constructor de la clase Ensamble."""
        # lista_elementos.sort(key=lambda l: l.get_matriz_rigidez().k.size, reverse=True)
        self._lista_elementos = lista_elementos
        self._union = Elemento('')
        self._sle = None
        self._graf: dict[str, float | list[float] | bool | Any] = {'l_resorte': 10.0, 'max_carga_x': -np.inf,
                                                                   'max_carga_y': -np.inf,
                                                                   'lim_x': [np.inf, -np.inf],
                                                                   'lim_y': [np.inf, -np.inf], 'visible_eje_x': True,
                                                                   'visible_eje_y': True}
        self._lista_cargas_puntuales_x = []
        self._lista_cargas_puntuales_y = []
        self._lista_momentos = []
        self._lista_cargas_puntuales = []
        self._lista_cargas_distribuidas = []
        self._lista_cargas_axiales = []
        self._tipo_ensamble = {'resorte': False, 'barra': False, 'armadura': False, 'viga': False, 'marco': False,
                               'triangular_cst': False}
        self._calcular()
        self._lista_nodos = self._union.get_lista_nodos()
        self._procesar_datos()
        plt.ioff()  # deshabilitada interactividad matplotlib

    def _repr_latex_(self):
        """Representación en LaTeX del sistema global de ecuaciones para notebooks."""
        vec_d = np.array(self._union.obtener_rigidez().obtener_etiquetas_desplazamientos(),
                         dtype=object).reshape(-1, 1)
        vec_r = np.array(self._union.obtener_rigidez().obtener_etiquetas_reacciones(), dtype=object).reshape(-1, 1)
        texto_latex = r'\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_r, '{:}') + r'\end{array}\right\}_{\{R\}}+\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(self._union.obtener_rigidez().obtener_fuerzas(),
                                       '{:}') + r'\end{array}\right\}_{\{F_{ext.}\}}=\left[\begin{array}{' + 'c' * \
                       self._union.obtener_rigidez().obtener_matriz().shape[1] + '}'
        texto_latex += _generar_matrix(self._union.obtener_rigidez().obtener_matriz(),
                                       '{:G}') + r'\end{array}\right]_{[K]}\cdot\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}_{\{d\}}'
        return '$' + texto_latex + '$'

    def __repr__(self):
        """Representación del objeto como string."""
        return ' '

    def __str__(self):
        """Representación del objeto como string."""
        return ' '

    def solucion(self):
        """Presenta la solución (desplazamientos y reacciones) en una tabla."""
        d = self._union.obtener_rigidez().obtener_etiquetas_desplazamientos()
        r = self._union.obtener_rigidez().obtener_etiquetas_reacciones()
        if es_notebook():
            desp = ['$' + label + '$' for label in d]
            reacc = ['$' + label + '$' for label in r]
            return tabulate({'Desplazamientos': desp, 'Reacciones': reacc}, headers='keys', showindex=False,
                            tablefmt='html')
        else:
            print(tabulate({'Desplazamientos': d, 'Reacciones': r}, headers='keys', showindex=False, tablefmt='simple'))
            return None

    def _calcular(self):
        """Ensambla la matriz de rigidez global sumando las matrices de cada elemento."""
        if len(self._lista_elementos) > 0:
            self._union = self._lista_elementos[0]
            for i in range(len(self._lista_elementos) - 1):
                self._union = self._union + self._lista_elementos[i + 1]

    def get_nodo(self, nombre: str) -> Nodo | None:
        """Busca y retorna un nodo por su nombre."""
        for n in self._lista_nodos:
            if n.nombre == nombre:
                return n
        return None

    def get_elemento(self, nombre: str) -> Elemento | None:
        """Busca y retorna un elemento por su nombre."""
        for ele in self._lista_elementos:
            if ele.nombre == nombre:
                return ele
        return None

    def solucionar_por_gauss_y_calcular_reacciones(self):
        """Resuelve el sistema de ecuaciones y calcula las reacciones.

        Este es el método principal para obtener la solución completa de la estructura.
        """
        A, b, etiquetas = self.get_sistema_reducido()
        self._sle = Gauss(A, b)
        self._sle.ajustar_etiquetas(etiquetas)
        self.calcular_reacciones(self._sle.x)

    def calcular_reacciones(self, sol_desplazamientos: np.ndarray):
        """Calcula las reacciones a partir de los desplazamientos nodales conocidos.

        Parameters
        ----------
        sol_desplazamientos: matrix | ndarray
            Vector columna con el resultado de los desplazamientos
        """
        self._union.obtener_rigidez().calcular_reacciones(sol_desplazamientos)

    def _procesar_datos(self):
        """Extrae y organiza datos de los elementos para la graficación."""
        if len(self._lista_elementos) > 0:
            # Identifica los tipos de elementos presentes en el ensamble
            for elemento in self._lista_elementos:
                if es_resorte(elemento):
                    self._tipo_ensamble['resorte'] = True
                elif es_barra(elemento):
                    self._tipo_ensamble['barra'] = True
                elif es_armadura(elemento):
                    self._tipo_ensamble['armadura'] = True
                elif es_viga(elemento):
                    self._tipo_ensamble['viga'] = True
                    # Extrae cargas para graficación
                    n_i = elemento.get_nodo_inicial()
                    n_j = elemento.get_nodo_final()
                    for c in elemento._obtener_cargas()['puntual']:
                        self._graf['max_carga_y'] = max(self._graf['max_carga_y'], abs(c[0]))
                        self._lista_cargas_puntuales.append([c[0], [n_i.punto[0:2], n_j.punto[0:2]], c[1]])
                    for m in elemento._obtener_cargas()['momento']:
                        self._lista_momentos.append([m[0], [
                            n_i.punto[0] + m[1] * (n_j.punto[0] - n_i.punto[0]) / elemento.get_longitud(),
                            n_i.punto[1] + m[1] * (n_j.punto[1] - n_i.punto[1]) / elemento.get_longitud()]])
                    for c in elemento._obtener_cargas()['distribuida']:
                        self._graf['max_carga_y'] = max(self._graf['max_carga_y'], abs(c[0]), abs(c[1]))
                        self._lista_cargas_distribuidas.append([c, [n_i.punto[0:2], n_j.punto[0:2]]])
                elif es_marco(elemento):
                    self._tipo_ensamble['marco'] = True
                    # Extrae cargas para graficación
                    n_i = elemento.get_nodo_inicial()
                    n_j = elemento.get_nodo_final()
                    for c in elemento._obtener_cargas()['puntual']:
                        self._graf['max_carga_y'] = max(self._graf['max_carga_y'], abs(c[0]))
                        self._lista_cargas_puntuales.append([c[0], [n_i.punto[0:2], n_j.punto[0:2]], c[1]])
                    for m in elemento._obtener_cargas()['momento']:
                        self._lista_momentos.append([m[0], [
                            n_i.punto[0] + m[1] * (n_j.punto[0] - n_i.punto[0]) / elemento.get_longitud(),
                            n_i.punto[1] + m[1] * (n_j.punto[1] - n_i.punto[1]) / elemento.get_longitud()]])
                    for c in elemento._obtener_cargas()['distribuida']:
                        self._graf['max_carga_y'] = max(self._graf['max_carga_y'], abs(c[0]), abs(c[1]))
                        self._lista_cargas_distribuidas.append([c, [n_i.punto[0:2], n_j.punto[0:2]]])
                    for c in elemento._obtener_cargas()['axial']:
                        self._graf['max_carga_y'] = max(self._graf['max_carga_y'], abs(c[0]))
                        self._lista_cargas_axiales.append([c[0], [n_i.punto[0:2], n_j.punto[0:2]], c[1]])
                elif es_triangular_cst(elemento):
                    self._tipo_ensamble['triangular_cst'] = True
            
            # Determina los límites del dominio para la graficación
            if not (self._tipo_ensamble['resorte'] and (list(self._tipo_ensamble.values()).count(True) == 1)):
                for n in self._lista_nodos:
                    self._graf['lim_x'][0] = min(self._graf['lim_x'][0], n.punto[0])
                    self._graf['lim_x'][1] = max(self._graf['lim_x'][1], n.punto[0])
                    self._graf['lim_y'][0] = min(self._graf['lim_y'][0], n.punto[1])
                    self._graf['lim_y'][1] = max(self._graf['lim_y'][1], n.punto[1])
                self._graf['l_resorte'] = max(self._graf['lim_x'][1] - self._graf['lim_x'][0],
                                              self._graf['lim_y'][1] - self._graf['lim_y'][0]) / 10.0
            else:
                self._graf['visible_eje_x'] = False
                self._graf['visible_eje_y'] = False

            # Ajusta la longitud de los resortes para la visualización si es necesario
            for elemento in self._lista_elementos:
                n_i = elemento.get_nodo_inicial()
                n_j = elemento.get_nodo_final()
                if es_resorte(elemento):
                    if 'y' in n_i.grados_libertad.keys():
                        p = n_i.punto
                        if n_j.punto[0] == 0.0 and n_j.punto[1] == 0.0 and n_j.punto[2] == 0.0:
                            n_j.punto = (p[0], p[1] + self._graf['l_resorte'] * elemento._direccion, p[2])
                        self._graf['lim_y'][0] = min(self._graf['lim_y'][0], n_i.punto[1], n_j.punto[1])
                        self._graf['lim_y'][1] = max(self._graf['lim_y'][1], n_i.punto[1], n_j.punto[1])
                    else:
                        p = n_i.punto
                        if n_j.punto[0] == 0.0 and n_j.punto[1] == 0.0 and n_j.punto[2] == 0.0:
                            n_j.punto = (p[0] + self._graf['l_resorte'] * elemento._direccion, p[1], p[2])
                        self._graf['lim_x'][0] = min(self._graf['lim_x'][0], n_i.punto[0], n_j.punto[0])
                        self._graf['lim_x'][1] = max(self._graf['lim_x'][0], n_i.punto[0], n_j.punto[0])
            if self._tipo_ensamble['viga'] and (list(self._tipo_ensamble.values()).count(True) == 1):
                self._graf['visible_eje_y'] = False
            if self._tipo_ensamble['barra'] and (list(self._tipo_ensamble.values()).count(True) == 1):
                self._graf['visible_eje_y'] = False

            # Extrae las cargas nodales externas
            for n in self._lista_nodos:
                if self._tipo_ensamble['viga'] or self._tipo_ensamble['marco']:
                    if 'x' in n.grados_libertad.keys():
                        self._graf['max_carga_y'] = max(self._graf['max_carga_y'],
                                                        abs(n.fuerzas_externas.get('x', 0.0)))
                    if 'y' in n.grados_libertad.keys():
                        self._graf['max_carga_y'] = max(self._graf['max_carga_y'],
                                                        abs(n.fuerzas_externas.get('y', 0.0)))
                if n.fuerzas_externas.get('x', 0.0) != 0.0:
                    self._lista_cargas_puntuales_x.append([n.fuerzas_externas['x'], n.punto[0:2]])
                if n.fuerzas_externas.get('y', 0.0) != 0.0:
                    self._lista_cargas_puntuales_y.append([n.fuerzas_externas['y'], n.punto[0:2]])
                if n.fuerzas_externas.get('eje_z', 0.0) != 0.0:
                    self._lista_momentos.append([n.fuerzas_externas['eje_z'], n.punto[0:2]])

    def _sistema_ecuaciones_reducido(self):
        """Muestra el sistema de ecuaciones reducido en formato matricial."""
        if self._sle is not None:
            self._sle.mostrar_sistema()

    def _solucion_sistema_ecuaciones_reducido(self):
        """Muestra la solución del sistema reducido en formato de tabla."""
        if self._sle is not None:
            return self._sle.solucion()
        else:
            return None

    def matriz_global_reducida(self):
        """Muestra la matriz de rigidez global reducida."""
        self._union.mostrar_sistema(reducida=True)

    def matriz_global(self):
        """Muestra la matriz de rigidez global completa."""
        self._union.mostrar_sistema()

    def diagrama_cargas(self, mostrar_soportes: bool = True, mostrar_cargas: bool = True,
                        mostrar_nodos: bool = True, mostrar_etiquetas: bool = True):
        """Dibuja un diagrama de la estructura completa con sus cargas y soportes.
        """
        if self._lista_elementos is not None:
            self._graf['fig'], self._graf['ax'] = plt.subplots(figsize=(10, 6))

            # Determinación de tipo de soporte
            # [Tipo Apoyo, Estilo]
            # Tipo Apoyo: 0 Pivotado, 1 empotrado
            # Estilo:
            #       Tipo Apoyo: 0 Pivotado
            #           0: inferior Móvil
            #           1: inferior Fijo
            #           2: superior Móvil
            #           3: superior Fijo
            #           4: izquierda Móvil
            #           5: izquierda Fijo
            #           6: derecha Móvil
            #           7: derecha Fijo
            #       Tipo Apoyo: 1 empotrado
            #           0: fijo izquierdo
            #           1: fijo derecha
            #           2: fijo inferior
            #           3: fijo superior
            for n in self._lista_nodos:
                if 'x' in n.grados_libertad.keys():
                    if n.grados_libertad['x'].valor:
                        if 'y' in n.grados_libertad.keys():
                            if n.grados_libertad['y'].valor:
                                if 'eje_z' in n.grados_libertad.keys():
                                    if n.grados_libertad['eje_z'].valor:
                                        # Libre en los 3 grados
                                        if mostrar_nodos:
                                            self._graf['ax'].plot(n.punto[0], n.punto[1], c='navy', marker='.')
                                    else:
                                        # Se mueve en x, y, y fijo en eje z

                                        # No válido o no implementado
                                        pass
                                else:
                                    # Se mueve en x, y
                                    if mostrar_nodos:
                                        self._graf['ax'].plot(n.punto[0], n.punto[1], c='navy', marker='.')
                            elif 'eje_z' in n.grados_libertad.keys():
                                if n.grados_libertad['eje_z'].valor:
                                    # Se mueve en x y eje z, fijo en y
                                    if n.punto[1] == self._graf['lim_y'][0]:
                                        i = 0
                                    elif n.punto[1] == self._graf['lim_y'][1]:
                                        i = 2
                                    else:
                                        i = 0
                                    if len(n.get_soporte()) == 0:
                                        n.set_soporte([0, i])
                                    # lista_soportes.append([n.punto[0:2], [0, i]])
                                else:
                                    # Se mueve en x, y fijo en y, y eje z
                                    # No válido o no implementado
                                    pass
                            else:
                                # Se mueve en x, fijo en y
                                if n.punto[1] == self._graf['lim_y'][0]:
                                    i = 0
                                elif n.punto[1] == self._graf['lim_y'][1]:
                                    i = 2
                                elif n.punto[0] == self._graf['lim_x'][0]:
                                    i = 4
                                elif n.punto[0] == self._graf['lim_x'][1]:
                                    i = 6
                                else:
                                    i = 0
                                if len(n.get_soporte()) == 0:
                                    n.set_soporte([0, i])
                        elif 'eje_z' in n.grados_libertad.keys():
                            if n.grados_libertad['eje_z'].valor:
                                # Se mueve solo en x, y eje z
                                # Sería una viga vertical, no aplica
                                pass
                                # self._graf['ax'].plot(n.punto[0], n.punto[1], c='navy', marker='.')
                            else:
                                # Se mueve en x, y fijo en eje z
                                # No aplica
                                pass
                        else:
                            # Se mueve solo en x
                            if mostrar_nodos:
                                self._graf['ax'].plot(n.punto[0], n.punto[1], c='navy', marker='.')
                    elif 'y' in n.grados_libertad.keys():
                        if n.grados_libertad['y'].valor:
                            if 'eje_z' in n.grados_libertad.keys():
                                if n.grados_libertad['eje_z'].valor:
                                    # Libre en y, y eje_z, fijo en x
                                    if n.punto[0] == self._graf['lim_x'][0]:
                                        i = 4
                                    elif n.punto[0] == self._graf['lim_x'][1]:
                                        i = 6
                                    else:
                                        i = 4
                                    if len(n.get_soporte()) == 0:
                                        n.set_soporte([0, i])
                                else:
                                    # Se mueve en x, y, y fijo en z
                                    # No válido o no implementado
                                    pass
                            else:
                                # Se mueve en y, fijo en x
                                if n.punto[0] == self._graf['lim_x'][0]:
                                    i = 4
                                elif n.punto[0] == self._graf['lim_x'][1]:
                                    i = 6
                                else:
                                    i = 6
                                if len(n.get_soporte()) == 0:
                                    n.set_soporte([0, i])
                        else:
                            if 'eje_z' in n.grados_libertad.keys():
                                if n.grados_libertad['eje_z'].valor:
                                    # Fijo en x, y, y libre en eje z
                                    if n.punto[1] == self._graf['lim_y'][0]:
                                        i = 1
                                    elif n.punto[1] == self._graf['lim_y'][1]:
                                        i = 3
                                    elif n.punto[0] == self._graf['lim_x'][0]:
                                        i = 5
                                    elif n.punto[0] == self._graf['lim_x'][1]:
                                        i = 7
                                    else:
                                        i = 1
                                    if len(n.get_soporte()) == 0:
                                        n.set_soporte([0, i])
                                else:
                                    # Fijo en x, y, y eje z aplica para marcos
                                    if n.punto[1] == self._graf['lim_y'][0]:
                                        i = 2
                                    elif n.punto[1] == self._graf['lim_y'][1]:
                                        i = 3
                                    elif n.punto[0] == self._graf['lim_x'][0]:
                                        i = 0
                                    elif n.punto[0] == self._graf['lim_x'][1]:
                                        i = 1
                                    else:
                                        i = 0
                                    if len(n.get_soporte()) == 0:
                                        n.set_soporte([1, i])
                                    # lista_soportes.append([n.punto[0:2], [0, i]])
                            else:  # Solo grados x, y fijos
                                if n.punto[1] == self._graf['lim_y'][0]:
                                    i = 1
                                elif n.punto[1] == self._graf['lim_y'][1]:
                                    i = 3
                                elif n.punto[0] == self._graf['lim_x'][0]:
                                    i = 5
                                elif n.punto[0] == self._graf['lim_x'][1]:
                                    i = 7
                                else:
                                    i = 1
                                if len(n.get_soporte()) == 0:
                                    n.set_soporte([0, i])
                    elif 'eje_z' in n.grados_libertad.keys():
                        if n.grados_libertad['eje_z'].valor:
                            # Se mueve solo en eje z, fijo en x
                            # No aplica
                            pass
                            # self._graf['ax'].plot(n.punto[0], n.punto[1], c='navy', marker='.')
                        else:
                            # Fijo en x, y eje z
                            # No aplica, sería viga vertical
                            pass
                    else:
                        # Fijo en x
                        if n.punto[0] == self._graf['lim_x'][0]:
                            i = 0
                        elif n.punto[0] == self._graf['lim_x'][1]:
                            i = 1
                        else:
                            i = 0
                        if len(n.get_soporte()) == 0:
                            n.set_soporte([1, i])
                        # lista_soportes.append([n.punto[0:2], [1, i]])
                elif 'y' in n.grados_libertad.keys():
                    if n.grados_libertad['y'].valor:
                        if 'eje_z' in n.grados_libertad.keys():
                            if n.grados_libertad['eje_z'].valor:
                                # Se mueve en y, y eje z
                                if mostrar_nodos:
                                    self._graf['ax'].plot(n.punto[0], n.punto[1], c='navy', marker='.')
                            else:
                                # Se mueve en y, y fijo en z
                                pass
                        else:
                            # Se mueve en y
                            if mostrar_nodos:
                                self._graf['ax'].plot(n.punto[0], n.punto[1], c='navy', marker='.')
                    elif 'eje_z' in n.grados_libertad.keys():
                        if n.grados_libertad['eje_z'].valor:
                            # Fijo en y, y móvil en el eje z
                            if n.punto[1] == self._graf['lim_y'][0]:
                                i = 0
                            elif n.punto[1] == self._graf['lim_y'][1]:
                                i = 2
                            elif n.punto[0] == self._graf['lim_x'][0]:
                                i = 4
                            elif n.punto[0] == self._graf['lim_x'][1]:
                                i = 6
                            else:
                                i = 0
                            if len(n.get_soporte()) == 0:
                                n.set_soporte([0, i])
                            # lista_soportes.append([n.punto[0:2], [0, i]])
                        else:
                            # Fijo en y, y en el eje z
                            if n.punto[0] == self._graf['lim_x'][0]:
                                i = 0
                            elif n.punto[0] == self._graf['lim_x'][1]:
                                i = 1
                            else:
                                i = 0
                            if len(n.get_soporte()) == 0:
                                n.set_soporte([1, i])
                            # lista_soportes.append([n.punto[0:2], [1, i]])
                    else:
                        # Fijo en y
                        if n.punto[1] == self._graf['lim_y'][0]:
                            i = 2
                        elif n.punto[1] == self._graf['lim_y'][1]:
                            i = 3
                        else:
                            i = 2
                        if len(n.get_soporte()) == 0:
                            n.set_soporte([1, i])
                        # lista_soportes.append([n.punto[0:2], [1, i]])
                else:
                    # No valido ni grado x, ni y
                    pass

            if self._tipo_ensamble['triangular_cst']:
                self.__dibujar_elemento_triangular_cst()
            if self._tipo_ensamble['marco']:
                self.__dibujar_elemento_marco()
            if self._tipo_ensamble['viga']:
                self.__dibujar_elemento_viga()
            if self._tipo_ensamble['armadura']:
                self.__dibujar_elemento_armadura()
            if self._tipo_ensamble['barra']:
                self.__dibujar_elemento_barra()
            if self._tipo_ensamble['resorte']:
                self.__dibujar_elemento_resorte()
            # Soportes y Cargas
            if mostrar_soportes:
                self.__dibujar_soportes()
            if mostrar_cargas:
                self.__dibujar_cargas_nodales()
                self.__dibujar_cargas_elementos()
            ###
            # self._graf['ax'].get_yaxis().set_ticks([])
            self._graf['ax'].spines['top'].set_visible(False)
            self._graf['ax'].spines['right'].set_visible(False)
            if not self._graf['visible_eje_y']:
                self._graf['ax'].spines['left'].set_visible(False)
                self._graf['ax'].get_yaxis().set_ticks([])
            if not self._graf['visible_eje_x']:
                self._graf['ax'].spines['bottom'].set_visible(False)
                self._graf['ax'].get_xaxis().set_ticks([])
            # plt.title('Diagrama de cargas')
            if mostrar_etiquetas:
                for n in self._lista_nodos:
                    self._graf['ax'].text(n.punto[0], n.punto[1], n.nombre,
                                          ha="left", va="top", size=7, alpha=0.9,
                                          bbox=dict(boxstyle="circle,pad=0.1",
                                                    fc="lightgreen", ec="darkslategrey", lw=0.2, alpha=0.7))
            if mostrar_etiquetas:
                for ele in self._lista_elementos:
                    if not es_triangular_cst(ele):
                        x = 0.5 * (ele.get_nodo_inicial().punto[0] + ele.get_nodo_final().punto[0])
                        y = 0.5 * (ele.get_nodo_inicial().punto[1] + ele.get_nodo_final().punto[1])
                    else:
                        x = (ele.get_nodo_inicial().punto[0] + ele.get_nodo_final().punto[0] +
                             ele.get_nodo_medio().punto[
                                 0]) / 3.0
                        y = (ele.get_nodo_inicial().punto[1] + ele.get_nodo_final().punto[1] +
                             ele.get_nodo_medio().punto[
                                 1]) / 3.0
                    self._graf['ax'].text(x, y, ele.nombre,
                                          ha="center", va="center", size=7, alpha=0.9,
                                          bbox=dict(boxstyle="square,pad=0.1",
                                                    fc="lightcoral", ec="indianred", lw=0.2, alpha=0.7))
            plt.xlabel('$x$')
            plt.ylabel('$y$')
            plt.axis('equal')
            plt.show()

    def ecuacion_de_axial(self):
        """Genera la ecuación simbólica por tramos de la fuerza axial."""
        x = sp.symbols('x')
        N = sp.Function('N')(x)
        if self._lista_elementos is not None:
            arg = []
            for elemento in self._lista_elementos:
                arg += list(elemento.ecuacion_de_axial().args[1].args)
            return sp.Eq(N, sp.Piecewise(*arg))
        else:
            return None

    def ecuacion_de_cortante(self):
        """Genera la ecuación simbólica por tramos de la fuerza cortante."""
        x = sp.symbols('x')
        V = sp.Function('V')(x)
        if self._lista_elementos is not None:
            arg = []
            for elemento in self._lista_elementos:
                arg += list(elemento.ecuacion_de_cortante().args[1].args)
            return sp.Eq(V, sp.Piecewise(*arg))
        else:
            return None

    def ecuacion_de_momento(self):
        """Genera la ecuación simbólica por tramos del momento flector."""
        x = sp.symbols('x')
        M = sp.Function('M')(x)
        if self._lista_elementos is not None:
            arg = []
            for elemento in self._lista_elementos:
                arg += list(elemento.ecuacion_de_momento().args[1].args)
            return sp.Eq(M, sp.Piecewise(*arg))
        else:
            return None

    def ecuacion_de_giro(self):
        """Genera la ecuación simbólica por tramos del giro (pendiente)."""
        x = sp.symbols('x')
        phi = sp.Function('phi')(x)
        if self._lista_elementos is not None:
            arg = []
            for elemento in self._lista_elementos:
                arg += list(elemento.ecuacion_de_giro().args[1].args)
            return sp.Eq(phi, sp.Piecewise(*arg))
        else:
            return None

    def ecuacion_de_deflexion(self):
        """Genera la ecuación simbólica por tramos de la deflexión."""
        x = sp.symbols('x')
        y = sp.Function('y')(x)
        if self._lista_elementos is not None:
            arg = []
            for elemento in self._lista_elementos:
                arg += list(elemento.ecuacion_de_deflexion().args[1].args)
            return sp.Eq(y, sp.Piecewise(*arg))
        else:
            return None

    def diagrama_de_axial(self, n_puntos: int = 80):
        """Dibuja el diagrama de fuerza axial para los elementos de marco."""
        if self._lista_elementos is not None:
            fig, ax = plt.subplots()
            t = max((self._graf['lim_x'][1] - self._graf['lim_x'][0]),
                    (self._graf['lim_y'][1] - self._graf['lim_y'][0])) / 20
            max_val = 0
            if self._tipo_ensamble['marco']:
                for ele in self._lista_elementos:
                    if es_marco(ele):
                        l_x, l_y, l_z = ele._obtener_arrays_axiales(int(n_puntos*ele.get_longitud()/20/t))
                        max_val = max(max_val, max(abs(l_y)))
            for elemento in self._lista_elementos:
                if es_marco(elemento):
                    l_x, l_y, l_z = elemento._obtener_arrays_axiales(int(n_puntos*elemento.get_longitud()/20/t))
                    ax.add_patch(
                        patches.PathPatch(obtener_path_marco(elemento, t), edgecolor='lightsteelblue',
                                          facecolor='lightsteelblue', lw=0.2))
                    ax.add_patch(
                        patches.Circle(elemento.get_nodo_inicial().punto[0:2], t / 2, edgecolor='lightsteelblue',
                                       facecolor='lightsteelblue', lw=0.2))
                    ax.add_patch(patches.Circle(elemento.get_nodo_final().punto[0:2], t / 2, edgecolor='lightsteelblue',
                                                facecolor='lightsteelblue', lw=0.2))
                    if abs(max_val) < 1E-12:
                        factor = 0.0
                    else:
                        factor = 8 * t / max_val
                    x = elemento.get_nodo_inicial().punto[0] + l_x * elemento.get_coseno()
                    y = elemento.get_nodo_inicial().punto[1] + l_x * elemento.get_seno()
                    ly_prima = l_y * factor
                    f_x = x - ly_prima * elemento.get_seno()
                    f_y = y + ly_prima * elemento.get_coseno()
                    plt.plot(f_x, f_y, c='C4', lw=0.2)
                    for i in range(len(x)):
                        plt.plot([f_x[i], x[i]], [f_y[i], y[i]], c='C4', lw=0.2)
                    for i in l_z:
                        pos_y = 5  # offset escritura
                        val_x, val_y = i
                        if val_y < 0:
                            pos_y = -5
                        ang = np.degrees(np.arccos(elemento.get_coseno())) * np.sign(elemento.get_seno())
                        x = elemento.get_nodo_inicial().punto[
                                0] + val_x * elemento.get_coseno() - val_y * factor * elemento.get_seno()
                        y = elemento.get_nodo_inicial().punto[
                                1] + val_x * elemento.get_seno() + val_y * factor * elemento.get_coseno()
                        plt.annotate(f'${float(val_y):.4G}$', (x, y), c='black',
                                     textcoords="offset points",
                                     xytext=(-pos_y * elemento.get_seno(), pos_y * elemento.get_coseno()), va='center',
                                     ha='center', fontsize=8,
                                     rotation=ang, rotation_mode='anchor')
                    ax.axis('equal')
            plt.grid()
            plt.title('Diagrama de axiales')
            plt.xlabel('$x$')
            # plt.ylabel('$y$')
            plt.show()

    def diagrama_de_cortante(self, n_puntos: int = 80):
        """Dibuja el diagrama de fuerza cortante para los elementos de viga y marco."""
        if self._lista_elementos is not None:
            fig, ax = plt.subplots()
            t = max((self._graf['lim_x'][1] - self._graf['lim_x'][0]),
                    (self._graf['lim_y'][1] - self._graf['lim_y'][0])) / 20
            max_val = 0
            if self._tipo_ensamble['marco']:
                for ele in self._lista_elementos:
                    if es_marco(ele):
                        l_x, l_y, l_z = ele._obtener_arrays_cortantes(int(n_puntos*ele.get_longitud()/20/t))
                        max_val = max(max_val, max(abs(l_y)))
            for elemento in self._lista_elementos:
                if es_viga(elemento):
                    l_x, l_y, l_z = elemento._obtener_arrays_cortantes(int(n_puntos*elemento.get_longitud()/20/t))
                    plt.fill_between(l_x, l_y, color='C0', lw=0.2, alpha=0.6)
                    for i in l_z:
                        pos_y = 5  # offset escritura
                        val_x, val_y = i
                        if val_y < 0:
                            pos_y = -5
                        plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
                                     textcoords="offset points", xytext=(0, pos_y), va='center', ha='center',
                                     fontsize=8)
                    plt.ylabel('$V$')
                elif es_marco(elemento):
                    l_x, l_y, l_z = elemento._obtener_arrays_cortantes(int(n_puntos*elemento.get_longitud()/20/t))
                    ax.add_patch(
                        patches.PathPatch(obtener_path_marco(elemento, t), edgecolor='lightsteelblue',
                                          facecolor='lightsteelblue', lw=0.2))
                    ax.add_patch(
                        patches.Circle(elemento.get_nodo_inicial().punto[0:2], t / 2, edgecolor='lightsteelblue',
                                       facecolor='lightsteelblue', lw=0.2))
                    ax.add_patch(patches.Circle(elemento.get_nodo_final().punto[0:2], t / 2, edgecolor='lightsteelblue',
                                                facecolor='lightsteelblue', lw=0.2))
                    # max_val = max(abs(l_y))
                    if abs(max_val) < 1E-12:
                        factor = 0.0
                    else:
                        # factor = 0.5 * elemento.get_longitud() / max_val
                        factor = 8 * t / max_val
                    x = elemento.get_nodo_inicial().punto[0] + l_x * elemento.get_coseno()
                    y = elemento.get_nodo_inicial().punto[1] + l_x * elemento.get_seno()
                    ly_prima = l_y * factor
                    f_x = x - ly_prima * elemento.get_seno()
                    f_y = y + ly_prima * elemento.get_coseno()
                    plt.plot(f_x, f_y, c='C0', lw=0.2)
                    for i in range(len(x)):
                        plt.plot([f_x[i], x[i]], [f_y[i], y[i]], c='C0', lw=0.2)
                    for i in l_z:
                        pos_y = 5  # offset escritura
                        val_x, val_y = i
                        if val_y < 0:
                            pos_y = -5
                        ang = np.degrees(np.arccos(elemento.get_coseno())) * np.sign(elemento.get_seno())
                        x = elemento.get_nodo_inicial().punto[
                                0] + val_x * elemento.get_coseno() - val_y * factor * elemento.get_seno()
                        y = elemento.get_nodo_inicial().punto[
                                1] + val_x * elemento.get_seno() + val_y * factor * elemento.get_coseno()
                        plt.annotate(f'${float(val_y):.4G}$', (x, y), c='black',
                                     textcoords="offset points",
                                     xytext=(-pos_y * elemento.get_seno(), pos_y * elemento.get_coseno()), va='center',
                                     ha='center', fontsize=8,
                                     rotation=ang, rotation_mode='anchor')
                    ax.axis('equal')
            plt.grid()
            plt.title('Diagrama de cortante')
            plt.xlabel('$x$')
            # plt.ylabel('$y$')
            plt.show()

    def diagrama_de_momento(self, n_puntos: int = 80):
        """Dibuja el diagrama de momento flector para los elementos de viga y marco."""
        if self._lista_elementos is not None:
            fig, ax = plt.subplots()
            t = max((self._graf['lim_x'][1] - self._graf['lim_x'][0]),
                    (self._graf['lim_y'][1] - self._graf['lim_y'][0])) / 20
            max_val = 0
            if self._tipo_ensamble['marco']:
                for ele in self._lista_elementos:
                    if es_marco(ele):
                        l_x, l_y, l_z = ele._obtener_arrays_momentos(int(n_puntos*ele.get_longitud()/20/t))
                        max_val = max(max_val, max(abs(l_y)))
            for elemento in self._lista_elementos:
                if es_viga(elemento):
                    l_x, l_y, l_z = elemento._obtener_arrays_momentos(int(n_puntos*elemento.get_longitud()/20/t))
                    plt.fill_between(l_x, l_y, color='C1', lw=0.2, alpha=0.6)
                    for i in l_z:
                        pos_y = 5  # offset escritura
                        val_x, val_y = i
                        if val_y < 0:
                            pos_y = -5
                        plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
                                     textcoords="offset points", xytext=(0, pos_y), va='center', ha='center',
                                     fontsize=8)
                    plt.ylabel('$M$')
                elif es_marco(elemento):
                    l_x, l_y, l_z = elemento._obtener_arrays_momentos(int(n_puntos*elemento.get_longitud()/20/t))
                    ax.add_patch(
                        patches.PathPatch(obtener_path_marco(elemento, t), edgecolor='lightsteelblue',
                                          facecolor='lightsteelblue', lw=0.2))
                    ax.add_patch(
                        patches.Circle(elemento.get_nodo_inicial().punto[0:2], t / 2, edgecolor='lightsteelblue',
                                       facecolor='lightsteelblue', lw=0.2))
                    ax.add_patch(patches.Circle(elemento.get_nodo_final().punto[0:2], t / 2, edgecolor='lightsteelblue',
                                                facecolor='lightsteelblue', lw=0.2))
                    # max_val = max(abs(l_y))
                    if abs(max_val) < 1E-12:
                        factor = 0.0
                    else:
                        # factor = 0.5 * elemento.get_longitud() / max_val
                        factor = 8 * t / max_val
                    x = elemento.get_nodo_inicial().punto[0] + l_x * elemento.get_coseno()
                    y = elemento.get_nodo_inicial().punto[1] + l_x * elemento.get_seno()
                    ly_prima = l_y * factor
                    f_x = x - ly_prima * elemento.get_seno()
                    f_y = y + ly_prima * elemento.get_coseno()
                    plt.plot(f_x, f_y, c='C1', lw=0.2)
                    for i in range(len(x)):
                        plt.plot([f_x[i], x[i]], [f_y[i], y[i]], c='C1', lw=0.2)
                    for i in l_z:
                        pos_y = 5  # offset escritura
                        val_x, val_y = i
                        if val_y < 0:
                            pos_y = -5
                        ang = np.degrees(np.arccos(elemento.get_coseno())) * np.sign(elemento.get_seno())
                        x = elemento.get_nodo_inicial().punto[
                                0] + val_x * elemento.get_coseno() - val_y * factor * elemento.get_seno()
                        y = elemento.get_nodo_inicial().punto[
                                1] + val_x * elemento.get_seno() + val_y * factor * elemento.get_coseno()
                        plt.annotate(f'${float(val_y):.4G}$', (x, y), c='black',
                                     textcoords="offset points",
                                     xytext=(-pos_y * elemento.get_seno(), pos_y * elemento.get_coseno()), va='center',
                                     ha='center', fontsize=8,
                                     rotation=ang, rotation_mode='anchor')
                    ax.axis('equal')
            plt.grid()
            plt.title('Diagrama de momento')
            plt.xlabel('$x$')
            # plt.ylabel('$y$')
            plt.show()

    def diagrama_de_giro(self, n_puntos: int = 80):
        """Dibuja el diagrama de giro (pendiente) para los elementos de viga y marco."""
        if self._lista_elementos is not None:
            fig, ax = plt.subplots()
            t = max((self._graf['lim_x'][1] - self._graf['lim_x'][0]),
                    (self._graf['lim_y'][1] - self._graf['lim_y'][0])) / 20
            max_val = 0
            if self._tipo_ensamble['marco']:
                for ele in self._lista_elementos:
                    if es_marco(ele):
                        l_x, l_y, l_z = ele._obtener_arrays_angulos(int(n_puntos*ele.get_longitud()/20/t))
                        max_val = max(max_val, max(abs(l_y)))
            for elemento in self._lista_elementos:
                if es_viga(elemento):
                    l_x, l_y, l_z = elemento._obtener_arrays_angulos(int(n_puntos*elemento.get_longitud()/20/t))
                    plt.fill_between(l_x, l_y, color='C2', lw=0.2, alpha=0.6)
                    for i in l_z:
                        pos_y = 5  # offset escritura
                        val_x, val_y = i
                        if val_y < 0:
                            pos_y = -5
                        plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
                                     textcoords="offset points", xytext=(0, pos_y), va='center', ha='center',
                                     fontsize=8)
                    plt.ylabel(r'$\phi$')
                elif es_marco(elemento):
                    l_x, l_y, l_z = elemento._obtener_arrays_angulos(int(n_puntos*elemento.get_longitud()/20/t))
                    ax.add_patch(
                        patches.PathPatch(obtener_path_marco(elemento, t), edgecolor='lightsteelblue',
                                          facecolor='lightsteelblue', lw=0.2))
                    ax.add_patch(
                        patches.Circle(elemento.get_nodo_inicial().punto[0:2], t / 2, edgecolor='lightsteelblue',
                                       facecolor='lightsteelblue', lw=0.2))
                    ax.add_patch(patches.Circle(elemento.get_nodo_final().punto[0:2], t / 2, edgecolor='lightsteelblue',
                                                facecolor='lightsteelblue', lw=0.2))
                    # max_val = max(abs(l_y))
                    if abs(max_val) < 1E-12:
                        factor = 0.0
                    else:
                        # factor = 0.5 * elemento.get_longitud() / max_val
                        factor = 8 * t / max_val
                    x = elemento.get_nodo_inicial().punto[0] + l_x * elemento.get_coseno()
                    y = elemento.get_nodo_inicial().punto[1] + l_x * elemento.get_seno()
                    ly_prima = l_y * factor
                    f_x = x - ly_prima * elemento.get_seno()
                    f_y = y + ly_prima * elemento.get_coseno()
                    plt.plot(f_x, f_y, c='C2', lw=0.2)
                    for i in range(len(x)):
                        plt.plot([f_x[i], x[i]], [f_y[i], y[i]], c='C2', lw=0.2)
                    for i in l_z:
                        pos_y = 5  # offset escritura
                        val_x, val_y = i
                        if val_y < 0:
                            pos_y = -5
                        ang = np.degrees(np.arccos(elemento.get_coseno())) * np.sign(elemento.get_seno())
                        x = elemento.get_nodo_inicial().punto[
                                0] + val_x * elemento.get_coseno() - val_y * factor * elemento.get_seno()
                        y = elemento.get_nodo_inicial().punto[
                                1] + val_x * elemento.get_seno() + val_y * factor * elemento.get_coseno()
                        plt.annotate(f'${float(val_y):.4G}$', (x, y), c='black',
                                     textcoords="offset points",
                                     xytext=(-pos_y * elemento.get_seno(), pos_y * elemento.get_coseno()), va='center',
                                     ha='center', fontsize=8,
                                     rotation=ang, rotation_mode='anchor')
                    ax.axis('equal')
            plt.grid()
            plt.title('Diagrama de giro')
            plt.xlabel('$x$')
            # plt.ylabel(r'$\phi$')
            plt.show()

    def diagrama_de_deflexion(self, n_puntos: int = 80):
        """Dibuja el diagrama de deflexión para los elementos de viga y marco."""
        if self._lista_elementos is not None:
            fig, ax = plt.subplots()
            t = max((self._graf['lim_x'][1] - self._graf['lim_x'][0]),
                    (self._graf['lim_y'][1] - self._graf['lim_y'][0])) / 20
            max_val = 0
            if self._tipo_ensamble['marco']:
                for ele in self._lista_elementos:
                    if es_marco(ele):
                        l_x, l_y, l_z = ele._obtener_arrays_deflexion(int(n_puntos*ele.get_longitud()/20/t))
                        max_val = max(max_val, max(abs(l_y)))
            for elemento in self._lista_elementos:
                if es_viga(elemento):
                    l_x, l_y, l_z = elemento._obtener_arrays_deflexion(int(n_puntos*elemento.get_longitud()/20/t))
                    plt.fill_between(l_x, l_y, color='C3', lw=0.2, alpha=0.6)
                    for i in l_z:
                        pos_y = 5  # offset escritura
                        val_x, val_y = i
                        if val_y < 0:
                            pos_y = -5
                        plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
                                     textcoords="offset points", xytext=(0, pos_y), va='center', ha='center',
                                     fontsize=8)
                    plt.ylabel('$y$')
                elif es_marco(elemento):
                    l_x, l_y, l_z = elemento._obtener_arrays_deflexion(int(n_puntos*elemento.get_longitud()/20/t))
                    ax.add_patch(
                        patches.PathPatch(obtener_path_marco(elemento, t), edgecolor='lightsteelblue',
                                          facecolor='lightsteelblue', lw=0.2))
                    ax.add_patch(
                        patches.Circle(elemento.get_nodo_inicial().punto[0:2], t / 2, edgecolor='lightsteelblue',
                                       facecolor='lightsteelblue', lw=0.2))
                    ax.add_patch(patches.Circle(elemento.get_nodo_final().punto[0:2], t / 2, edgecolor='lightsteelblue',
                                                facecolor='lightsteelblue', lw=0.2))
                    # max_val = max(abs(l_y))
                    if abs(max_val) < 1E-12:
                        factor = 0.0
                    else:
                        # factor = 0.5 * elemento.get_longitud() / max_val
                        factor = 8 * t / max_val
                    x = elemento.get_nodo_inicial().punto[0] + l_x * elemento.get_coseno()
                    y = elemento.get_nodo_inicial().punto[1] + l_x * elemento.get_seno()
                    ly_prima = l_y * factor
                    f_x = x - ly_prima * elemento.get_seno()
                    f_y = y + ly_prima * elemento.get_coseno()
                    plt.plot(f_x, f_y, c='C3', lw=0.2)
                    for i in range(len(x)):
                        plt.plot([f_x[i], x[i]], [f_y[i], y[i]], c='C3', lw=0.2)
                    for i in l_z:
                        pos_y = 5  # offset escritura
                        val_x, val_y = i
                        if val_y < 0:
                            pos_y = -5
                        ang = np.degrees(np.arccos(elemento.get_coseno())) * np.sign(elemento.get_seno())
                        x = elemento.get_nodo_inicial().punto[
                                0] + val_x * elemento.get_coseno() - val_y * factor * elemento.get_seno()
                        y = elemento.get_nodo_inicial().punto[
                                1] + val_x * elemento.get_seno() + val_y * factor * elemento.get_coseno()
                        plt.annotate(f'${float(val_y):.4G}$', (x, y), c='black',
                                     textcoords="offset points",
                                     xytext=(-pos_y * elemento.get_seno(), pos_y * elemento.get_coseno()), va='center',
                                     ha='center', fontsize=8,
                                     rotation=ang, rotation_mode='anchor')
                    ax.axis('equal')
            plt.grid()
            plt.title('Diagrama de deflexion')
            plt.xlabel('$x$')
            # plt.ylabel('$y$')
            plt.show()

    def deformada(self, magnificacion: float = 1.0, n_puntos: int = 50, mostrar_nodos: bool = True):
        """Dibuja la forma deformada de la estructura, superpuesta a la forma original."""
        if self._lista_elementos is not None:
            fig, ax = plt.subplots(figsize=(15, 5))
            t = max((self._graf['lim_x'][1] - self._graf['lim_x'][0]),
                    (self._graf['lim_y'][1] - self._graf['lim_y'][0])) / 20
            lista_t = []
            for elemento in self._lista_elementos:
                if es_armadura(elemento):
                    x_i = elemento.get_nodo_inicial().punto[0]
                    y_i = elemento.get_nodo_inicial().punto[1]
                    x_j = elemento.get_nodo_final().punto[0]
                    y_j = elemento.get_nodo_final().punto[1]
                    d_x_i = elemento.get_nodo_inicial().grados_libertad['x'].desplazamiento * magnificacion
                    d_y_i = elemento.get_nodo_inicial().grados_libertad['y'].desplazamiento * magnificacion
                    d_x_j = elemento.get_nodo_final().grados_libertad['x'].desplazamiento * magnificacion
                    d_y_j = elemento.get_nodo_final().grados_libertad['y'].desplazamiento * magnificacion
                    plt.plot([x_i, x_j], [y_i, y_j], linestyle='--', c='b', lw=1.0)
                    plt.plot([x_i + d_x_i, x_j + d_x_j], [y_i + d_y_i, y_j + d_y_j], c='C3', lw=2)
                    plt.ylabel('$y$')
                    ax.axis('equal')
                elif es_viga(elemento):
                    l_x, l_y, l_z = elemento._obtener_arrays_deflexion(n_puntos)
                    plt.plot([elemento.get_nodo_inicial().punto[0], elemento.get_nodo_final().punto[0]],
                             [elemento.get_nodo_inicial().punto[1], elemento.get_nodo_final().punto[1]], linestyle='--',
                             c='b', lw=1.0)
                    l_y *= magnificacion
                    plt.plot(l_x, l_y, color='C3', lw=2)
                elif es_marco(elemento):
                    l_x, l_y, l_z = elemento._obtener_arrays_deflexion(n_puntos)
                    d_x_i = elemento.get_nodo_inicial().grados_libertad['x'].desplazamiento
                    d_y_i = elemento.get_nodo_inicial().grados_libertad['y'].desplazamiento
                    d_x_j = elemento.get_nodo_final().grados_libertad['x'].desplazamiento
                    d_y_j = elemento.get_nodo_final().grados_libertad['y'].desplazamiento
                    d_axial_inicial = (d_x_i * elemento.get_coseno() + d_y_i * elemento.get_seno()) * magnificacion
                    d_axial_final = (d_x_j * elemento.get_coseno() + d_y_j * elemento.get_seno()) * magnificacion
                    l_y *= magnificacion
                    x = elemento.get_nodo_inicial().punto[0] + (l_x * (1.0 + (
                            d_axial_final - d_axial_inicial) / elemento.get_longitud()) + d_axial_inicial) * elemento.get_coseno()
                    y = elemento.get_nodo_inicial().punto[1] + (l_x * (1.0 + (
                            d_axial_final - d_axial_inicial) / elemento.get_longitud()) + d_axial_inicial) * elemento.get_seno()
                    f_x = x - l_y * elemento.get_seno()
                    f_y = y + l_y * elemento.get_coseno()
                    plt.plot([elemento.get_nodo_inicial().punto[0], elemento.get_nodo_final().punto[0]],
                             [elemento.get_nodo_inicial().punto[1], elemento.get_nodo_final().punto[1]], linestyle='--',
                             c='b', lw=1.0)
                    plt.plot(f_x, f_y, c='C3', lw=2)
                    plt.ylabel('$y$')
                    ax.axis('equal')
                elif es_triangular_cst(elemento):
                    lista_t.append(
                        [self._lista_nodos.index(elemento.get_nodo_inicial()),
                         self._lista_nodos.index(elemento.get_nodo_final()),
                         self._lista_nodos.index(elemento.get_nodo_medio())])
            if self._tipo_ensamble['triangular_cst']:
                lista_x = []
                lista_y = []
                lista_z = []
                for n in self._lista_nodos:
                    i, j, k = n.punto
                    lista_x.append(i + n.grados_libertad['x'].desplazamiento * magnificacion)
                    lista_y.append(j + n.grados_libertad['y'].desplazamiento * magnificacion)
                    lista_z.append(np.sqrt(
                        n.grados_libertad['x'].desplazamiento ** 2 + n.grados_libertad['y'].desplazamiento ** 2))
                ele = tri.Triangulation(lista_x, lista_y, np.array(lista_t))
                plt.tricontourf(ele, lista_z, levels=64, cmap=plt.jet())
                plt.colorbar()
                if mostrar_nodos:
                    plt.scatter(lista_x, lista_y, color='k', marker='.')
                ax.axis('equal')
                plt.ylabel('$y$')
            plt.grid()
            plt.title('Diagrama de deformada (magnificación : ' + str(magnificacion) + ')')
            plt.xlabel('$x$')
            plt.show()

    def diagrama_de_esfuerzo_von_mises(self, magnificacion: float = 1.0, mostrar_nodos: bool = True,
                                       mostrar_elementos: bool = True):
        """Dibuja el contorno de esfuerzos de von Mises para elementos 2D."""
        if self._lista_elementos is not None:
            fig, ax = plt.subplots(figsize=(15, 5))
            t = max((self._graf['lim_x'][1] - self._graf['lim_x'][0]),
                    (self._graf['lim_y'][1] - self._graf['lim_y'][0])) / 20
            lista_t = []
            for elemento in self._lista_elementos:
                if es_triangular_cst(elemento):
                    lista_t.append(
                        [self._lista_nodos.index(elemento.get_nodo_inicial()),
                         self._lista_nodos.index(elemento.get_nodo_final()),
                         self._lista_nodos.index(elemento.get_nodo_medio())])
            if self._tipo_ensamble['triangular_cst']:
                lista_x = []
                lista_y = []
                lista_z = []
                for n in self._lista_nodos:
                    i, j, k = n.punto
                    lista_x.append(i + n.grados_libertad['x'].desplazamiento * magnificacion)
                    lista_y.append(j + n.grados_libertad['y'].desplazamiento * magnificacion)
                    lista_z.append(np.sqrt(
                        n.grados_libertad['x'].desplazamiento ** 2 + n.grados_libertad['y'].desplazamiento ** 2))

                esf_vm = [vm._calcular_esfuerzo_von_mises() for vm in self._lista_elementos]
                ele = tri.Triangulation(lista_x, lista_y, np.array(lista_t))
                color = 'none'
                if mostrar_elementos:
                    color = 'k'
                plt.tripcolor(ele, facecolors=esf_vm, cmap='YlGn', edgecolors=color, shading='flat', linewidth=0.2)
                plt.colorbar()
                if mostrar_nodos:
                    plt.scatter(lista_x, lista_y, color='k', marker='.')
                ax.axis('equal')
                plt.ylabel('$y$')
            plt.grid()
            plt.title('Esfuerzo Von Mises')
            plt.xlabel('$x$')
            plt.show()

    def diagrama_de_esfuerzo_x(self, magnificacion: float = 1.0, mostrar_nodos: bool = True,
                               mostrar_elementos: bool = True):
        """Dibuja el contorno de esfuerzos en la dirección x para elementos 2D."""
        if self._lista_elementos is not None:
            fig, ax = plt.subplots(figsize=(15, 5))
            t = max((self._graf['lim_x'][1] - self._graf['lim_x'][0]),
                    (self._graf['lim_y'][1] - self._graf['lim_y'][0])) / 20
            lista_t = []
            for elemento in self._lista_elementos:
                if es_triangular_cst(elemento):
                    lista_t.append(
                        [self._lista_nodos.index(elemento.get_nodo_inicial()),
                         self._lista_nodos.index(elemento.get_nodo_final()),
                         self._lista_nodos.index(elemento.get_nodo_medio())])
            if self._tipo_ensamble['triangular_cst']:
                lista_x = []
                lista_y = []
                lista_z = []
                for n in self._lista_nodos:
                    i, j, k = n.punto
                    lista_x.append(i + n.grados_libertad['x'].desplazamiento * magnificacion)
                    lista_y.append(j + n.grados_libertad['y'].desplazamiento * magnificacion)
                    lista_z.append(np.sqrt(
                        n.grados_libertad['x'].desplazamiento ** 2 + n.grados_libertad['y'].desplazamiento ** 2))

                esf_x = [sx._calcular_esfuerzos()[0, 0] for sx in self._lista_elementos]
                ele = tri.Triangulation(lista_x, lista_y, np.array(lista_t))
                color = 'none'
                if mostrar_elementos:
                    color = 'k'
                plt.tripcolor(ele, facecolors=esf_x, cmap='YlGn', edgecolors=color, shading='flat', linewidth=0.2)
                plt.colorbar()
                if mostrar_nodos:
                    plt.scatter(lista_x, lista_y, color='k', marker='.')
                ax.axis('equal')
                plt.ylabel('$y$')
            plt.grid()
            plt.title('Esfuerzo en x')
            plt.xlabel('$x$')
            plt.show()

    def diagrama_de_esfuerzo_y(self, magnificacion: float = 1.0, mostrar_nodos: bool = True,
                               mostrar_elementos: bool = True):
        """Dibuja el contorno de esfuerzos en la dirección y para elementos 2D."""
        if self._lista_elementos is not None:
            fig, ax = plt.subplots(figsize=(15, 5))
            t = max((self._graf['lim_x'][1] - self._graf['lim_x'][0]),
                    (self._graf['lim_y'][1] - self._graf['lim_y'][0])) / 20
            lista_t = []
            for elemento in self._lista_elementos:
                if es_triangular_cst(elemento):
                    lista_t.append(
                        [self._lista_nodos.index(elemento.get_nodo_inicial()),
                         self._lista_nodos.index(elemento.get_nodo_final()),
                         self._lista_nodos.index(elemento.get_nodo_medio())])
            if self._tipo_ensamble['triangular_cst']:
                lista_x = []
                lista_y = []
                lista_z = []
                for n in self._lista_nodos:
                    i, j, k = n.punto
                    lista_x.append(i + n.grados_libertad['x'].desplazamiento * magnificacion)
                    lista_y.append(j + n.grados_libertad['y'].desplazamiento * magnificacion)
                    lista_z.append(np.sqrt(
                        n.grados_libertad['x'].desplazamiento ** 2 + n.grados_libertad['y'].desplazamiento ** 2))

                esf_y = [sy._calcular_esfuerzos()[1, 0] for sy in self._lista_elementos]
                ele = tri.Triangulation(lista_x, lista_y, np.array(lista_t))
                color = 'none'
                if mostrar_elementos:
                    color = 'k'
                plt.tripcolor(ele, facecolors=esf_y, cmap='YlGn', edgecolors=color, shading='flat', linewidth=0.2)
                plt.colorbar()
                if mostrar_nodos:
                    plt.scatter(lista_x, lista_y, color='k', marker='.')
                ax.axis('equal')
                plt.ylabel('$y$')
            plt.grid()
            plt.title('Esfuerzo y')
            plt.xlabel('$x$')
            plt.show()

    def diagrama_de_esfuerzo_cortante(self, magnificacion: float = 1.0, mostrar_nodos: bool = True,
                                      mostrar_elementos: bool = True):
        """Dibuja el contorno de esfuerzos cortantes (tau_xy) para elementos 2D."""
        if self._lista_elementos is not None:
            fig, ax = plt.subplots(figsize=(15, 5))
            t = max((self._graf['lim_x'][1] - self._graf['lim_x'][0]),
                    (self._graf['lim_y'][1] - self._graf['lim_y'][0])) / 20
            lista_t = []
            for elemento in self._lista_elementos:
                if es_triangular_cst(elemento):
                    lista_t.append(
                        [self._lista_nodos.index(elemento.get_nodo_inicial()),
                         self._lista_nodos.index(elemento.get_nodo_final()),
                         self._lista_nodos.index(elemento.get_nodo_medio())])
            if self._tipo_ensamble['triangular_cst']:
                lista_x = []
                lista_y = []
                lista_z = []
                for n in self._lista_nodos:
                    i, j, k = n.punto
                    lista_x.append(i + n.grados_libertad['x'].desplazamiento * magnificacion)
                    lista_y.append(j + n.grados_libertad['y'].desplazamiento * magnificacion)
                    lista_z.append(np.sqrt(
                        n.grados_libertad['x'].desplazamiento ** 2 + n.grados_libertad['y'].desplazamiento ** 2))

                t_xy = [txy._calcular_esfuerzos()[2, 0] for txy in self._lista_elementos]
                ele = tri.Triangulation(lista_x, lista_y, np.array(lista_t))
                color = 'none'
                if mostrar_elementos:
                    color = 'k'
                plt.tripcolor(ele, facecolors=t_xy, cmap='YlGn', edgecolors=color, shading='flat', linewidth=0.2)
                plt.colorbar()
                if mostrar_nodos:
                    plt.scatter(lista_x, lista_y, color='k', marker='.')
                ax.axis('equal')
                plt.ylabel('$y$')
            plt.grid()
            plt.title(r'Esfuerzo cortante $\tau_{xy}$')
            plt.xlabel('$x$')
            plt.show()

    def get_sistema_reducido(self) -> tuple[np.ndarray, np.ndarray, list[str]]:
        """Retorna el sistema de ecuaciones reducido [A]{x} = {b}.

        Returns
        -------
        tuple[np.ndarray, np.ndarray, list[str]]
            - Matriz de rigidez reducida (A).
            - Vector de fuerzas reducido (b).
            - Lista de etiquetas para las incógnitas de desplazamiento.
        """
        return self._union.obtener_rigidez().obtener_sistema_reducido()

    def __dibujar_soportes(self):
        """Dibuja los soportes de la estructura."""
        h = max(self._graf['lim_x'][1] - self._graf['lim_x'][0], self._graf['lim_y'][1] - self._graf['lim_y'][0]) / 15.0
        for n in self._lista_nodos:
            if len(n.get_soporte()) == 0:
                continue
            sop = [n.punto[0:2], n.get_soporte()]
            if sop[1][0] == 0:
                if sop[1][1] == 0:
                    self._graf['ax'].add_patch(patches.PathPatch(obtener_path_soporte(sop[0][0], h, sop[0][1]),
                                                                 edgecolor='gray', facecolor='lightgray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0], sop[0][1]), h / 16,
                                                              edgecolor='black', facecolor='black', lw=0.2))

                    self._graf['ax'].add_patch(patches.Circle((sop[0][0] - h / 2 + h / 8, sop[0][1] - h - h / 8), h / 8,
                                                              edgecolor='gray', facecolor='gray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0], sop[0][1] - h - h / 8), h / 8,
                                                              edgecolor='gray', facecolor='gray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0] + h / 2 - h / 8, sop[0][1] - h - h / 8), h / 8,
                                                              edgecolor='gray', facecolor='gray', lw=0.2))
                    self._graf['ax'].add_patch(
                        patches.Rectangle((sop[0][0] - h / 2, sop[0][1] - h - h / 4), h, -h / 4, lw=0.2, fill=False,
                                          hatch='////////'))
                elif sop[1][1] == 1:
                    self._graf['ax'].add_patch(patches.PathPatch(obtener_path_soporte(sop[0][0], h, sop[0][1]),
                                                                 edgecolor='gray', facecolor='lightgray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0], sop[0][1]), h / 16,
                                                              edgecolor='black', facecolor='black', lw=0.2))
                    self._graf['ax'].add_patch(
                        patches.Rectangle((sop[0][0] - h / 2, sop[0][1] - h), h, -h / 4, lw=0.2, fill=False,
                                          hatch='////////'))
                elif sop[1][1] == 2:
                    self._graf['ax'].add_patch(
                        patches.PathPatch(obtener_path_soporte(sop[0][0], h, sop[0][1], estilo=2),
                                          edgecolor='gray', facecolor='lightgray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0], sop[0][1]), h / 16,
                                                              edgecolor='black', facecolor='black', lw=0.2))

                    self._graf['ax'].add_patch(patches.Circle((sop[0][0] - h / 2 + h / 8, sop[0][1] + h + h / 8), h / 8,
                                                              edgecolor='gray', facecolor='gray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0], sop[0][1] + h + h / 8), h / 8,
                                                              edgecolor='gray', facecolor='gray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0] + h / 2 - h / 8, sop[0][1] + h + h / 8), h / 8,
                                                              edgecolor='gray', facecolor='gray', lw=0.2))
                    self._graf['ax'].add_patch(
                        patches.Rectangle((sop[0][0] - h / 2, sop[0][1] + h + h / 4), h, h / 4, lw=0.2, fill=False,
                                          hatch='////////'))
                elif sop[1][1] == 3:
                    self._graf['ax'].add_patch(
                        patches.PathPatch(obtener_path_soporte(sop[0][0], h, sop[0][1], estilo=2),
                                          edgecolor='gray', facecolor='lightgray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0], sop[0][1]), h / 16,
                                                              edgecolor='black', facecolor='black', lw=0.2))
                    self._graf['ax'].add_patch(
                        patches.Rectangle((sop[0][0] - h / 2, sop[0][1] + h), h, h / 4, lw=0.2, fill=False,
                                          hatch='////////'))
                elif sop[1][1] == 4:
                    self._graf['ax'].add_patch(
                        patches.PathPatch(obtener_path_soporte(sop[0][0], h, sop[0][1], estilo=4),
                                          edgecolor='gray', facecolor='lightgray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0], sop[0][1]), h / 16,
                                                              edgecolor='black', facecolor='black', lw=0.2))

                    self._graf['ax'].add_patch(patches.Circle((sop[0][0] - h - h / 8, sop[0][1] - h / 2 + h / 8), h / 8,
                                                              edgecolor='gray', facecolor='gray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0] - h - h / 8, sop[0][1]), h / 8,
                                                              edgecolor='gray', facecolor='gray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0] - h - h / 8, sop[0][1] + h / 2 - h / 8), h / 8,
                                                              edgecolor='gray', facecolor='gray', lw=0.2))
                    self._graf['ax'].add_patch(
                        patches.Rectangle((sop[0][0] - h - h / 2, sop[0][1] - h / 2), h / 4, h, lw=0.2, fill=False,
                                          hatch='////////'))
                elif sop[1][1] == 5:
                    self._graf['ax'].add_patch(
                        patches.PathPatch(obtener_path_soporte(sop[0][0], h, sop[0][1], estilo=4),
                                          edgecolor='gray', facecolor='lightgray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0], sop[0][1]), h / 16,
                                                              edgecolor='black', facecolor='black', lw=0.2))
                    self._graf['ax'].add_patch(
                        patches.Rectangle((sop[0][0] - h, sop[0][1] - h / 2), -h / 4, h, lw=0.2, fill=False,
                                          hatch='////////'))
                elif sop[1][1] == 6:
                    self._graf['ax'].add_patch(
                        patches.PathPatch(obtener_path_soporte(sop[0][0], h, sop[0][1], estilo=6),
                                          edgecolor='gray', facecolor='lightgray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0], sop[0][1]), h / 16,
                                                              edgecolor='black', facecolor='black', lw=0.2))

                    self._graf['ax'].add_patch(patches.Circle((sop[0][0] + h + h / 8, sop[0][1] - h / 2 + h / 8), h / 8,
                                                              edgecolor='gray', facecolor='gray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0] + h + h / 8, sop[0][1]), h / 8,
                                                              edgecolor='gray', facecolor='gray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0] + h + h / 8, sop[0][1] + h / 2 - h / 8), h / 8,
                                                              edgecolor='gray', facecolor='gray', lw=0.2))
                    self._graf['ax'].add_patch(
                        patches.Rectangle((sop[0][0] + h + h / 4, sop[0][1] - h / 2), h / 4, h, lw=0.2, fill=False,
                                          hatch='////////'))
                elif sop[1][1] == 7:
                    self._graf['ax'].add_patch(
                        patches.PathPatch(obtener_path_soporte(sop[0][0], h, sop[0][1], estilo=6),
                                          edgecolor='gray', facecolor='lightgray', lw=0.2))
                    self._graf['ax'].add_patch(patches.Circle((sop[0][0], sop[0][1]), h / 16,
                                                              edgecolor='black', facecolor='black', lw=0.2))
                    self._graf['ax'].add_patch(
                        patches.Rectangle((sop[0][0] + h, sop[0][1] - h / 2), h / 4, h, lw=0.2, fill=False,
                                          hatch='////////'))
                else:  # No debe ocurrir
                    pass
            elif sop[1][0] == 1:
                if sop[1][1] == 0:
                    self._graf['ax'].add_patch(
                        patches.Rectangle((sop[0][0] - h / 4, sop[0][1] - h / 2), h / 4, h, lw=0.2, fill=True,
                                          hatch='////////'))
                elif sop[1][1] == 1:
                    self._graf['ax'].add_patch(
                        patches.Rectangle((sop[0][0], sop[0][1] - h / 2), h / 4, h, lw=0.2, fill=True,
                                          hatch='////////'))
                elif sop[1][1] == 2:
                    self._graf['ax'].add_patch(
                        patches.Rectangle((sop[0][0] - h / 2, sop[0][1] - h / 4), h, h / 4, lw=0.2, fill=True,
                                          hatch='////////'))
                elif sop[1][1] == 3:
                    self._graf['ax'].add_patch(
                        patches.Rectangle((sop[0][0] - h / 2, sop[0][1]), h, h / 4, lw=0.2, fill=True,
                                          hatch='////////'))
            else:
                pass

    def __dibujar_cargas_nodales(self):
        """Dibuja las fuerzas y momentos aplicados directamente en los nodos."""
        def dibujar_momento(p: list[float, float], r: float, teta_1: float = 0, teta_2: float = 90, axis=None,
                            **kwargs):
            c_x, c_y = p
            r /= 72
            alfa = 0
            teta_flecha = teta_2
            if teta_2 < teta_1:
                teta_1, teta_2 = (teta_2, teta_1)
                alfa = 180
                teta_flecha = teta_1
            trans = (self._graf['fig'].dpi_scale_trans + transforms.ScaledTranslation(c_x, c_y, axis.transData))
            arc = patches.Arc((0, 0), r, r, angle=0, theta1=teta_1, theta2=teta_2, transform=trans
                              , capstyle='round', linestyle='-', **kwargs)
            axis.add_patch(arc)
            p_x = (r / 2) * np.cos(np.radians(teta_flecha))
            p_y = (r / 2) * np.sin(np.radians(teta_flecha))
            axis.add_patch(
                patches.RegularPolygon(xy=(p_x, p_y), numVertices=3, radius=r / 20,
                                       orientation=np.radians(teta_flecha + alfa), transform=trans, **kwargs))

        magnitud = 50  # magnitud en puntos de la carga
        for c in self._lista_cargas_puntuales_x:
            if self._graf['max_carga_y'] != -np.inf:
                magnitud = abs(c[0] * 120.0 / self._graf['max_carga_y'])
            dibujar_fuerza(c[0], c[1], self._graf['ax'], 'x', True, mag=magnitud)
        for c in self._lista_cargas_puntuales_y:
            if self._graf['max_carga_y'] != -np.inf:
                magnitud = abs(c[0] * 120.0 / self._graf['max_carga_y'])
            dibujar_fuerza(c[0], c[1], self._graf['ax'], 'y', True, mag=magnitud)
        for m in self._lista_momentos:
            if m[0] > 0.0:
                pos = 10
                ali = 'left'
                dibujar_momento(m[1], 25, -75, 150, axis=self._graf['ax'], color='green', lw=2)
            else:
                pos = -10
                ali = 'right'
                dibujar_momento(m[1], 25, 255, 30, axis=self._graf['ax'], color='green', lw=2)
            self._graf['ax'].annotate('${:g}$'.format(abs(m[0])),
                                      xy=(m[1]), xycoords='data',
                                      xytext=(pos, 10), textcoords='offset points', va='bottom', ha=ali, size=10,
                                      color='green')

    def __dibujar_cargas_elementos(self):
        """Dibuja las cargas distribuidas y puntuales aplicadas sobre los elementos."""
        if self._graf['max_carga_y'] == 0:
            factor = 1.0
        else:
            factor = float(120.0 / self._graf['max_carga_y'])
        for c in self._lista_cargas_puntuales:
            dibujar_carga_puntual(c[0], c[2], c[1], self._graf['ax'], factor, True)
        for c in self._lista_cargas_distribuidas:
            # fac = [50, factor]
            lon = np.sqrt((c[1][1][1] - c[1][0][1]) ** 2 + (c[1][1][0] - c[1][0][0]) ** 2)
            max_val = max((self._graf['lim_x'][1] - self._graf['lim_x'][0]),
                          (self._graf['lim_y'][1] - self._graf['lim_y'][0]))
            fac = [int(100 * lon / max_val), factor]
            dibujar_carga_distribuida(c[0], c[1], self._graf['ax'], fac)
        for c in self._lista_cargas_axiales:
            dibujar_carga_axial(c[0], c[2], c[1], self._graf['ax'], factor, True)

    def __dibujar_elemento_resorte(self):
        """Dibuja los elementos de tipo resorte."""
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

        def resorte(p_1: tuple, p_2: tuple):
            n = 30
            l_res = ((p_2[0] - p_1[0]) ** 2 + (p_2[1] - p_1[1]) ** 2) ** 0.5
            h = 0.1 * l_res
            t = 0.25 * h
            x_1, y_1 = p_1
            x_2, y_2 = p_2
            c = (p_2[0] - p_1[0]) / l_res
            s = (p_2[1] - p_1[1]) / l_res
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
                    self._graf['ax'].add_patch(patch)
            for i in range(n - 1):
                if i % 2 == 0:
                    patch = patches.PathPatch(dib_resorte((x[i], y[i]), (x[i + 1], y[i + 1]), t), edgecolor='royalblue',
                                              facecolor='lightsteelblue', lw=0.2, alpha=0.4)
                    self._graf['ax'].add_patch(patch)

        for elemento in self._lista_elementos:
            n_i = elemento.get_nodo_inicial()
            n_j = elemento.get_nodo_final()
            if es_resorte(elemento):
                resorte(n_i.punto[0:2], n_j.punto[0:2])

    def __dibujar_elemento_barra(self):
        """Dibuja los elementos de tipo barra."""
        for elemento in self._lista_elementos:
            n_i = elemento.get_nodo_inicial()
            n_j = elemento.get_nodo_final()
            h = max(self._graf['lim_x'][1] - self._graf['lim_x'][0],
                    self._graf['lim_y'][1] - self._graf['lim_y'][0]) / 30.0
            if es_barra(elemento):
                self._graf['ax'].add_patch(
                    patches.PathPatch(obtener_path_barra(n_i.punto[0], n_j.punto[0], h), edgecolor='royalblue',
                                      facecolor='lightsteelblue', lw=0.2))

    def __dibujar_elemento_armadura(self):
        """Dibuja los elementos de tipo armadura."""
        def dib_barra(p_1: tuple, p_2: tuple, t: float):
            lon = ((p_2[0] - p_1[0]) ** 2 + (p_2[1] - p_1[1]) ** 2) ** 0.5
            x_1, y_1 = p_1
            x_2, y_2 = p_2
            c = (p_2[0] - p_1[0]) / lon
            s = (p_2[1] - p_1[1]) / lon
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

        for elemento in self._lista_elementos:
            n_i = elemento.get_nodo_inicial()
            n_j = elemento.get_nodo_final()
            h = max(self._graf['lim_x'][1] - self._graf['lim_x'][0],
                    self._graf['lim_y'][1] - self._graf['lim_y'][0]) / 10.0
            if es_armadura(elemento):
                # dib_barra(n_i.punto[0:2], n_j.punto[0:2], h / 4)
                patch = patches.PathPatch(dib_barra(n_i.punto[0:2], n_j.punto[0:2], h / 4), edgecolor='royalblue',
                                          facecolor='lightsteelblue', lw=0.2)
                self._graf['ax'].add_patch(patch)
                self._graf['ax'].plot(n_i.punto[0], n_i.punto[1], c='navy', marker='.')
                self._graf['ax'].plot(n_j.punto[0], n_j.punto[1], c='navy', marker='.')

    def __dibujar_elemento_viga(self):
        """Dibuja los elementos de tipo viga."""
        min_x = np.inf
        max_x = -np.inf
        for elemento in self._lista_elementos:
            n_i = elemento.get_nodo_inicial()
            n_j = elemento.get_nodo_final()
            if es_viga(elemento):
                min_x = min(min_x, n_i.punto[0], n_j.punto[0])
                max_x = max(max_x, n_i.punto[0], n_j.punto[0])
        self._graf['ax'].add_patch(
            patches.PathPatch(obtener_path_viga(min_x, max_x), edgecolor='royalblue', facecolor='lightsteelblue',
                              lw=0.2))

    def __dibujar_elemento_marco(self):
        """Dibuja los elementos de tipo marco."""
        for elemento in self._lista_elementos:
            if es_marco(elemento):
                n_i = elemento.get_nodo_inicial()
                n_j = elemento.get_nodo_final()
                t = max(self._graf['lim_x'][1] - self._graf['lim_x'][0],
                        self._graf['lim_y'][1] - self._graf['lim_y'][0]) / 30.0
                self._graf['ax'].add_patch(
                    patches.PathPatch(obtener_path_marco(elemento, t), edgecolor='lightsteelblue',
                                      facecolor='lightsteelblue', lw=0.2))
                self._graf['ax'].add_patch(
                    patches.Circle((n_i.punto[0:2]), t / 2, edgecolor='lightsteelblue', facecolor='lightsteelblue',
                                   lw=0.2))
                self._graf['ax'].add_patch(
                    patches.Circle((n_j.punto[0:2]), t / 2, edgecolor='lightsteelblue', facecolor='lightsteelblue',
                                   lw=0.2))

    def __dibujar_elemento_triangular_cst(self):
        """Dibuja los elementos de tipo triangular CST."""
        for elemento in self._lista_elementos:
            n_i = elemento.get_nodo_inicial()
            n_j = elemento.get_nodo_final()
            n_m = elemento.get_nodo_medio()
            if es_triangular_cst(elemento):
                self._graf['ax'].add_patch(
                    patches.Polygon((n_i.punto[0:2], n_j.punto[0:2], n_m.punto[0:2]), edgecolor='royalblue',
                                    facecolor='lightsteelblue', lw=0.2))


def main():
    """Función principal para demostración."""
    n_1 = Nodo('A', 0.0, grados_libertad={'y': False, 'eje_z': True})
    n_2 = Nodo('B', 5.0, grados_libertad={'y': True, 'eje_z': True})
    n_3 = Nodo('C', 3.0, 2.0, grados_libertad={'x': False, 'y': False})
    n_4 = Nodo('D', 3.0, grados_libertad={'x': False, 'y': True, 'eje_z': True})
    n_2.agregar_fuerza_externa(-10, 'y')

    E = 200E6  # kPa
    I = 0.1 * 0.1 ** 3 / 12  # m⁴
    A = np.pi * 10E-3 ** 2 / 4  # m²
    e_1 = Viga('1', n_1, n_4, E=E, I=I)
    e_2 = Viga('2', n_4, n_2, E=E, I=I)
    e_3 = Armadura('3', n_3, n_4, A=A, E=E)

    n_1.agregar_fuerza_externa(-25, 'y')
    e_1 + e_2
    # n_1 = Nodo('1', 0, grados_libertad={'y': False, 'eje_z': True})
    # n_2 = Nodo('2', 6, grados_libertad={'y': False, 'eje_z': True})
    # n_2.agregar_fuerza_externa(80, 'y')
    # e_1 = Viga('1', n_1, n_2, E=200E6, I=1E-4)
    # e_1.agregar_carga_trapezoidal(-30, -90)
    # # e_1.agregar_carga_distribuida(-30)
    # # e_1.agregar_carga_triangular_ascendente(-60)
    # # e_1.agregar_carga_puntual(-20)
    # from mnspy import GaussJordan
    # A, b, etiquetas = e_1.obtener_sistema_reducido()
    # sol = GaussJordan(A, b)
    # sol.ajustar_etiquetas(etiquetas)
    # sol.solucion()
    # e_1.calcular_reacciones(sol.x)
    # e_1.obtener_arrays_deflexion(100)
    # gl = Ensamble([e_1])
    # gl.diagrama_cargas()

    # n_1 = Nodo('A', 0, grados_libertad={'y': False, 'eje_z': True})
    # n_2 = Nodo('1', 2, grados_libertad={'y': True, 'eje_z': True})
    # n_3 = Nodo('2', 4, grados_libertad={'y': True, 'eje_z': True})
    # n_4 = Nodo('B', 6, grados_libertad={'y': False, 'eje_z': True})
    # n_2.agregar_fuerza_externa(-2, 'eje_z')
    # n_3.agregar_fuerza_externa(-4, 'y')
    # e_1 = Viga('1', n_1, n_2, E=200E6, I=1E-4)
    # e_2 = Viga('2', n_2, n_3, E=200E6, I=1E-4)
    # e_3 = Viga('3', n_3, n_4, E=200E6, I=1E-4)
    #
    # from mnspy import Ensamble
    # gl = Ensamble([e_1, e_2, e_3])
    # gl.diagrama_cargas()
    # print(gl.get_sistema_reducido())
    # gl.solucionar_por_gauss_y_calcular_reacciones()
    # print(gl.get_sistema_reducido())
    # gl.matriz_global()

    # n_1 = Nodo('1', 0, 0, grados_libertad={'x': True, 'y': True})
    # n_2 = Nodo('2', 0, 3, grados_libertad={'x': False, 'y': False})
    # n_3 = Nodo('3', 3, 3, grados_libertad={'x': False, 'y': False})
    # n_4 = Nodo('4', 3, 0, grados_libertad={'x': False, 'y': False})
    #
    # e_1 = Armadura('1', n_1, n_2, A=6E-4, E=200E9)
    # e_2 = Armadura('2', n_1, n_3, A=6E-4, E=200E9)
    # e_3 = Armadura('3', n_1, n_4, A=6E-4, E=200E9)
    #
    # n_1.agregar_fuerza_externa(-50000, 'y')
    # mg = e_1 + e_2 + e_3
    # from mnspy import GaussJordan
    # A, b, etiquetas = mg.obtener_sistema_reducido()
    # sol = GaussJordan(A, b)
    # sol.ajustar_etiquetas(etiquetas, True)
    # mg.calcular_reacciones(sol.x)
    # from mnspy import Ensamble
    # gl = Ensamble([e_1, e_2, e_3])
    # gl.diagrama_cargas()

    # n_1 = Nodo('1', 0, 0, grados_libertad={'x': False, 'y': False, 'eje_z': False})
    # n_2 = Nodo('2', 0, 15 * 12, grados_libertad={'x': True, 'y': True, 'eje_z': True})
    # n_3 = Nodo('3', 20 * 12, 15 * 12, grados_libertad={'x': False, 'y': False, 'eje_z': False})
    # e_1 = Marco('1', n_1, n_2, A=12, I=1000, E=29000)
    # e_2 = Marco('2', n_2, n_3, A=12, I=1000, E=29000)
    # e_1.agregar_carga_distribuida(-10)
    # e_2.agregar_carga_puntual(-20)
    # mg = e_1 + e_2
    # from mnspy import GaussJordan
    # A, b, etiquetas = mg.obtener_sistema_reducido()
    # sol = GaussJordan(A, b)
    # sol.ajustar_etiquetas(etiquetas)
    # sol.solucion()
    # mg.calcular_reacciones(sol.x)
    # gl = Ensamble([e_1, e_2])
    # gl.diagrama_cargas()


if __name__ == '__main__':
    main()
