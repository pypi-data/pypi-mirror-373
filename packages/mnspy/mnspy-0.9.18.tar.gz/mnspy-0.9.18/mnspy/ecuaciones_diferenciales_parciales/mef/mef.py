from mnspy.utilidades import es_notebook, _generar_matrix, _formato_float_latex
import numpy as np
from IPython.display import display, Math
import sympy as sp

TOL_CERO = 1E-10
FORMATO_NUM = '{:.10g}'
sp.init_printing(use_latex=True)


def longitud(p1: tuple[float, float, float], p2: tuple[float, float, float]) -> float:
    """Calcula la distancia euclidiana entre dos puntos en el espacio 3D.

    Parameters
    ----------
    p1: tuple[float, float, float]
        Coordenadas (x, y, z) del primer punto.
    p2: tuple[float, float, float]
        Coordenadas (x, y, z) del segundo punto.

    Returns
    -------
    float
        La distancia entre los dos puntos.
    """
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2)


class GradoLibertad:
    """Representa un grado de libertad (GDL) para un nodo en un análisis estructural.

    Un grado de libertad describe una posible dirección de movimiento (traslación o
    rotación) de un nodo. Puede estar libre (móvil) o restringido (fijo).

    Attributes
    ----------
    desplazamiento: float
        Valor del desplazamiento o rotación del nodo para este GDL.
    fuerza: float
        Fuerza o momento externo aplicado en el nodo para este GDL.
    gl: str
        Nombre del grado de libertad (ej. 'x', 'y', 'eje_z').
    label_desplazamiento: str
        Símbolo para el desplazamiento (ej. 'u', 'v', 'phi').
    label_fuerza: str
        Símbolo para la fuerza (ej. 'f', 'm').
    label_reaccion: str
        Símbolo para la reacción (ej. 'F', 'M').
    reaccion: float
        Fuerza o momento de reacción en el nodo para este GDL.
    valor: bool
        Estado del GDL. ``True`` si es móvil (libre), ``False`` si es
        restringido (fijo).
    """

    def __init__(self, gl: str, estado: bool = False):
        """Constructor de la clase GradoLibertad

        Parameters
        ----------
        gl: str
            Define el grado de libertad, puede ser 'x', 'y', 'z', 'eje_x', 'eje_y', 'eje_z'.

        estado: bool, optional
            Establece el estado del GDL. ``True`` para móvil, ``False`` para fijo.
            Por defecto es ``False``.
        """
        self.gl = gl
        self.valor = estado
        self.label_reaccion = None
        self.reaccion = 0.0 if estado else None
        self.label_fuerza = None
        self.fuerza = 0.0
        self.label_desplazamiento = None
        self.desplazamiento = None if estado else 0.0
        if gl == 'x':
            self.label_desplazamiento = 'u'
        elif gl == 'y':
            self.label_desplazamiento = 'v'
        elif gl == 'z':
            self.label_desplazamiento = 'w'
        elif gl == 'eje_x':
            self.label_desplazamiento = r'\phi'
        elif gl == 'eje_y':
            self.label_desplazamiento = r'\phi'
        elif gl == 'eje_z':
            self.label_desplazamiento = r'\phi'
        else:
            self.label_desplazamiento = '-'

    def __repr__(self):
        """Representación del objeto como string.

        Returns
        -------
        str
            'móvil' o 'fijo' según el estado del GDL.
        """
        return self.__str__()

    def __str__(self):
        """Representación del objeto como string.

        Returns
        -------
        str
            'móvil' o 'fijo' según el estado del GDL.
        """
        texto = 'móvil' if self.valor else 'fijo'
        return texto


