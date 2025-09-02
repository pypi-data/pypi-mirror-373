from mnspy.utilidades import es_notebook, _generar_matrix, _formato_float_latex
import numpy as np
from IPython.display import display, Math
import sympy as sp
from enum import Enum
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib import tri

TOL_CERO = 1E-10
FORMATO_NUM = '{:.10g}'
sp.init_printing(use_latex=True)


class Metodo(Enum):
    """Define los esquemas de discretización para los términos de convección.

    - **CDS (Central Differencing Scheme)**: Esquema centrado, de segundo orden
      pero puede generar oscilaciones no físicas con altos números de Péclet.
    - **UDS (Upwind Differencing Scheme)**: Esquema de diferencias contra el
      viento, de primer orden, muy estable pero introduce difusión numérica.
    - **HDS (Hybrid Differencing Scheme)**: Esquema híbrido que combina CDS y
      UDS, utilizando UDS cuando la convección es dominante (Pe > 2).
    """
    CDS = 1  # Central Differencing Scheme
    UDS = 2  # Upwind Differencing Scheme
    HDS = 3  # Hybrid Differencing Scheme


#
# class Escalar:
#     def __init__(self, variable: str, valor: float = 0.0):
#         self.variable = variable
#         self.valor = valor


class Vertice:
    """Representa un vértice (o nodo) en una malla de volúmenes finitos.

    Un vértice tiene coordenadas espaciales (x, y, z) y puede almacenar
    propiedades escalares (ej. temperatura) y vectoriales (ej. velocidad).
    """
    def __init__(self, nombre: str, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        """Constructor de la clase Vertice.

        Parameters
        ----------
        nombre : str
            Identificador único para el vértice.
        x : float, optional
            Coordenada x del vértice. Por defecto es 0.0.
        y : float, optional
            Coordenada y del vértice. Por defecto es 0.0.
        z : float, optional
            Coordenada z del vértice. Por defecto es 0.0.
        """
        self.nombre = nombre
        self.x = x
        self.y = y
        self.z = z
        self.campos = None
        self.escalares = None
        self.lista_superficies = list()

    def get_punto(self) -> tuple[float, float, float]:
        """Retorna las coordenadas del vértice como una tupla."""
        return self.x, self.y, self.z

    def set_punto(self, punto: tuple[float, float, float]):
        """Establece las coordenadas del vértice."""
        self.x, self.y, self.z = punto

    def get_distancia(self, p: tuple[float, float, float]) -> float:
        """Calcula la distancia euclidiana a otro punto."""
        return float(np.sqrt((self.x - p[0]) ** 2 + (self.y - p[1]) ** 2 + (self.z - p[2]) ** 2))

    def set_escalar(self, var: dict):
        """Agrega o actualiza un valor escalar asociado al vértice.

        Parameters
        ----------
        var : dict
            Diccionario con el nombre de la variable y su valor.
            Ejemplo: `{'T': 300.0}`.
        """
        if self.escalares is None:
            self.escalares = var
        else:
            self.escalares.update(var)

    def get_escalar(self) -> dict['str': float | list | np.ndarray]:
        """Retorna el diccionario de escalares del vértice."""
        return self.escalares

    def set_campo(self, var: dict[str, list | np.ndarray]):
        """Agrega o actualiza un campo vectorial asociado al vértice.

        Parameters
        ----------
        var : dict[str, list | np.ndarray]
            Diccionario con el nombre del campo y su valor vectorial.
            Ejemplo: `{'velocidad': [1.0, 0.5, 0.0]}`.
        """
        if self.campos is None:
            self.campos = var
        else:
            self.campos.update(var)

    def get_campo(self) -> dict[str, list | np.ndarray]:
        """Retorna el diccionario de campos vectoriales del vértice."""
        return self.campos


class Superficie:
    """Representa una superficie (o cara) que delimita un volumen de control (Celda).

    Una superficie está definida por una lista de vértices y tiene propiedades
    geométricas como área y vector normal. Actúa como interfaz entre dos
    celdas vecinas (o una celda y una frontera del dominio).

    Attributes
    ----------
    nombre : str
        Identificador único para la superficie.
    lista_vertices : list[int]
        Lista de índices de los vértices que definen la superficie.
    t : float
        Espesor (para superficies 2D representadas como líneas).
    u : tuple[float, float, float]
        Vector de velocidad en la superficie, utilizado en problemas de convección.
    A : float
        Área de la superficie.
    centroide : Vertice
        Objeto `Vertice` que representa el centroide de la superficie.
    normal : np.ndarray
        Vector normal unitario a la superficie.
    """
    def __init__(self, nombre: str, vertices: list[int], t: float = 1.0,
                 u: tuple[float, float, float] = (0.0, 0.0, 0.0)):
        """Constructor de la clase Superficie.

        Parameters
        ----------
        nombre : str
            Identificador único para la superficie.
        vertices : list[int]
            Lista de índices de los vértices que la componen.
        t : float, optional
            Espesor, para cálculos de área en 2D. Por defecto es 1.0.
        u : tuple[float, float, float], optional
            Vector de velocidad en la cara. Por defecto es (0,0,0).
        """
        self.nombre = nombre
        self.lista_vertices = vertices
        self.vertices = None
        self.t = t
        self.A = None
        self.u = u
        self._vecinos = [None, None]
        self.centroide = Vertice(nombre)
        self.normal = None

    def set_vertices(self, vertices: list[Vertice]):
        """Asigna los objetos `Vertice` a la superficie."""
        self.vertices = vertices

    def set_centroide(self, centroide: tuple[float, float, float]):
        """Establece las coordenadas del centroide de la superficie."""
        self.centroide.set_punto(centroide)

    def set_normal(self, normal: np.ndarray):
        """Establece el vector normal de la superficie."""
        self.normal = normal

    def get_vecinos(self) -> list:
        """Retorna la lista de celdas vecinas a esta superficie."""
        return self._vecinos

    def get_vecino(self, vecino: any):
        """Obtiene la celda vecina opuesta a la celda dada.

        Parameters
        ----------
        vecino : Celda
            La celda de referencia.

        Returns
        -------
        Celda or None
            La celda vecina, o `None` si es una frontera.
        """
        if vecino in self.get_vecinos():
            for c in self.get_vecinos():
                if c != vecino:
                    return c
        else:
            return None

    def set_vecino(self, vecino: any):
        """Asigna una celda como vecina a esta superficie.

        Una superficie puede tener como máximo dos celdas vecinas.
        """
        if self._vecinos[0] is None:
            self._vecinos[0] = vecino
        elif self._vecinos[1] is None:
            self._vecinos[1] = vecino
        else:
            raise IndexError("Una superficie no puede tener más de dos celdas vecinas.")


class SuperficieDirichlet(Superficie):
    """Representa una condición de frontera de tipo Dirichlet (valor fijo).

    Hereda de `Superficie` y añade un atributo para almacenar el valor
    fijo de la variable en la frontera (ej. temperatura fija).
    """
    def __init__(self, nombre: str, vertices: list[int], var: dict[str:float] = None, t: float = 1.0,
                 u: tuple[float, float, float] = (0.0, 0.0, 0.0)):
        """Constructor para una superficie de frontera Dirichlet.

        Parameters
        ----------
        var : dict[str:float], optional
            Diccionario que contiene el nombre de la variable y su valor fijo.
            Ejemplo: `{'T': 300.0}`. Por defecto es `{'T': 0.0}`.
        """
        super().__init__(nombre, vertices, t, u)
        if var is None:
            self.var = {'T': 0.0}
        else:
            self.var = var


class SuperficieNeumann(Superficie):
    """Representa una condición de frontera de tipo Neumann (flujo fijo).

    Hereda de `Superficie` y añade un atributo para especificar el flujo
    (gradiente de la variable) a través de la frontera. Un flujo de cero
    representa una frontera aislada o de simetría.
    """
    def __init__(self, nombre: str, vertices: list[int], flujo: float = 0.0, t: float = 1.0,
                 u: tuple[float, float, float] = (0.0, 0.0, 0.0)):
        """Constructor para una superficie de frontera Neumann.

        Parameters
        ----------
        flujo : float, optional
            Valor del flujo a través de la superficie. Por defecto es 0.0 (aislada).
        """
        super().__init__(nombre, vertices, t, u)
        self.flujo = flujo


class SuperficieRobin(Superficie):
    """Representa una condición de frontera de tipo Robin (mixta).

    Hereda de `Superficie` y modela una condición que depende tanto del valor
    de la variable en la frontera como de su flujo, comúnmente usada para
    representar transferencia de calor por convección.
    """
    def __init__(self, nombre: str, vertices: list[int], h: float = 0.0, T_inf: float = 0.0, t: float = 1.0,
                 u: tuple[float, float, float] = (0.0, 0.0, 0.0)):
        """Constructor para una superficie de frontera Robin.

        Parameters
        ----------
        h : float, optional
            Coeficiente de transferencia (ej. coeficiente de convección).
        T_inf : float, optional
            Valor de referencia del ambiente (ej. temperatura del fluido circundante).
        """
        super().__init__(nombre, vertices, t, u)
        self.h = h
        self.T_inf = T_inf


def es_superficie_dirichlet(sup: Superficie) -> bool:
    """Método estático para identificar si es una superficie Dirichlet

    Parameters
    ----------
    sup: Superficie
        Objeto de tipo Superficie

    Returns
    -------
    True: Si la superficie es de tipo Dirichlet
    False: Si la superficie no es de tipo Dirichlet
    """
    return type(sup).__name__ == 'SuperficieDirichlet'


def es_superficie_neumann(sup: Superficie) -> bool:
    """Método estático para identificar si es una superficie Neumann

    Parameters
    ----------
    sup: Superficie
        Objeto de tipo Superficie

    Returns
    -------
    True: Si la superficie es de tipo Neumann
    False: Si la superficie no es de tipo Neumann
    """
    return type(sup).__name__ == 'SuperficieNeumann'


def es_superficie_robin(sup: Superficie) -> bool:
    """Método estático para identificar si es una superficie Robin

    Parameters
    ----------
    sup: Superficie
        Objeto de tipo Superficie

    Returns
    -------
    True: Si la superficie es de tipo Robin
    False: Si la superficie no es de tipo Robin
    """
    return type(sup).__name__ == 'SuperficieRobin'


class Celda:
    """Representa un volumen de control o celda, la unidad fundamental en el MVF.

    La ecuación de conservación se aplica a esta celda, resultando en una
    ecuación algebraica que relaciona el valor de la variable en el centroide
    de la celda con los valores en las celdas vecinas.

    Attributes
    ----------
    nombre : str
        Identificador único para la celda.
    gamma : float
        Coeficiente de difusión (ej. conductividad térmica).
    q : float
        Término fuente volumétrico.
    phi_p : float
        Coeficiente central (a_P) en la ecuación discretizada.
    s_u : float
        Componente constante del término fuente linealizado (S_u).

    """
    def __init__(self, nombre: str, superficies: list[int], gamma: float = 1.0, q: float = 0.0, h: float = 0.0,
                 p: float = 1.0, T_inf: float = 0.0, densidad: float = 1.0):
        """Constructor de la clase Celda.

        Parameters
        ----------
        nombre : str
            Identificador único de la celda.
        superficies : list[int]
            Lista de índices de las superficies que componen la celda.
        gamma : float, optional
            Coeficiente de difusión. Por defecto es 1.0.
        q : float, optional
            Término fuente volumétrico. Por defecto es 0.0.
        h : float, optional
            Coeficiente de transferencia (para fuentes lineales). Por defecto es 0.0.
        p : float, optional
            Perímetro (para fuentes lineales). Por defecto es 1.0.
        T_inf : float, optional
            Temperatura de referencia (para fuentes lineales). Por defecto es 0.0.
        densidad : float, optional
            Densidad del fluido (para problemas de convección). Por defecto es 1.0.
        """
        self.nombre = nombre
        self.lista_superficies = superficies
        self.superficies = None
        self.gamma = gamma
        self.q = q
        self.h = h
        self.p = p
        self.T_inf = T_inf
        self.densidad = densidad
        self.centroide = Vertice(nombre)
        self.coeficientes = dict()
        self.flujos = dict()
        self.signo_normal = None
        self.s_u = 0.0
        self.phi_p = 0.0

    def set_superficies(self, superficies: list[Superficie]):
        """Asigna los objetos `Superficie` a la celda."""
        self.superficies = superficies

    def set_centroide(self, centroide: tuple[float, float, float]):
        """Establece las coordenadas del centroide de la celda."""
        self.centroide.set_punto(centroide)

    def set_signo_normal(self, normal: list[float]):
        """Asigna los signos de las normales de las superficies respecto a la celda."""
        self.signo_normal = normal

    def calcular_ecuaciones(self, metodo: Metodo = Metodo.CDS):
        """Construye la ecuación algebraica discretizada para la celda.

        Calcula los coeficientes de la ecuación `a_P * phi_P = sum(a_nb * phi_nb) + S_u`,
        donde `phi_P` es el valor en el centroide de la celda actual, y `phi_nb`
        son los valores en las celdas vecinas. El término fuente se linealiza
        como `S = S_u + S_p * phi_P`.

        Parameters
        ----------
        metodo : Metodo, optional
            El esquema de discretización a utilizar (CDS, UDS, o HDS).
            Por defecto es `Metodo.CDS`.
        """
        if self.superficies is None:
            print('Celda no está calculada')
            return
        s_p = 0.0
        self.s_u = 0.0
        if metodo == Metodo.CDS:
            for i, s in enumerate(self.superficies):
                # Términos fuente lineales (ej. por convección perimetral)
                self.s_u += self.h * self.p * self.centroide.get_distancia(s.centroide.get_punto()) * self.T_inf
                s_p += -self.h * self.p * self.centroide.get_distancia(s.centroide.get_punto())
                # Término fuente volumétrico
                self.s_u += self.q * s.A * self.centroide.get_distancia(s.centroide.get_punto())

                # --- Contribución de cada superficie ---
                if es_superficie_dirichlet(s):
                    # Frontera de valor fijo (Dirichlet)
                    # Término difusivo
                    s_p += -self.gamma * s.A / self.centroide.get_distancia(s.centroide.get_punto())
                    self.s_u += self.gamma * s.A / self.centroide.get_distancia(s.centroide.get_punto()) * s.var['T']
                    # Convectivo
                    s_p += self.densidad * np.dot(s.u, s.normal) * self.signo_normal[i]
                    self.s_u += -self.densidad * np.dot(s.u, s.normal) * self.signo_normal[i] * s.var['T']

                elif es_superficie_neumann(s):
                    # Frontera de flujo fijo (Neumann)
                    self.s_u += s.flujo * s.A
                elif es_superficie_robin(s):
                    # Frontera mixta (Robin)
                    R_eq = s.A / (self.centroide.get_distancia(s.centroide.get_punto()) / self.gamma + 1.0 / s.h)
                    s_p += -R_eq
                    self.s_u += R_eq * s.T_inf
                else:
                    # Superficie interna (conecta con otra celda)
                    vecino = s.get_vecino(self)
                    if vecino is not None:
                        # Término difusivo
                        # El coeficiente `a_nb` se añade al diccionario de coeficientes.
                        if self.gamma == vecino.gamma:
                            # Material homogéneo
                            self.coeficientes[vecino.nombre] = self.gamma * s.A / self.centroide.get_distancia(
                                vecino.centroide.get_punto())
                        else:
                            # Material no homogéneo, se usa media armónica para la conductividad.
                            g = self.centroide.get_distancia(s.centroide.get_punto()) / self.centroide.get_distancia(
                                vecino.centroide.get_punto())
                            k = self.gamma * vecino.gamma / ((1 - g) * self.gamma + g * vecino.gamma)
                            self.coeficientes[vecino.nombre] = k * s.A / self.centroide.get_distancia(
                                vecino.centroide.get_punto())
                        # Término convectivo (CDS)
                        self.coeficientes[vecino.nombre] += -self.densidad * np.dot(s.u, s.normal) * self.signo_normal[
                            i] / 2.0
        elif metodo == Metodo.UDS:
            for i, s in enumerate(self.superficies):
                self.s_u += self.h * self.p * self.centroide.get_distancia(s.centroide.get_punto()) * self.T_inf
                s_p += -self.h * self.p * self.centroide.get_distancia(s.centroide.get_punto())
                self.s_u += self.q * s.A * self.centroide.get_distancia(s.centroide.get_punto())
                if es_superficie_dirichlet(s):
                    # Difusivo
                    s_p += -self.gamma * s.A / self.centroide.get_distancia(s.centroide.get_punto())
                    self.s_u += self.gamma * s.A / self.centroide.get_distancia(s.centroide.get_punto()) * s.var['T']
                    # Convectivo
                    s_p += -max(0.0, -self.densidad * np.dot(s.u, s.normal) * self.signo_normal[i])
                    self.s_u += max(0.0, -self.densidad * np.dot(s.u, s.normal) * self.signo_normal[i]) * s.var['T']
                elif es_superficie_neumann(s):
                    # Convectivo
                    self.s_u += s.flujo * s.A
                elif es_superficie_robin(s):
                    # Difusivo
                    R_eq = s.A / (self.centroide.get_distancia(s.centroide.get_punto()) / self.gamma + 1.0 / s.h)
                    s_p += -R_eq
                    self.s_u += R_eq * s.T_inf
                else:
                    vecino = s.get_vecino(self)
                    if vecino is not None:
                        # Difusivo
                        if self.gamma == vecino.gamma:
                            self.coeficientes[vecino.nombre] = self.gamma * s.A / self.centroide.get_distancia(
                                vecino.centroide.get_punto())
                        else:
                            g = self.centroide.get_distancia(s.centroide.get_punto()) / self.centroide.get_distancia(
                                vecino.centroide.get_punto())
                            k = self.gamma * vecino.gamma / ((1 - g) * self.gamma + g * vecino.gamma)
                            self.coeficientes[vecino.nombre] = k * s.A / self.centroide.get_distancia(
                                vecino.centroide.get_punto())
                        # Convectivo
                        self.coeficientes[vecino.nombre] += max(0.0, -self.densidad * np.dot(s.u, s.normal) *
                                                                self.signo_normal[i])
        elif metodo == Metodo.HDS:
            for i, s in enumerate(self.superficies):
                self.s_u += self.h * self.p * self.centroide.get_distancia(s.centroide.get_punto()) * self.T_inf
                s_p += -self.h * self.p * self.centroide.get_distancia(s.centroide.get_punto())
                self.s_u += self.q * s.A * self.centroide.get_distancia(s.centroide.get_punto())
                if es_superficie_dirichlet(s):
                    # Difusivo
                    s_p += -self.gamma * s.A / self.centroide.get_distancia(s.centroide.get_punto())
                    self.s_u += self.gamma * s.A / self.centroide.get_distancia(s.centroide.get_punto()) * s.var['T']
                    # Convectivo
                    s_p += -max(0.0, -self.densidad * np.dot(s.u, s.normal) * self.signo_normal[i])
                    self.s_u += max(0.0, -self.densidad * np.dot(s.u, s.normal) * self.signo_normal[i]) * s.var['T']
                elif es_superficie_neumann(s):
                    # Convectivo
                    self.s_u += s.flujo * s.A
                elif es_superficie_robin(s):
                    # Difusivo
                    R_eq = s.A / (self.centroide.get_distancia(s.centroide.get_punto()) / self.gamma + 1.0 / s.h)
                    s_p += -R_eq
                    self.s_u += R_eq * s.T_inf
                else:
                    vecino = s.get_vecino(self)
                    if vecino is not None:
                        if self.gamma == vecino.gamma:
                            self.coeficientes[vecino.nombre] = max(0.0, -self.densidad * np.dot(s.u, s.normal) * \
                                                                   self.signo_normal[i],
                                                                   self.gamma * s.A / self.centroide.get_distancia(
                                                                       vecino.centroide.get_punto()) - self.densidad * np.dot( \
                                                                       s.u, s.normal) * \
                                                                   self.signo_normal[i] / 2.0)
                        else:
                            g = self.centroide.get_distancia(s.centroide.get_punto()) / self.centroide.get_distancia( \
                                vecino.centroide.get_punto())
                            k = self.gamma * vecino.gamma / ((1 - g) * self.gamma + g * vecino.gamma)
                            self.coeficientes[vecino.nombre] = max(0.0, -self.densidad * np.dot(s.u, s.normal) *
                                                                   self.signo_normal[i],
                                                                   k * s.A / self.centroide.get_distancia(
                                                                       vecino.centroide.get_punto()) - self.densidad * np.dot(
                                                                       s.u, s.normal) *
                                                                   self.signo_normal[i] / 2.0)
        # El coeficiente central a_P se calcula como la suma de los coeficientes de los vecinos
        # menos la parte del término fuente que depende de phi_P.
        self.phi_p = sum(self.coeficientes.values()) - s_p

    def get_ecuacion(self, escalar: str = r'\phi'):
        """Retorna la ecuación de la celda en formato simbólico (SymPy)."""
        if len(self.coeficientes) == 0:
            return sp.Symbol('')
        else:
            return sp.Eq(self.phi_p * sp.Symbol(escalar + '_{' + self.nombre + '}') + sum(
                [-self.coeficientes[c] * sp.Symbol(escalar + '_{' + c + '}') for c in self.coeficientes.keys()]),
                         self.s_u)

    def diagrama_balance(self, mostrar_etiquetas: bool = True):
        """Dibuja un diagrama de la celda, mostrando los flujos a través de sus superficies.

        Útil para verificar visualmente el balance de flujos en un volumen de control.
        """
        fig, ax = plt.subplots(figsize=(15, 5))
        lista_x = []
        lista_y = []
        if len(self.lista_superficies) == 2:
            x_e = self.superficies[0].vertices[0].x
            y_e = self.superficies[0].vertices[0].y
            x_w = self.superficies[1].vertices[0].x
            y_w = self.superficies[1].vertices[0].y
            ancho = abs(x_e - x_w) / 50
            lista_x.append(x_e)
            lista_y.append(y_e)
            lista_x.append(x_w)
            lista_y.append(y_w)
            lista_p = np.array([[x_e, y_e + ancho], [x_w, y_w + ancho], [x_w, y_w - ancho], [x_e, y_e - ancho]])
            ax.add_patch(
                Polygon(lista_p, closed=True, edgecolor='lightsteelblue', facecolor='lightsteelblue', linewidth=0.5))
            if es_superficie_dirichlet(self.superficies[0]) or es_superficie_neumann(
                    self.superficies[0]) or es_superficie_robin(self.superficies[0]):
                plt.plot([x_e, x_e], [y_e - ancho, y_e + ancho], ls='--', lw=0.5, color='royalblue')
            else:
                plt.plot([x_e, x_e], [y_e - ancho, y_e + ancho], lw=0.5, color='royalblue')
            if es_superficie_dirichlet(self.superficies[1]) or es_superficie_neumann(
                    self.superficies[1]) or es_superficie_robin(self.superficies[1]):
                plt.plot([x_w, x_w], [y_e - ancho, y_e + ancho], ls='--', lw=0.5, color='royalblue')
            else:
                plt.plot([x_w, x_w], [y_e - ancho, y_e + ancho], lw=0.5, color='royalblue')

            if self.h != 0:
                q = self.h * self.p * abs(x_e - x_w) * (self.centroide.get_escalar()['T'] - self.T_inf)
                x_h = np.linspace(min(x_e, x_w), max(x_e, x_w), 50)
                if q > 0.0:
                    sentido = '<-'
                else:
                    sentido = '->'
                for x in x_h:
                    ax.annotate('', xy=(x, ancho), xycoords='data',
                                xytext=(0, 50), textcoords='offset points', va='center', ha='center', size=8,
                                arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3", color='blue', ls='--',
                                                lw=0.5))
                    ax.annotate('', xy=(x, -ancho), xycoords='data',
                                xytext=(0, -50), textcoords='offset points', va='center', ha='center', size=8,
                                arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3", color='blue', ls='--',
                                                lw=0.5))
                ax.annotate('$' + 'q' + '=' + '{:G}$'.format(q),
                            xy=(0.5 * (x_e + x_w), 0.5 * (y_e + y_w) + ancho), xycoords='data',
                            xytext=(0, 50), textcoords='offset points', va='center', ha='center', size=8)

            if self.q != 0:
                q = self.q * 0.5 * (self.superficies[0].A + self.superficies[1].A) * abs(x_e - x_w)
                ax.annotate('$' + 'q' + '=' + '{:G}$'.format(q),
                            xy=(self.centroide.x, self.centroide.y), xycoords='data',
                            xytext=(0, 0), textcoords='offset points', va='center', ha='right', size=8)
        else:
            for s in self.superficies:
                lista_x.append(s.centroide.get_punto()[0])
                lista_y.append(s.centroide.get_punto()[1])
                lista_vx = []
                lista_vy = []
                lista_p = [self.centroide.get_punto()[:2]]
                for v in s.vertices:
                    lista_vx.append(v.get_punto()[0])
                    lista_vy.append(v.get_punto()[1])
                    lista_p.append(v.get_punto()[:2])
                ax.add_patch(
                    Polygon(np.array(lista_p), closed=True, edgecolor='lightsteelblue', facecolor='lightsteelblue',
                            linewidth=0.5))
                if es_superficie_dirichlet(s) or es_superficie_neumann(s) or es_superficie_robin(s):
                    plt.plot(lista_vx, lista_vy, ls='--', lw=0.5, color='royalblue')
                else:
                    plt.plot(lista_vx, lista_vy, lw=0.5, color='royalblue')
        plt.scatter(lista_x, lista_y, color='gray', marker='.')
        lista_x = []
        lista_y = []
        lista_x.append(self.centroide.get_punto()[0])
        lista_y.append(self.centroide.get_punto()[1])
        plt.scatter(lista_x, lista_y, color='r', marker='.')
        if mostrar_etiquetas:
            ax.text(self.centroide.get_punto()[0], self.centroide.get_punto()[1], self.nombre, ha="left", va="top",
                    size=6,
                    alpha=0.8,
                    bbox=dict(boxstyle="circle,pad=0.1", fc="lightgreen", ec="darkslategrey", lw=0.2, alpha=0.7))
            for s in self.superficies:
                ax.text(s.centroide.get_punto()[0], s.centroide.get_punto()[1], s.nombre, ha="left", va="top", size=6,
                        alpha=0.8,
                        bbox=dict(boxstyle="round,pad=0.1", fc="lightblue", ec="darkslategrey", lw=0.2, alpha=0.7))
                for v in s.vertices:
                    ax.text(v.get_punto()[0], v.get_punto()[1], v.nombre, ha="left", va="bottom", size=6, alpha=0.8)
        for i, s in enumerate(self.superficies):
            pos = self.signo_normal[i] * s.normal * 50
            if self.flujos[s.nombre] > 0.0:
                sentido = '<-'
            else:
                sentido = '->'
            ax.annotate('$' + 'q' + '=' + '{:G}$'.format(abs(self.flujos[s.nombre])),
                        xy=(s.centroide.get_punto()[0:2]), xycoords='data',
                        xytext=(pos[0], pos[1]), textcoords='offset points', va='center', ha='center', size=8,
                        arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3", color='blue', lw=0.5))

        ax.axis('equal')
        ax.set_axis_off()
        # plt.ylabel('$y$')
        # plt.grid()
        # plt.title('Balance')
        # plt.xlabel('$x$')
        ax.set_xmargin(0.55)
        ax.set_ymargin(0.55)
        plt.show()