class Nodo:
    """Representa un nodo en una estructura de elementos finitos.

    Un nodo es un punto en el espacio que tiene coordenadas, grados de libertad,
    y al cual se le pueden aplicar fuerzas externas o desplazamientos.

    Attributes
    ----------
    nombre: str
        Nombre asignado al nodo
    punto: tuple[float, float, float]
        Coordenadas (x, y, z) del nodo.
    grados_libertad: dict[str, GradoLibertad]
        Diccionario que contiene los objetos `GradoLibertad` asociados al nodo.
    es_rotula: bool
        Si es ``True``, se considera que el nodo es una rótula (momento cero),
        aplicable a elementos tipo viga y marco.

    Methods
    -------
    agregar_fuerza_externa(carga: float, gl: str):
        Añade una fuerza o momento externo a un grado de libertad específico.
    ajustar_grado_libertad(gl: str, estado: bool):
        Modifica el estado (móvil/fijo) de un grado de libertad.
    agregar_desplazamiento_inicial(delta: float, gl: str):
        Aplica un desplazamiento conocido (asentamiento) a un grado de libertad.

    Examples:
    -------
    from mnspy import Nodo

    n_1 = Nodo('1', 0, 0, grados_libertad={'x': False, 'y': False})
    n_1.agregar_fuerza_externa(80, 'x')
    """

    def __init__(self, nombre: str, x: float = 0.0, y: float = 0.0, z: float = 0.0,
                 grados_libertad: dict[str, bool] = None, es_rotula: bool = False):
        """Constructor de la clase Nodo

        Parameters
        ----------
        nombre: str
            Nombre o identificador del nodo.
        x: float, optional
            Coordenada x del nodo. Por defecto es 0.0.
        y: float, optional
            Coordenada y del nodo. Por defecto es 0.0.
        z: float, optional
            Coordenada z del nodo. Por defecto es 0.0.
        grados_libertad: dict[str, bool], optional
            Diccionario que define los GDL y su estado (True=móvil, False=fijo).
            Los GDL pueden ser 'x', 'y', 'z', 'eje_x', 'eje_y', 'eje_z'.
        """
        self.nombre = nombre
        self.punto = (x, y, z)

        if grados_libertad is None:
            self.grados_libertad = None
        else:
            # Aunque es un diccionario es necesario ordenarlo
            grados_libertad = {g: grados_libertad[g] for g in ['x', 'y', 'z', 'eje_x', 'eje_y', 'eje_z'] if
                               g in grados_libertad.keys()}
            self.grados_libertad = {n: GradoLibertad(n, v) for n, v in grados_libertad.items()}
        self.es_rotula = es_rotula
        self.fuerzas_externas = dict()
        self._tipo_soporte = []

    def get_soporte(self):
        """Obtiene la información del tipo de soporte asignado al nodo.

        Esta información solo se utiliza para la representación gráfica en el
        diagrama de cargas y no afecta los cálculos del análisis estructural.

        Returns
        -------
        list[int]
            Una lista de dos elementos que define el tipo y estilo del soporte.
        """
        return self._tipo_soporte

    def set_soporte(self, sop: list[int]):
        """Establece el tipo de soporte para el nodo.

        Esta asignación es puramente para fines de visualización en el diagrama
        de cargas y no interviene en los cálculos de la matriz de rigidez ni
        en la resolución del sistema.

        Parameters
        ----------
        sop : list[int]
            Una lista de dos enteros que define el soporte:
            - ``sop[0]``: Tipo de Apoyo
                - 0: Pivotado
                - 1: Empotrado
            - ``sop[1]``: Estilo del Apoyo
                - Si Tipo Apoyo es 0 (Pivotado):
                    - 0: inferior Móvil
                    - 1: inferior Fijo
                    - 2: superior Móvil
                    - 3: superior Fijo
                    - 4: izquierda Móvil
                    - 5: izquierda Fijo
                    - 6: derecha Móvil
                    - 7: derecha Fijo
                - Si Tipo Apoyo es 1 (Empotrado):
                    - 0: fijo izquierdo
                    - 1: fijo derecha
                    - 2: fijo inferior
                    - 3: fijo superior
        """
        self._tipo_soporte = sop

    def agregar_fuerza_externa(self, carga: float, gl: str) -> None:
        """Adiciona una fuerza externa (fuerza o momento) al nodo

        Parameters
        ----------
        carga: float
            corresponde al valor de la fuerza o momento
        gl: str
            corresponde al nombre del grado de libertad

        Returns
        -------
        None
        """
        self.grados_libertad[gl].fuerza += carga
        if gl in self.fuerzas_externas.keys():
            self.fuerzas_externas[gl] += carga
        else:
            self.fuerzas_externas[gl] = carga

    def agregar_desplazamiento_inicial(self, delta: float, gl: str) -> None:
        """Adiciona un desplazamiento inicial al nodo

        Parameters
        ----------
        delta: float
            corresponde al valor del desplazamiento
        gl: str
            corresponde al nombre del grado de libertad

        Returns
        -------
        None
        """
        if self.grados_libertad[gl].desplazamiento is None:
            self.grados_libertad[gl].desplazamiento = 0.0
        self.grados_libertad[gl].desplazamiento += delta
        self.grados_libertad[gl].valor = False  # Deber ser restringido

    def ajustar_grado_libertad(self, gl: str, estado: bool) -> None:
        """Ajusta el estado de grado de libertad del Nodo

        Parameters
        ----------
        gl: str
            Define el grado de libertad, puede ser 'x', 'y', 'z', 'eje_x', 'eje_y', 'eje_z'
        estado: bool
            Establece el estado del GDL. ``True`` para móvil, ``False`` para fijo.

        Returns
        -------
        None
        """
        self.grados_libertad[gl].valor = estado
        self.grados_libertad[gl].reaccion = 0.0 if estado else None
        self.grados_libertad[gl].desplazamiento = None if estado else 0.0

    def __str__(self):
        """Representación del objeto como string.

        Returns
        -------
        str
            El nombre del nodo.
        """
        return 'Nodo: ' + self.nombre

    def _repr_latex_(self):
        texto_latex = r'\begin{array}{l}'
        texto_latex += 'Nombre &: ' + str(self.nombre) + r'\\'
        texto_latex += 'Punto &:' + str(self.punto) + r'\\'
        if self.grados_libertad is not None:
            texto_latex += 'Grados~de~libertad &: ' + r'\begin{cases}'
            for gl in self.grados_libertad:
                texto_latex += gl + '&: '
                texto_latex += r'm\acute {o}vil' if self.grados_libertad[gl].valor else 'fijo'
                texto_latex += r'\\'
            texto_latex += r'\end{cases}\\'
            texto_latex += 'Fuerzas~externas &: ' + r'\begin{cases}'
            for gl in self.grados_libertad:
                texto_latex += gl + '&: ' + str(self.grados_libertad[gl].fuerza) + r'\\'
            texto_latex += r'\end{cases}\\'
            texto_latex += 'Desplazamientos &: ' + r'\begin{cases}'
            for gl in self.grados_libertad:
                if self.grados_libertad[gl].valor:
                    texto_latex += r'\color{blue}' + gl + '&\color{blue}: ' + str(
                        self.grados_libertad[gl].desplazamiento) + r'\\'
                else:
                    texto_latex += gl + '&: ' + str(self.grados_libertad[gl].desplazamiento) + r'\\'
            texto_latex += r'\end{cases}\\'
            texto_latex += 'Reacciones &: ' + r'\begin{cases}'
            for gl in self.grados_libertad:
                if self.grados_libertad[gl].valor:
                    texto_latex += gl + '&: None' + r'\\'
                else:
                    texto_latex += r'\color{blue}' + gl + '&\color{blue}: ' + str(
                        self.grados_libertad[gl].reaccion) + r'\\'
            texto_latex += r'\end{cases}'
        texto_latex += r'\end{array}'
        return '$' + texto_latex + '$'

    def __repr__(self):
        """Representación del objeto como string.

        Returns
        -------
        str
            El nombre del nodo.
        """
        return 'Nodo: ' + self.nombre


class Rigidez:
    """Representa la matriz de rigidez de un elemento o de una estructura ensamblada.

    Esta clase encapsula la matriz de rigidez [k], la lista de nodos que conecta
    y los grados de libertad involucrados. Proporciona métodos para obtener
    vectores y matrices, tanto del sistema completo como del sistema reducido.

    Attributes
    ----------
    grados: list[str]
        Lista de los grados de libertad involucrados
    k: ndarray
        Matriz de rigidez
    lista_nodos: list[Nodo]
        Lista de los nodos involucrados
    """

    def __init__(self, k: np.ndarray, lista_nodos: list[Nodo], grados: list[str] = None):
        """Constructor de la clase Rigidez

        Parameters
        ----------
        k: ndarray
            Matriz de rigidez
        lista_nodos: list[Nodo]
            Lista de los nodos involucrados
        grados: list[str]
            Lista de los grados de libertad involucrados
        """
        self.k = k
        self.lista_nodos = lista_nodos
        self.grados = grados

    def __repr__(self):
        """Representación del objeto en un entorno de notebook.

        Returns
        -------
        str or IPython.display.Math
            Una representación en LaTeX del sistema de ecuaciones o la matriz de rigidez.
        """
        vec_d = np.array(self.obtener_etiquetas_desplazamientos(), dtype=object).reshape(-1, 1)
        vec_r = np.array(self.obtener_etiquetas_reacciones(), dtype=object).reshape(-1, 1)
        if es_notebook():
            texto_latex = r'\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_r,
                                           '{:}') + r'\end{array}\right\}_{Reacciones}=\left[\begin{array}{' + 'c' * \
                           self.k.shape[1] + '}'
            texto_latex += _generar_matrix(self.k,
                                           '{:G}') + r'\end{array}\right]_{Rigidez}\cdot\left\{\begin{array}{c}'
            texto_latex += (_generar_matrix(vec_d, '{:}') +
                            r'\end{array}\right\}_{Desplazamientos}-\left\{\begin{array}{c}')
            texto_latex += _generar_matrix(self.obtener_fuerzas(),
                                           '{:}') + r'\end{array}\right\}_{F_{externas}}'
            display(Math(texto_latex))
            return "Sistema de ecuaciones (en azul las incógnitas)"
        else:
            return np.array2string(self.k, formatter={'float_kind': lambda x: '{:}'.format(x)})

    def __add__(self, otro):
        """Sobrecarga del operador de suma para ensamblar matrices de rigidez.

        Parameters
        ----------
        otro: Rigidez
            El otro objeto tipo Rigidez que se sumará

        Returns
        -------
        Rigidez
            Un nuevo objeto `Rigidez` que es el resultado del ensamble.
        """
        suma = Rigidez(self.k.copy(), self.lista_nodos.copy())
        for item in otro.lista_nodos:
            if item not in self.lista_nodos:
                suma.k = np.insert(np.insert(suma.k, [suma.k.shape[0]] * len(item.grados_libertad), 0.0, axis=0),
                                   [suma.k.shape[1]] * len(item.grados_libertad), 0.0, axis=1)
                # suma.k = np.hstack((suma.k, np.zeros((suma.k.shape[0], len(item.grados_libertad)))))
                # suma.k = np.vstack((suma.k, np.zeros((len(item.grados_libertad), suma.k.shape[1]))))
                suma.lista_nodos.append(item)
        i_otro = 0
        for item_i in otro.lista_nodos:
            i = 0
            for indice in range(suma.lista_nodos.index(item_i)):
                i += len(suma.lista_nodos[indice].grados_libertad)
            j_otro = 0
            for item_j in otro.lista_nodos:
                j = 0
                for indice in range(suma.lista_nodos.index(item_j)):
                    j += len(suma.lista_nodos[indice].grados_libertad)
                for k_i in otro.grados:
                    for k_j in otro.grados:
                        # suma.k[i + list(item_i.grados_libertad.keys()).index(k_i), j + list(
                        #     item_j.grados_libertad.keys()).index(k_j)] += otro.k[
                        #     i_otro + list(item_i.grados_libertad.keys()).index(k_i), j_otro + list(
                        #         item_j.grados_libertad.keys()).index(k_j)]
                        suma.k[i + list(item_i.grados_libertad.keys()).index(k_i), j + list(
                            item_j.grados_libertad.keys()).index(k_j)] += otro.k[
                            i_otro + otro.grados.index(k_i), j_otro + otro.grados.index(k_j)]
                j_otro += len(otro.grados)
            i_otro += len(otro.grados)
        return suma

    def mostrar_sistema(self, reducida: bool = False):
        """Muestra el sistema de ecuaciones generado en forma matricial

        Parameters
        ----------
        reducida: bool
            Si es True muestra el sistema de ecuaciones generado que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False muestra todo el sistema de ecuaciones generado

        Returns
        -------
        Información del sistema de ecuaciones generado en latex para iPython
        """
        vec_d = np.array(self.obtener_etiquetas_desplazamientos(reducida), dtype=object).reshape(-1, 1)
        vec_r = np.array(self.obtener_etiquetas_reacciones(reducida), dtype=object).reshape(-1, 1)
        if es_notebook():
            texto_latex = r'\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_r,
                                           '{:}') + r'\end{array}\right\}=\left[\begin{array}{' + 'c' * \
                           self.obtener_matriz(reducida).shape[1] + '}'
            texto_latex += _generar_matrix(self.obtener_matriz(reducida),
                                           '{:G}') + r'\end{array}\right]\cdot\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}-\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(self.obtener_fuerzas(reducida),
                                           '{:}') + r'\end{array}\right\}'
            display(Math(texto_latex))
        else:
            return np.array2string(self.obtener_matriz(reducida), formatter={'float_kind': lambda x: '{:}'.format(x)})

    def obtener_sistema_reducido(self) -> tuple[np.ndarray, np.ndarray, list[str]]:
        """Obtiene la matriz [A], el vector {b} y las etiquetas para el sistema
        reducido.

        El sistema reducido solo incluye los grados de libertad que son móviles
        (incógnitas).

        Returns
        -------
        tuple[np.ndarray, np.ndarray, list[str]]
            - Matriz de rigidez reducida [A].
            - Vector de fuerzas reducido {b}.
            - Lista de etiquetas para las incógnitas de desplazamiento.
        """
        return self.obtener_matriz(True), self.obtener_fuerzas(True), self.obtener_etiquetas_desplazamientos(True)

    def calcular_reacciones(self, sol_desplazamientos: np.ndarray):
        """Calcula las fuerzas de reacción en los nodos restringidos.

        Parameters
        ----------
        sol_desplazamientos: matrix | ndarray
            Vector columna con el resultado de los desplazamientos
        Returns
        -------
        None
        """
        indice = 0
        for item in self.lista_nodos:
            for gl in item.grados_libertad.values():
                if gl.valor:
                    gl.desplazamiento = sol_desplazamientos[indice, 0]
                    indice += 1
        reacciones = np.matmul(self.obtener_matriz(), self.obtener_desplazamientos()) - self.obtener_fuerzas()
        indice = 0
        for item in self.lista_nodos:
            for gl in item.grados_libertad.values():
                if not gl.valor:
                    gl.reaccion = reacciones[indice, 0]
                indice += 1

    def obtener_matriz(self, reducida: bool = False) -> np.ndarray:
        """Obtiene la matriz de rigidez

        Parameters
        ----------
        reducida: bool
            Si es True retorna la matriz de rigidez que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False retorna toda la matriz de rigidez

        Returns
        -------
        np.ndarray
            La matriz de rigidez solicitada.
        """
        if reducida:
            lista_eliminar = []
            i = 0
            for item in self.lista_nodos:
                if self.grados is None:
                    k = len(item.grados_libertad)
                else:
                    k = len(self.grados)
                for i_gl, gl in enumerate(item.grados_libertad.values()):
                    if not gl.valor:
                        lista_eliminar.append(i + i_gl)
                i += k
            mat_global = np.delete(self.k, lista_eliminar, 0)
            mat_global = np.delete(mat_global, lista_eliminar, 1)
            return mat_global
        else:
            return self.k

    def obtener_fuerzas(self, reducida: bool = False) -> np.ndarray:
        """Obtiene el vector columna de fuerzas

        Parameters
        ----------
        reducida: bool
            Si es True retorna el vector columna de fuerzas que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False retorna todo el vector columna de fuerzas

        Returns
        -------
        np.ndarray
            El vector columna de fuerzas.
        """
        fuerza = None
        for item in self.lista_nodos:
            f_i = np.array([[fu.fuerza for fu in item.grados_libertad.values()]]).transpose()
            if fuerza is None:
                fuerza = f_i
            else:
                fuerza = np.vstack((fuerza, f_i))
        if reducida:
            lista_eliminar = []
            i = 0
            for item in self.lista_nodos:
                for i_gl, gl in enumerate(item.grados_libertad.values()):
                    if not gl.valor:
                        lista_eliminar.append(i + i_gl)
                i += len(item.grados_libertad)
            fuerza = np.delete(fuerza, lista_eliminar, 0)
            return fuerza - self.obtener_fuerzas_iniciales_reducidas()  # Se le resta las fuerzas iníciales si hay desplazamiento
        else:
            return fuerza

    def obtener_fuerzas_iniciales_reducidas(self) -> np.ndarray:
        """Obtiene el vector de fuerzas nodales equivalentes debido a desplazamientos iniciales.

        Returns
        -------
        np.ndarray
            Vector columna de fuerzas iniciales para el sistema reducido.
        """
        desplazamiento = None
        for item in self.lista_nodos:
            d_i = np.array(
                [[d.desplazamiento if d.desplazamiento is not None else 0.0 for d in
                  item.grados_libertad.values()]]).transpose()
            if desplazamiento is None:
                desplazamiento = d_i
            else:
                desplazamiento = np.vstack((desplazamiento, d_i))
        d_inicial = np.matmul(self.obtener_matriz(), desplazamiento)
        lista_eliminar = []
        i = 0
        for item in self.lista_nodos:
            for i_gl, gl in enumerate(item.grados_libertad.values()):
                if not gl.valor:
                    lista_eliminar.append(i + i_gl)
            i += len(item.grados_libertad)
        d_inicial = np.delete(d_inicial, lista_eliminar, 0)
        return d_inicial

    def obtener_desplazamientos(self) -> np.ndarray:
        """Obtiene el vector columna de desplazamientos

        Returns
        -------
        np.ndarray
            El vector columna de desplazamientos.
        """
        desplazamiento = None
        for item in self.lista_nodos:
            d_i = [d.desplazamiento for d in item.grados_libertad.values()]
            if desplazamiento is None:
                desplazamiento = d_i
            else:
                desplazamiento = np.hstack((desplazamiento, d_i))
        return np.array(desplazamiento).reshape(-1, 1)

    def obtener_etiquetas_desplazamientos(self, reducida: bool = False) -> list[str]:
        """Obtiene la lista de etiquetas de los desplazamientos

        Parameters
        ----------
        reducida: bool
            Si es True retorna la lista de etiquetas de los desplazamientos que involucre solamente incognitas
            de desplazamiento, en caso contrario si es False retorna toda la lista de etiquetas de los desplazamientos

        Returns
        -------
        list[str]
            Lista de etiquetas para los desplazamientos.
        """
        etiquetas = []
        for item in self.lista_nodos:
            for n, gl in item.grados_libertad.items():
                if reducida and not gl.valor:
                    continue
                if self.grados is not None:
                    if n not in self.grados:
                        continue

                dato = gl.label_desplazamiento + '_{' + item.nombre + '}'
                # dato = dato if gl.desplazamiento is None else dato + '=' + str(gl.desplazamiento)
                dato = dato if gl.desplazamiento is None else dato + '=' + _formato_float_latex(gl.desplazamiento,
                                                                                                TOL_CERO, FORMATO_NUM)
                if gl.valor and es_notebook():
                    etiquetas.append(r'\color{blue}' + dato)
                else:
                    etiquetas.append(dato)
        return etiquetas

    def obtener_etiquetas_fuerzas(self, reducida: bool = False) -> list[str]:
        """Obtiene la lista de etiquetas de las fuerzas

        Parameters
        ----------
        reducida: bool
            Si es True retorna la lista de etiquetas de las fuerzas que involucre solamente incognitas
            de desplazamiento, en caso contrario si es False retorna toda la lista de etiquetas de las fuerzas

        Returns
        -------
        list[str]
            Lista de etiquetas para las fuerzas.
        """
        etiquetas = []
        for item in self.lista_nodos:
            for n, gl in item.grados_libertad.items():
                if self.grados is not None:
                    if n not in self.grados or (reducida and not gl.valor):
                        continue
                # etiquetas.append(gl.label_fuerzas + '_{' + item.nombre + '}')
                etiquetas.append(gl.label_fuerza)
        return etiquetas

    def obtener_etiquetas_reacciones(self, reducida: bool = False) -> list[str]:
        """Obtiene la lista de etiquetas de las reacciones

        Parameters
        ----------
        reducida: bool
            Si es True retorna la lista de etiquetas de las reacciones que involucre solamente incognitas
            de desplazamiento, en caso contrario si es False retorna toda la lista de etiquetas de las reacciones

        Returns
        -------
        list[str]
            Lista de etiquetas para las reacciones.
        """
        etiquetas = []
        for item in self.lista_nodos:
            for n, gl in item.grados_libertad.items():
                if reducida and not gl.valor:
                    continue
                if self.grados is not None:
                    if n not in self.grados:
                        continue
                sub = gl.gl if 'eje' not in gl.gl else ''
                dato = gl.label_reaccion + '_{' + item.nombre + sub + '}'
                # dato = dato if gl.valor is None else dato + '=' + str(gl.valor)
                if gl.valor:
                    etiquetas.append(r'\cancel{' + dato + '}')
                else:
                    # dato = dato if gl.reaccion is None else dato + '=' + str(gl.reaccion)
                    dato = dato if gl.reaccion is None else dato + '=' + _formato_float_latex(gl.reaccion, TOL_CERO,
                                                                                              FORMATO_NUM)
                    etiquetas.append(r'\color{blue}' + dato)
        return etiquetas


class Elemento:
    """Clase base para todos los tipos de elementos finitos.

    Define la interfaz común para los elementos, incluyendo el ensamblaje,
    la obtención de la matriz de rigidez y la visualización del sistema.

    Attributes
    ----------
    _L: float
        Longitud del elemento (elemento lineal)
    _fuerzas_i: ndarray
        vector columna de las fuerzas en el nodo i
    _fuerzas_j: ndarray
        vector columna de las fuerzas en el nodo j
    _fuerzas_m: ndarray
        vector columna de las fuerzas en el nodo m
    _k: Rigidez
        Objeto relacionado con la matriz de rigidez
    _nodo_i: Nodo
        Nodo inicial del elemento (elemento lineal)
    _nodo_j: Nodo
        Nodo final del elemento (elemento lineal)
    _nodo_m: Nodo
        Tercer nodo(elemento Triangular)
    nombre: str
            Nombre asignado al Elemento
    """

    def __init__(self, nombre: str, nodo_i: Nodo = None, nodo_j: Nodo = None, nodo_m: Nodo = None):
        """Constructor de la clase Elemento

        Parameters
        ----------
        nombre: str
            Nombre asignado al Elemento
        nodo_i: Nodo
            Nodo inicial del elemento (elemento lineal)
        nodo_j: Nodo
            Nodo final del elemento (elemento lineal)
        nodo_m: Nodo
            Tercer nodo(elemento Triangular)
        """
        self.nombre = nombre
        self._k = None
        self._fuerzas_i = None
        self._fuerzas_j = None
        # Si hay una rótula
        self._fuerzas_i_rot = None
        self._fuerzas_j_rot = None

        self._fuerzas_m = None
        self._nodo_i = nodo_i
        self._nodo_j = nodo_j
        self._nodo_m = nodo_m
        if self._nodo_i is None or self._nodo_j is None:
            self._L = None
        else:
            self._L = longitud(nodo_i.punto, nodo_j.punto)
        self._lista_elementos = None
        self._c = None
        self._s = None
        # self._tol_cero_etiquetas = 1E-10

    def _repr_latex_(self):
        vec_d = np.array(self.obtener_rigidez().obtener_etiquetas_desplazamientos(),
                         dtype=object).reshape(-1, 1)
        vec_r = np.array(self.obtener_rigidez().obtener_etiquetas_reacciones(), dtype=object).reshape(-1, 1)
        texto_latex = r'\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_r, '{:}') + r'\end{array}\right\}_{\{R\}}+\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(self.obtener_rigidez().obtener_fuerzas(),
                                       '{:}') + r'\end{array}\right\}_{\{F_{ext.}\}}=\left[\begin{array}{' + 'c' * \
                       self.obtener_rigidez().obtener_matriz().shape[1] + '}'
        texto_latex += _generar_matrix(self.obtener_rigidez().obtener_matriz(),
                                       '{:G}') + r'\end{array}\right]_{[K]}\cdot\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}_{\{d\}}'
        return '$' + texto_latex + '$'

    def __repr__(self):
        """Representación del objeto como string.

        Returns
        -------
        str
            El nombre del elemento.
        """
        return 'Elemento: ' + self.nombre

    def __str__(self):
        """Representación del objeto como string.

        Returns
        -------
        str
            El nombre del elemento.
        """
        return 'Elemento: ' + self.nombre

    def __add__(self, otro):
        """Sobrecarga del operador de suma para ensamblar elementos.

        Parameters
        ----------
        otro : Elemento
            El otro objeto tipo Elemento que se sumará

        Returns
        -------
            Objeto tipo Elemento resultante de la suma
        """
        suma = Elemento(self.nombre + '+' + otro.nombre)
        if self._lista_elementos is None:
            lista_1 = [self]
            temp_k = Rigidez(self._k.k.copy(), self._k.lista_nodos, self._k.grados)
            j = 0
            for nodo in self.get_lista_nodos():
                if len(self._k.grados) < len(nodo.grados_libertad.keys()):
                    for i, item in enumerate(nodo.grados_libertad.keys()):
                        if item not in self._k.grados:
                            temp_k.k = np.insert(np.insert(temp_k.k, j + i, 0.0, axis=0), j + i, 0.0, axis=1)
                j += len(nodo.grados_libertad.keys())
            suma._k = temp_k + otro._k
        else:
            lista_1 = self._lista_elementos
            suma._k = self._k + otro._k
        if otro._lista_elementos is None:
            lista_2 = [otro]
        else:
            lista_2 = otro._lista_elementos
        suma._lista_elementos = lista_1 + lista_2
        return suma

    # def obtener_ecuacion_cortante(self):
    #     x = sp.symbols('x')
    #     V = sp.Function('V')(x)
    #     if self._lista_elementos is not None:
    #         arg = []
    #         for elemento in self._lista_elementos:
    #             arg += list(elemento.obtener_ecuacion_cortante().args[1].args)
    #         return sp.Eq(V, sp.Piecewise(*arg))
    #
    # def obtener_ecuacion_momento(self):
    #     x = sp.symbols('x')
    #     M = sp.Function('M')(x)
    #     if self._lista_elementos is not None:
    #         arg = []
    #         for elemento in self._lista_elementos:
    #             arg += list(elemento.obtener_ecuacion_momento().args[1].args)
    #         return sp.Eq(M, sp.Piecewise(*arg))
    #
    # def obtener_ecuacion_angulo(self):
    #     x = sp.symbols('x')
    #     phi = sp.Function('phi')(x)
    #     if self._lista_elementos is not None:
    #         arg = []
    #         for elemento in self._lista_elementos:
    #             arg += list(elemento.obtener_ecuacion_angulo().args[1].args)
    #         return sp.Eq(phi, sp.Piecewise(*arg))
    #
    # def obtener_ecuacion_deflexion(self):
    #     x = sp.symbols('x')
    #     y = sp.Function('y')(x)
    #     if self._lista_elementos is not None:
    #         arg = []
    #         for elemento in self._lista_elementos:
    #             arg += list(elemento.obtener_ecuacion_deflexion().args[1].args)
    #         return sp.Eq(y, sp.Piecewise(*arg))

    # def diagrama_de_cortante(self):
    #     if self._lista_elementos is not None:
    #         for elemento in self._lista_elementos:
    #             l_x, l_y, l_z = elemento.obtener_arrays_cortantes()
    #             plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.9)
    #             for i in l_z:
    #                 pos_y = 5  # offset escritura
    #                 val_x, val_y = i
    #                 if val_y < 0:
    #                     pos_y = -5
    #                 plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
    #                              textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
    #         plt.grid()
    #         plt.title('Diagrama de cortantes')
    #         plt.xlabel('$x$')
    #         plt.ylabel('$V$')
    #         plt.show()
    #
    # def diagrama_de_momento(self):
    #     if self._lista_elementos is not None:
    #         for elemento in self._lista_elementos:
    #             l_x, l_y, l_z = elemento.obtener_arrays_momentos()
    #             plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.9)
    #             for i in l_z:
    #                 pos_y = 5  # offset escritura
    #                 val_x, val_y = i
    #                 if val_y < 0:
    #                     pos_y = -5
    #                 plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
    #                              textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
    #         plt.grid()
    #         plt.title('Diagrama de momentos')
    #         plt.xlabel('$x$')
    #         plt.ylabel('$M$')
    #         plt.show()
    #
    # def diagrama_de_giro(self):
    #     if self._lista_elementos is not None:
    #         for elemento in self._lista_elementos:
    #             l_x, l_y, l_z = elemento.obtener_arrays_angulos()
    #             plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.9)
    #             for i in l_z:
    #                 pos_y = 5  # offset escritura
    #                 val_x, val_y = i
    #                 if val_y < 0:
    #                     pos_y = -5
    #                 plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
    #                              textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
    #         plt.grid()
    #         plt.title('Diagrama de giros')
    #         plt.xlabel('$x$')
    #         plt.ylabel(r'$\phi$')
    #         plt.show()
    #
    # def diagrama_de_deflexion(self):
    #     if self._lista_elementos is not None:
    #         for elemento in self._lista_elementos:
    #             l_x, l_y, l_z = elemento.obtener_arrays_deflexion()
    #             plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.9)
    #             for i in l_z:
    #                 pos_y = 5  # offset escritura
    #                 val_x, val_y = i
    #                 if val_y < 0:
    #                     pos_y = -5
    #                 plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
    #                              textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
    #         plt.grid()
    #         plt.title('Diagrama de deflexión')
    #         plt.xlabel('$x$')
    #         plt.ylabel('$y$')
    #         plt.show()

    def get_lista_nodos(self):
        return self._k.lista_nodos

    def get_nodo_inicial(self) -> Nodo:
        return self._nodo_i

    def get_nodo_final(self) -> Nodo:
        return self._nodo_j

    def get_nodo_medio(self) -> Nodo:
        return self._nodo_m

    def get_seno(self) -> float:
        return self._s

    def get_coseno(self) -> float:
        return self._c

    def get_longitud(self) -> float:
        return self._L

    def get_matriz_rigidez(self):
        return self._k.obtener_matriz()

    def get_matriz_rigidez_local(self):
        return self.get_matriz_rigidez()

    def get_matriz_T(self):
        return np.eye(self.get_matriz_rigidez().shape[0])

    def obtener_rigidez(self) -> Rigidez:
        return self._k

    # def obtener_sistema_reducido(self) -> tuple[np.ndarray, np.ndarray, list[str]]:
    #     """Obtiene las matrices y etiquetas del sistema de ecuaciones reducido
    #
    #     Returns
    #     -------
    #     Retorna una Tuple con la matriz de Rigidez reducida (A), el vector columna (b) y  una lista de las
    #     etiquetas de las variables.
    #     """
    #     return self._k.obtener_sistema_reducido()

    def _obtener_fuerzas(self, reducida: bool = False) -> np.ndarray:
        """Obtiene el vector columna de fuerzas

        Parameters
        ----------
        reducida: bool
            Si es True retorna el vector columna de fuerzas que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False retorna todo el vector columna de fuerzas

        Returns
        -------
        Retorna el vector columna de fuerzas.
        """
        if self._nodo_i is None or self._nodo_j is None:
            self._k.obtener_fuerzas(reducida)
        fuerza = np.vstack((self._fuerzas_i, self._fuerzas_j))
        if reducida:
            lista_eliminar = []
            i = 0
            for item in [self._nodo_i, self._nodo_j]:
                for j, gl in enumerate(self._k.grados):
                    if not item.grados_libertad[gl].valor:
                        lista_eliminar.append(i + j)
                i += len(self._k.grados)
            fuerza = np.delete(fuerza, lista_eliminar, 0)
            return fuerza
        else:
            return fuerza

    def _obtener_fuerzas_por_rotula(self, reducida: bool = False) -> np.ndarray:
        """Obtiene el vector columna de fuerzas debido a la rotula

        Parameters
        ----------
        reducida: bool
            Si es True retorna el vector columna de fuerzas que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False retorna todo el vector columna de fuerzas

        Returns
        -------
        Retorna el vector columna de fuerzas.
        """
        fuerza = np.vstack((self._fuerzas_i_rot, self._fuerzas_j_rot))
        if reducida:
            lista_eliminar = []
            i = 0
            for item in [self._nodo_i, self._nodo_j]:
                for j, gl in enumerate(self._k.grados):
                    if not item.grados_libertad[gl].valor:
                        lista_eliminar.append(i + j)
                i += len(self._k.grados)
            fuerza = np.delete(fuerza, lista_eliminar, 0)
            return fuerza
        else:
            return fuerza

    def mostrar_sistema(self, reducida: bool = False):
        """Muestra el sistema de ecuaciones generado en forma matricial

        Parameters
        ----------
        reducida: bool
            Si es True muestra el sistema de ecuaciones generado que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False muestra todo el sistema de ecuaciones generado

        Returns
        -------
        Información del sistema de ecuaciones generado en latex para iPython
        """
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(reducida), dtype=object).reshape(-1, 1)
        vec_r = np.array(self._k.obtener_etiquetas_reacciones(reducida), dtype=object).reshape(-1, 1)
        if es_notebook():
            texto_latex = r'\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_r, '{:}') + r'\end{array}\right\}_{\{R\}}+\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(self._k.obtener_fuerzas(reducida),
                                           '{:}') + r'\end{array}\right\}_{\{F_{ext.}\}}=\left[\begin{array}{' + 'c' * \
                           self._k.obtener_matriz(reducida).shape[1] + '}'
            texto_latex += _generar_matrix(self._k.obtener_matriz(reducida),
                                           '{:G}') + r'\end{array}\right]_{[K]}\cdot\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}_{\{d\}}'
            display(Math(texto_latex))
        else:
            return np.array2string(self._k.obtener_matriz(reducida),
                                   formatter={'float_kind': lambda x: '{:}'.format(x)})

    def mostrar_matriz_rigidez(self, reducida: bool = False):
        """Obtiene la matriz de rigidez

        Parameters
        ----------
        reducida: bool
            Si es True retorna la matriz de rigidez que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False retorna toda la matriz de rigidez

        Returns
        -------
        IPython.display.Math or str
            Una representación en LaTeX de la matriz o la matriz impresa en consola.
        """
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(reducida), dtype=object).reshape(-1, 1)
        if es_notebook():
            texto_latex = r'\left[\begin{array}{' + 'c' * self._k.obtener_matriz(reducida).shape[1] + '}'
            texto_latex += _generar_matrix(self._k.obtener_matriz(reducida),
                                           '{:G}') + r'\end{array}\right]\cdot\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}'
            display(Math(texto_latex))
        else:
            return np.array2string(self._k.obtener_matriz(reducida),
                                   formatter={'float_kind': lambda x: '{:}'.format(x)})

    def _obtener_cargas(self) -> dict:
        return {}

    def _obtener_arrays_cortantes(self, n_puntos):
        return [], [], []

    def _obtener_arrays_momentos(self, n_puntos):
        return [], [], []

    def _obtener_arrays_angulos(self, n_puntos):
        return [], [], []

    def _obtener_arrays_deflexion(self, n_puntos):
        return [], [], []


def main():
    from resorte import Resorte
    from viga import Viga
    n_1 = Nodo('1', 0, grados_libertad={'y': False, 'eje_z': False})
    n_2 = Nodo('2', 3, grados_libertad={'y': False, 'eje_z': True})
    n_3 = Nodo('3', 6, grados_libertad={'y': True, 'eje_z': True})
    n_4 = Nodo('4', 6, grados_libertad={'y': True})
    # n_3.fuerza=array([[-50],[0]])
    el_1 = Viga('1', n_1, n_2, 210E6, 2E-4)
    el_2 = Viga('2', n_2, n_3, 210E6, 2E-4)
    r_1 = Resorte('3', n_3, n_4, 200, 'y')

    sol = el_1 + el_2 + r_1
    print(sol.mostrar_matriz_rigidez())

    n_1 = Nodo('1', 0, grados_libertad={'y': False, 'eje_z': False})
    n_2 = Nodo('2', 3, grados_libertad={'y': True, 'eje_z': True})
    n_3 = Nodo('3', 6, grados_libertad={'y': False, 'eje_z': True})
    n_4 = Nodo('4', 9, grados_libertad={'y': True, 'eje_z': True})
    n_5 = Nodo('5', 12, grados_libertad={'y': False, 'eje_z': False})

    e_1 = Viga('1', n_1, n_2, E=210E6, I=2E-4)
    e_2 = Viga('2', n_2, n_3, E=210E6, I=2E-4)
    e_3 = Viga('3', n_3, n_4, E=210E6, I=2E-4)
    e_4 = Viga('4', n_4, n_5, E=210E6, I=2E-4)

    n_2.agregar_fuerza_externa(-50, 'y')
    n_4.agregar_fuerza_externa(-50, 'y')

    mg = e_1 + e_2 + e_3 + e_4
    print(mg.mostrar_matriz_rigidez())


if __name__ == '__main__':
    main()
