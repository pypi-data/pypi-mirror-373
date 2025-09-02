from mnspy.ecuaciones_diferenciales_parciales.mvf import Celda, Vertice, SuperficieDirichlet, Superficie, Metodo, \
    es_superficie_neumann, es_superficie_dirichlet, es_superficie_robin
from mnspy.ecuaciones_algebraicas_lineales import Gauss, EcuacionesAlgebraicasLineales
from IPython.display import display, Math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib import tri
import sympy as sp

TOL_CERO = 1E-10
FORMATO_NUM = '{:.10g}'
sp.init_printing(use_latex=True)


def get_normal(puntos: list[tuple[float, float, float]]) -> np.array:
    """Calcula el vector normal unitario a una superficie definida por 3 puntos.

    Parameters
    ----------
    puntos : list[tuple[float, float, float]]
        Lista de 3 tuplas, cada una representando las coordenadas (x, y, z)
        de un punto en la superficie.

    Returns
    -------
    np.array
        Vector normal unitario.
    """
    a, b, c = puntos
    r_1 = np.array([b[0] - a[0], b[1] - a[1], b[2] - a[2]])
    r_2 = np.array([c[0] - a[0], c[1] - a[1], c[2] - a[2]])
    n = np.cross(r_1, r_2)
    return n / np.linalg.norm(n)


def get_resta(a: tuple[float, float, float], b: tuple[float, float, float]) -> np.array:
    """Calcula la resta vectorial entre dos puntos (a - b)."""
    return np.array([a[0] - b[0], a[1] - b[1], a[2] - b[2]])


class VolumenFinito:
    """Clase principal para el análisis por el Método de Volúmenes Finitos (MVF).

    Esta clase orquesta todo el proceso de simulación:
    1.  Toma una malla definida por vértices, superficies y celdas.
    2.  Realiza el pre-procesamiento geométrico: calcula centroides, áreas,
        vectores normales y conectividad entre celdas.
    3.  Construye el sistema global de ecuaciones algebraicas `[A]{phi} = {b}`
        a partir de las ecuaciones de cada celda.
    4.  Resuelve el sistema de ecuaciones para encontrar el valor del escalar `phi`
        en el centroide de cada celda.
    5.  Realiza el post-procesamiento: calcula valores derivados como flujos
        y valores interpolados en las superficies y vértices.
    6.  Proporciona métodos para visualizar la malla, la solución y los campos de flujo.

    Attributes
    ----------
    vertices : list[Vertice]
        Lista de todos los vértices de la malla.
    superficies : list[Superficie]
        Lista de todas las superficies (caras) de la malla.
    celdas : list[Celda]
        Lista de todas las celdas (volúmenes de control) de la malla.
    escalar_phi : str
        Nombre de la variable escalar que se está resolviendo (ej. 'T' para temperatura).
    _A : np.ndarray
        Matriz de coeficientes del sistema lineal global.
    _b : np.ndarray
        Vector de términos independientes del sistema lineal global.
    _sol : EcuacionesAlgebraicasLineales
        Objeto que contiene la solución del sistema lineal.
    flujos : dict
        Diccionario que almacena los flujos calculados en cada superficie de frontera.
    """
    def __init__(self, vertice: list[Vertice], superficies: list[Superficie], celdas: list[Celda],
                 escalar_phi: str = 'T', metodo: Metodo = Metodo.CDS):
        """Constructor de la clase VolumenFinito.

        Parameters
        ----------
        vertice : list[Vertice]
            Lista de todos los vértices que componen la malla.
        superficies : list[Superficie]
            Lista de todas las superficies, incluyendo las de frontera.
        celdas : list[Celda]
            Lista de todas las celdas o volúmenes de control.
        escalar_phi : str, optional
            Nombre de la variable a resolver. Por defecto es 'T'.
        metodo : Metodo, optional
            Esquema de discretización a utilizar. Por defecto es `Metodo.CDS`.
        """
        self.vertices = vertice
        self.superficies = superficies
        self.celdas = celdas
        self.escalar_phi = escalar_phi
        self._A = np.zeros((len(self.celdas), len(self.celdas)))
        self._b = np.zeros(len(self.celdas)).reshape(-1, 1)
        self._etiquetas = list()
        self._sol = None
        self.flujos = dict()
        self.limite = {'min': np.array([np.inf, np.inf, np.inf]), 'max': np.array([-np.inf, -np.inf, -np.inf])}

        # --- Pre-procesamiento de la malla ---
        # 1. Conectar vértices a superficies y calcular centroides de superficies.
        for s in self.superficies:
            s.set_vertices([vertice[i] for i in s.lista_vertices])
            for v in s.lista_vertices:
                self.vertices[v].lista_superficies.append(s)
                self.limite.update({'min': np.minimum(self.vertices[v].get_punto(), 0),
                                    'max': np.maximum(self.vertices[v].get_punto(), 0)})
            x = y = z = 0.0
            for v in s.vertices:
                x += v.x
                y += v.y
                z += v.z
            s.set_centroide((x / len(s.vertices), y / len(s.vertices), z / len(s.vertices)))
        # 2. Conectar superficies a celdas.
        for c in celdas:
            c.set_superficies([self.superficies[i] for i in c.lista_superficies])
        # 3. Calcular áreas y vectores normales para cada superficie.
        for s in self.superficies:
            if len(s.vertices) >= 3:
                # Superficie 3D (triangular)
                s.A = np.cross(get_resta(s.vertices[0].get_punto(), s.vertices[1].get_punto()),
                               get_resta(s.vertices[0].get_punto(), s.vertices[2].get_punto()))
                s.A = 0.5 * float(np.linalg.norm(s.A))
                s.set_normal(
                    get_normal([s.vertices[0].get_punto(), s.vertices[1].get_punto(), s.vertices[2].get_punto()]))
            elif len(s.vertices) == 2:
                # Superficie 2D (línea con espesor)
                s.A = float(np.linalg.norm(get_resta(s.vertices[0].get_punto(), s.vertices[1].get_punto()))) * s.t
                n = np.cross((0, 0, 1), get_resta(s.vertices[0].get_punto(), s.vertices[1].get_punto()))
                s.set_normal(n / np.linalg.norm(n))
            else:
                # Superficie 1D
                s.A = s.t
                s.set_normal(np.array([-1.0, 0.0, 0.0]))

        # 4. Calcular centroides de celda, conectividad y signos de normales.
        for c in celdas:
            self._etiquetas.append(escalar_phi + '_{' + c.nombre + '}')
            x = y = z = 0.0
            for s in c.superficies:
                s.set_vecino(c)  # Establece la relación celda-superficie-celda
                x += s.centroide.x
                y += s.centroide.y
                z += s.centroide.z
            c.set_centroide((x / len(c.superficies), y / len(c.superficies), z / len(c.superficies)))

        for c in celdas:
            signos = list()
            for s in c.superficies:
                signos.append(np.sign(np.dot(get_resta(s.centroide.get_punto(), c.centroide.get_punto()), s.normal)))
            c.set_signo_normal(signos)
            c.calcular_ecuaciones(metodo) # Discretiza la ecuación para la celda

        # 5. Ensamblaje de la matriz global [A] y el vector {b}
        for c in celdas:
            i = self._etiquetas.index(escalar_phi + '_{' + c.nombre + '}')
            self._A[i][i] = c.phi_p
            self._b[i][0] = c.s_u
            for var in c.coeficientes.keys():
                j = self._etiquetas.index(escalar_phi + '_{' + var + '}')
                self._A[i][j] = -c.coeficientes[var]

    def es_unidimensional(self) -> bool:
        """Verifica si el problema es 1D (varía solo en x)."""
        estado = self.limite['max'] != self.limite['min']
        return bool(estado[0] and not estado[1] and not estado[2])

    def es_bidimensional(self) -> bool:
        """Verifica si el problema es 2D (varía en x e y)."""
        estado = self.limite['max'] != self.limite['min']
        return bool(estado[0] and estado[1] and not estado[2])

    def es_tridimensional(self) -> bool:
        """Verifica si el problema es 3D (varía en x, y, z)."""
        estado = self.limite['max'] != self.limite['min']
        return bool(estado[0] and estado[1] and estado[2])

    def get_celda(self, nombre: str) -> Celda | None:
        """Busca y retorna una celda por su nombre."""
        for i in self.celdas:
            if i.nombre == nombre:
                return i
        return None

    def get_superficie(self, nombre: str) -> Superficie | None:
        """Busca y retorna una superficie por su nombre."""
        for i in self.superficies:
            if i.nombre == nombre:
                return i
        return None

    def get_vertice(self, nombre: str) -> Vertice | None:
        """Busca y retorna un vértice por su nombre."""
        for i in self.vertices:
            if i.nombre == nombre:
                return i
        return None

    def solucionar_por_Gauss(self):
        """Resuelve el sistema de ecuaciones lineales usando eliminación de Gauss."""
        self._sol = Gauss(self._A, self._b)
        self._sol.ajustar_etiquetas(self._etiquetas)
        self._calcular_variables_secundarias()

    def mostrar_sistema_lineal_ecuaciones(self):
        """Muestra el sistema de ecuaciones global en formato matricial."""
        if self._sol is not None:
            self._sol.mostrar_sistema()
        else:
            print('El sistema de ecuaciones no se ha calculado')

    def ajustar_solucion(self, sol: np.ndarray):
        """Permite establecer una solución externa y calcular las variables secundarias.

        Parameters
        ----------
        sol : np.ndarray
            Vector columna con los valores de la solución para cada celda.
        """
        self._sol = EcuacionesAlgebraicasLineales(self._A, self._b)
        self._sol.x = sol
        self._sol.ajustar_etiquetas(self._etiquetas)
        self._calcular_variables_secundarias()

    def get_solucion(self):
        """Retorna el vector de solución."""
        if self._sol is not None:
            return self._sol.x
        else:
            print('El sistema de ecuaciones no se ha calculado')
            return None

    def solucion(self):
        """Muestra la solución en una tabla formateada."""
        if self._sol is not None:
            return self._sol.solucion()
        else:
            print('El sistema de ecuaciones no se ha calculado')
            return None

    def _calcular_variables_secundarias(self):
        """Calcula valores derivados (post-proceso) después de resolver el sistema.

        Esto incluye:
        1.  Asignar la solución a los centroides de las celdas.
        2.  Calcular los flujos a través de cada superficie.
        3.  Interpolar los valores del escalar en los centroides de las superficies
            y en los vértices de la malla.
        """
        # 1. Asignar la solución (phi) a los centroides de las celdas.
        for i, c in enumerate(self.celdas):
            c.centroide.set_escalar({self.escalar_phi: self._sol.x[i, 0]})

        # 2. Calcular flujos e interpolar valores en las superficies.
        for c in self.celdas:
            for s in c.superficies:
                if es_superficie_dirichlet(s):
                    # Para fronteras Dirichlet, el valor en la cara es conocido.
                    s.centroide.set_escalar({self.escalar_phi: s.var[self.escalar_phi]})
                    pro_1 = c.centroide.get_escalar()[self.escalar_phi]
                    pro_2 = s.centroide.get_escalar()[self.escalar_phi]
                    # El flujo se calcula usando la ley de Fourier/Fick.
                    q = c.gamma * (pro_1 - pro_2) * s.A / c.centroide.get_distancia(s.centroide.get_punto())
                    c.flujos.update({s.nombre: q})
                    self.flujos.update({s.nombre: q})
                elif es_superficie_neumann(s):
                    # Para fronteras Neumann, el flujo es conocido.
                    # El valor en la cara se extrapola desde el centroide de la celda.
                    s.centroide.set_escalar({self.escalar_phi: c.centroide.get_escalar()[
                                                                   self.escalar_phi] + c.centroide.get_distancia(
                        s.centroide.get_punto()) * s.flujo / c.gamma})
                    c.flujos.update({s.nombre: -s.flujo * s.A})
                    self.flujos.update({s.nombre: -s.flujo * s.A})
                elif es_superficie_robin(s):
                    # Para fronteras Robin, se calcula un valor equivalente en la cara.
                    pro_1 = c.centroide.get_escalar()[self.escalar_phi]
                    r = c.centroide.get_distancia(s.centroide.get_punto())
                    pro_2 = (s.h * s.T_inf + c.gamma * pro_1 / r) / (s.h + c.gamma / r)
                    s.centroide.set_escalar(
                        {self.escalar_phi: pro_2})
                    # El flujo se calcula a partir de los valores de la celda y la cara.
                    q = c.gamma * (pro_1 - pro_2) * s.A / c.centroide.get_distancia(s.centroide.get_punto())
                    c.flujos.update({s.nombre: q})
                    self.flujos.update({s.nombre: q})
                else:
                    # Para superficies internas, se interpola linealmente el valor en la cara.
                    vecino = s.get_vecino(c)
                    pro_1 = c.centroide.get_escalar()[self.escalar_phi]
                    pro_2 = vecino.centroide.get_escalar()[self.escalar_phi]
                    g = c.centroide.get_distancia(s.centroide.get_punto()) / c.centroide.get_distancia(
                        vecino.centroide.get_punto())
                    # s.centroide.set_escalar({self.escalar_phi: (1 - g) * pro_1 + g * pro_2})
                    # Interpolación con media armónica para materiales diferentes.
                    s.centroide.set_escalar({self.escalar_phi: (c.gamma * (
                            1 - g) * pro_1 + vecino.gamma * g * pro_2) / (c.gamma * (1 - g) + vecino.gamma * g)})
                    # Cálculo del flujo entre las dos celdas.
                    k = c.gamma * vecino.gamma / ((1 - g) * c.gamma + g * vecino.gamma)
                    q = k * (pro_1 - pro_2) * s.A / c.centroide.get_distancia(vecino.centroide.get_punto())
                    c.flujos.update({s.nombre: q})

        # 3. Interpolar valores en los vértices.
        for v in self.vertices:
            if len(v.lista_superficies):
                # Se utiliza un promedio ponderado por la inversa de la distancia
                # desde el vértice a los centroides de las superficies circundantes.
                val = {self.escalar_phi: []}
                r = list()
                t_fija = list()
                # Si un vértice está en una frontera Dirichlet, se le da prioridad a ese valor.
                for s in v.lista_superficies:
                    if es_superficie_dirichlet(s):
                        t_fija.append(s.centroide.get_escalar()[self.escalar_phi])
                    val[self.escalar_phi].append(s.centroide.get_escalar()[self.escalar_phi])
                    dis = v.get_distancia(s.centroide.get_punto())
                    if dis == 0.0:
                        r.append(1.0)
                    else:
                        r.append(1.0 / dis)
                if len(t_fija) == 0:
                    v.set_escalar(
                        {self.escalar_phi: np.dot(np.array(val[self.escalar_phi]), np.array(r)) / np.sum(np.array(r))})
                else:
                    v.set_escalar({self.escalar_phi: np.mean(np.array(t_fija))})

    def mostrar_ecuaciones(self):
        texto_latex = r'\begin{align}'
        for c in self.celdas:
            texto_latex += sp.latex(c.get_ecuacion(r'\,' + self.escalar_phi).lhs) + r'&=' + sp.latex(
                c.get_ecuacion(r'\,' + self.escalar_phi).rhs) + r'\\'
        texto_latex += r'\end{align}'
        return display(Math(texto_latex))

    def __mallado(self, mostrar_etiquetas, ax, mostrar_nodos=True):
        """Método privado para dibujar la malla base."""
        lista_x = []
        lista_y = []
        for c in self.celdas:
            if self.es_unidimensional():
                ancho = (self.limite['max'][0] - self.limite['min'][0]) / 80
                x_e = self.vertices[c.superficies[0].lista_vertices[0]].x
                y_e = self.vertices[c.superficies[0].lista_vertices[0]].y
                x_w = self.vertices[c.superficies[1].lista_vertices[0]].x
                y_w = self.vertices[c.superficies[1].lista_vertices[0]].y
                lista_x.append(x_e)
                lista_y.append(y_e)
                lista_x.append(x_w)
                lista_y.append(y_w)
                lista_p = np.array([[x_e, y_e + ancho], [x_w, y_w + ancho], [x_w, y_w - ancho], [x_e, y_e - ancho]])
                ax.add_patch(Polygon(lista_p, closed=True, edgecolor='lightsteelblue', facecolor='lightsteelblue',
                                     linewidth=0.5))
                if es_superficie_dirichlet(c.superficies[0]) or es_superficie_neumann(
                        c.superficies[0]) or es_superficie_robin(c.superficies[0]):
                    plt.plot([x_e, x_e], [y_e - ancho, y_e + ancho], ls='--', lw=1.5, color='royalblue')
                else:
                    plt.plot([x_e, x_e], [y_e - ancho, y_e + ancho], lw=1.5, color='royalblue')
                if es_superficie_dirichlet(c.superficies[1]) or es_superficie_neumann(
                        c.superficies[1]) or es_superficie_robin(c.superficies[1]):
                    plt.plot([x_w, x_w], [y_e - ancho, y_e + ancho], ls='--', lw=1.5, color='royalblue')
                else:
                    plt.plot([x_w, x_w], [y_e - ancho, y_e + ancho], lw=1.5, color='royalblue')

            else:
                for s in c.superficies:
                    lista_x.append(s.centroide.get_punto()[0])
                    lista_y.append(s.centroide.get_punto()[1])
                    lista_vx = []
                    lista_vy = []
                    lista_p = [c.centroide.get_punto()[:2]]
                    for v in s.vertices:
                        lista_vx.append(v.get_punto()[0])
                        lista_vy.append(v.get_punto()[1])
                        lista_p.append(v.get_punto()[:2])
                    ax.add_patch(Polygon(lista_p, closed=True, edgecolor='lightsteelblue', facecolor='lightsteelblue',
                                         linewidth=0.5))
                    if es_superficie_dirichlet(s) or es_superficie_neumann(s) or es_superficie_robin(s):
                        plt.plot(lista_vx, lista_vy, ls='--', lw=0.5, color='royalblue')
                    else:
                        plt.plot(lista_vx, lista_vy, lw=0.5, color='royalblue')
        if mostrar_nodos:
            plt.scatter(lista_x, lista_y, color='gray', marker='.')
        lista_x = []
        lista_y = []
        for c in self.celdas:
            lista_x.append(c.centroide.get_punto()[0])
            lista_y.append(c.centroide.get_punto()[1])
        if mostrar_nodos:
            plt.scatter(lista_x, lista_y, color='r', marker='.')
        if mostrar_etiquetas:
            for c in self.celdas:
                ax.text(c.centroide.get_punto()[0], c.centroide.get_punto()[1], c.nombre, ha="left", va="top", size=6,
                        alpha=0.8,
                        bbox=dict(boxstyle="circle,pad=0.1", fc="lightgreen", ec="darkslategrey", lw=0.2, alpha=0.7))
            for s in self.superficies:
                ax.text(s.centroide.get_punto()[0], s.centroide.get_punto()[1], s.nombre, ha="left", va="top", size=6,
                        alpha=0.8,
                        bbox=dict(boxstyle="round,pad=0.1", fc="lightblue", ec="darkslategrey", lw=0.2, alpha=0.7))
            for v in self.vertices:
                ax.text(v.get_punto()[0], v.get_punto()[1], v.nombre, ha="left", va="bottom", size=6, alpha=0.8)

    def mallado(self, mostrar_etiquetas: bool = True):
        """Dibuja la malla de volúmenes finitos.

        Parameters
        ----------
        mostrar_etiquetas : bool, optional
            Si es True, muestra los nombres de celdas, superficies y vértices.
            Por defecto es True.
        """
        fig, ax = plt.subplots(figsize=(15, 5))
        self.__mallado(mostrar_etiquetas, ax)
        ax.axis('equal')
        plt.title('mallado')
        plt.show()

    # Código comentado original, se deja por si se quiere reutilizar.
    # def diagrama_solucion(self, sol: np.ndarray):
    #     fig, ax = plt.subplots(figsize=(15, 5))
    #     color_fondo = 'azure'
    #     color_figura = 'royalblue'
    #     color_grid = 'silver'
    #     lista_x = []
    #     lista_y = []
    #     lista_z = []
    #     for v in self.vertices:
    #         i, j, k = v.get_punto()
    #         lista_x.append(i)
    #         lista_y.append(j)
    #     lista_i = list()
    #     lon = len(self.vertices)
    #     for item, c in enumerate(self.celdas):
    #         i, j, k = c.centroide.get_punto()
    #         lista_x.append(i)
    #         lista_y.append(j)
    #         for s in c.superficies:
    #             nuevo = [lon + item]
    #             if len(s.lista_vertices) == 1:
    #                 nuevo *= 2
    #             for v in s.lista_vertices:
    #                 nuevo.append(v)
    #             lista_i.append(nuevo)
    #             lista_z.append(sol[item, 0])
    #     cel = tri.Triangulation(lista_x, lista_y, np.array(lista_i))
    #     plt.tripcolor(cel, facecolors=lista_z, cmap='YlGn', edgecolors='face', shading='flat', linewidth=0.2)
    #     plt.colorbar()
    #     plt.show()

    def diagrama_valores_escalar(self, escalar: str = None):
        """Dibuja un mapa de colores de la solución en la malla.

        Parameters
        ----------
        escalar : str, optional
            Nombre del escalar a graficar. Si es None, usa el escalar
            principal de la simulación (ej. 'T'). Por defecto es None.
        """
        if escalar is None:
            escalar = 'T'
        fig, ax = plt.subplots(figsize=(15, 5))
        lista_x = []
        lista_y = []
        lista_z = []
        lista_i = []
        if self.es_unidimensional():
            ancho = (self.limite['max'][0] - self.limite['min'][0]) / 80
            for v in self.vertices:
                i, j, k = v.get_punto()
                lista_x.append(i)
                lista_y.append(j - ancho)
                lista_x.append(i)
                lista_y.append(j + ancho)
            lon = len(lista_x)
            for item, c in enumerate(self.celdas):
                i, j, k = c.centroide.get_punto()
                lista_x.append(i)
                lista_y.append(j)
                s_1 = c.superficies[0].lista_vertices[0]
                s_2 = c.superficies[1].lista_vertices[0]
                lista_i.append([lon + item, s_1 * 2, s_1 * 2 + 1])
                lista_z.append(c.centroide.get_escalar()[escalar])
                lista_i.append([lon + item, s_1 * 2 + 1, s_2 * 2 + 1])
                lista_z.append(c.centroide.get_escalar()[escalar])
                lista_i.append([lon + item, s_2 * 2 + 1, s_2 * 2])
                lista_z.append(c.centroide.get_escalar()[escalar])
                lista_i.append([lon + item, s_2 * 2, s_1 * 2])
                lista_z.append(c.centroide.get_escalar()[escalar])
        else:
            for v in self.vertices:
                i, j, k = v.get_punto()
                lista_x.append(i)
                lista_y.append(j)
            lon = len(self.vertices)
            for item, c in enumerate(self.celdas):
                i, j, k = c.centroide.get_punto()
                lista_x.append(i)
                lista_y.append(j)
                for s in c.superficies:
                    nuevo = [lon + item]
                    for v in s.lista_vertices:
                        nuevo.append(v)
                    lista_i.append(nuevo)
                    lista_z.append(c.centroide.get_escalar()[escalar])
        ax.axis('equal')
        for c in self.celdas:
            # plt.annotate('{:.3f}'.format(c.centroide.get_escalar()[escalar]), c.centroide.get_punto()[:2],
            #              xytext=(0, 0), textcoords='offset points', ha='center', va='center', size=7)
            ax.text(c.centroide.get_punto()[0], c.centroide.get_punto()[1],
                    '$' + '{:.3f}'.format(c.centroide.get_escalar()[escalar]) + '$', ha="center", va="center", size=6,
                    alpha=0.8, bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="white", lw=0.2, alpha=0.7))
        cel = tri.Triangulation(lista_x, lista_y, np.array(lista_i))
        plt.tripcolor(cel, facecolors=lista_z, cmap='YlGn', edgecolors='none', shading='flat')
        plt.colorbar()
        plt.show()

    def diagrama_T(self):
        """Dibuja un mapa de contorno (isolíneas) de la temperatura."""
        fig, ax = plt.subplots(figsize=(15, 5))
        lista_x = []
        lista_y = []
        lista_z = []
        for v in self.vertices:
            i, j, k = v.get_punto()
            lista_x.append(i)
            lista_y.append(j)
            lista_z.append(v.get_escalar()['T'])
        lista_i = list()
        lon_v = len(self.vertices)
        ancho = None
        if self.es_unidimensional():
            ancho = (self.limite['max'][0] - self.limite['min'][0]) / 100
        for item, c in enumerate(self.celdas):
            i, j, k = c.centroide.get_punto()
            lista_x.append(i)
            lista_y.append(j)
            lista_z.append(c.centroide.get_escalar()['T'])
            if self.es_unidimensional():
                lista_x.append(self.vertices[c.superficies[0].lista_vertices[0]].x)
                lista_y.append(ancho)
                lista_z.append(self.vertices[c.superficies[0].lista_vertices[0]].get_escalar()['T'])

                lista_x.append(self.vertices[c.superficies[1].lista_vertices[0]].x)
                lista_y.append(ancho)
                lista_z.append(self.vertices[c.superficies[1].lista_vertices[0]].get_escalar()['T'])

                lista_x.append(self.vertices[c.superficies[1].lista_vertices[0]].x)
                lista_y.append(-ancho)
                lista_z.append(self.vertices[c.superficies[1].lista_vertices[0]].get_escalar()['T'])

                lista_x.append(self.vertices[c.superficies[0].lista_vertices[0]].x)
                lista_y.append(-ancho)
                lista_z.append(self.vertices[c.superficies[0].lista_vertices[0]].get_escalar()['T'])

                lista_i.append([lon_v + item * 5, c.superficies[0].lista_vertices[0], lon_v + item * 5 + 1])
                lista_i.append([lon_v + item * 5, lon_v + item * 5 + 1, lon_v + item * 5 + 2])
                lista_i.append([lon_v + item * 5, lon_v + item * 5 + 2, c.superficies[1].lista_vertices[0]])
                lista_i.append([lon_v + item * 5, c.superficies[1].lista_vertices[0], lon_v + item * 5 + 3])
                lista_i.append([lon_v + item * 5, lon_v + item * 5 + 3, lon_v + item * 5 + 4])
                lista_i.append([lon_v + item * 5, lon_v + item * 5 + 4, c.superficies[0].lista_vertices[0]])
            else:
                for s in c.superficies:
                    nuevo = [lon_v + item]
                    for v in s.lista_vertices:
                        nuevo.append(v)
                    lista_i.append(nuevo)
        ax.axis('equal')
        cel = tri.Triangulation(lista_x, lista_y, np.array(lista_i))
        plt.tricontourf(cel, lista_z, levels=64, cmap=plt.jet())
        plt.colorbar()
        plt.show()

    def diagrama_campo_flujos(self):
        """Dibuja el campo vectorial de los flujos calculados."""
        fig, ax = plt.subplots(figsize=(15, 5))
        self.__mallado(False, ax, False)
        X = [c.centroide.get_punto()[0] for c in self.celdas]
        Y = [c.centroide.get_punto()[1] for c in self.celdas]
        U = []
        V = []
        for c in self.celdas:
            m = (np.array(list(c.flujos.values())) * np.array(c.signo_normal)).reshape(-1, 1)
            n = np.array([v.normal for v in c.superficies])
            r = np.mean(m * n, axis=0)
            U.append(r[0])
            V.append(r[1])
        ax.axis('equal')
        # plt.quiver(X, Y, U, V, units='width', color='red', pivot='mid', scale=20)
        ancho = np.max(np.hypot(U, V))
        if ancho == 0:
            ancho = 1
        ax.set_title('Campo flujo de calor')
        ax.quiver(X, Y, U, V, color='green', pivot='mid', scale=ancho / 50, scale_units='dots', headwidth=2.5,
                  headlength=3, headaxislength=2, linewidths=0.2, width=0.0025)
        plt.show()

    def diagrama_campo_velocidades(self):
        """Dibuja el campo vectorial de las velocidades (si aplica)."""
        fig, ax = plt.subplots(figsize=(15, 5))
        self.__mallado(False, ax, False)
        X = [c.centroide.get_punto()[0] for c in self.celdas]
        Y = [c.centroide.get_punto()[1] for c in self.celdas]
        U = []
        V = []
        for c in self.celdas:
            r = np.mean(np.array([v.u for v in c.superficies]), axis=0)
            U.append(r[0])
            V.append(r[1])
        ax.axis('equal')
        ancho = np.max(np.hypot(U, V))
        if ancho == 0:
            ancho = 1
        ax.set_title('Campo flujo de velocidades')
        ax.quiver(X, Y, U, V, color='red', pivot='mid', scale=ancho / 50, scale_units='dots', headwidth=2.5,
                  headlength=3, headaxislength=2, linewidths=0.2, width=0.0025)
        plt.show()


def main():
    # T_0 = 100
    # T_5 = 500
    # delta_x = 0.1
    # k = 1000
    # A = 10E-3
    # # Vertices
    # v = [Vertice(str(i), i * delta_x) for i in range(6)]
    # # Superficies
    # s = [SuperficieDirichlet('0', [0], {'T': T_0}, A), Superficie('1', [1], A), Superficie('2', [2], A),
    #      Superficie('3', [3], A), Superficie('4', [4], A), SuperficieDirichlet('5', [5], {'T': T_5}, A)]
    # # Celdas
    # c = [Celda(str(i + 1), [i, i + 1], k) for i in range(len(s) - 1)]
    # vol = VolumenFinito(v, s, c)
    from mnspy import Vertice, Superficie, SuperficieDirichlet, SuperficieNeumann, SuperficieRobin
    dis_x = [0.0, 0.1, 0.3, 0.6]
    dis_y = [0.0, 0.1, 0.2, 0.3]
    n_x = len(dis_x)
    n_y = len(dis_y)
    k_1 = 1E-3
    k_2 = 1E2
    A = 1
    v = list()
    for j in range(len(dis_y)):
        for i in range(len(dis_x)):
            v.append(Vertice(str(i + j * len(dis_x)), dis_x[i], dis_y[j]))
    # Superficies
    s = list()
    for j in range(n_y):
        for i in range(n_x - 1):
            if j == 0:
                if i == 0:
                    s.append(SuperficieNeumann(str(i + (n_x - 1) * j), [i + (n_x) * j, i + 1 + (n_x) * j], 0.0, A))
                else:
                    s.append(SuperficieNeumann(str(i + (n_x - 1) * j), [i + (n_x) * j, i + 1 + (n_x) * j], 100.0, A))
            elif j == n_y - 1:
                s.append(SuperficieRobin(str(i + (n_x - 1) * j), [i + (n_x) * j, i + 1 + (n_x) * j], 20.0, 300.0, A))
            else:
                s.append(Superficie(str(i + (n_x - 1) * j), [i + (n_x) * j, i + 1 + (n_x) * j], A))
    k = (n_x - 1) * n_y
    for j in range(n_y - 1):
        for i in range(n_x):
            if i == 0:
                s.append(SuperficieDirichlet(str(k + i + n_x * j), [i + n_x * j, i + n_x * (j + 1)], {'T': 320}, A))
            elif i == n_x - 1:
                s.append(SuperficieNeumann(str(k + i + n_x * j), [i + n_x * j, i + n_x * (j + 1)], 0.0, A))
            else:
                s.append(Superficie(str(k + i + n_x * j), [i + n_x * j, i + n_x * (j + 1)], A))
    # Celdas
    c = list()
    for j in range(n_y - 1):
        for i in range(n_x - 1):
            p = dis_x[i + 1] - dis_x[i]
            if i == 0:
                c.append(Celda(str(i + 1 + (n_x - 1) * j),
                               [i + (n_x - 1) * j, k + i + 1 + n_x * j, i + (n_x - 1) * (j + 1), k + i + n_x * j],
                               gamma=k_1))
            else:
                c.append(Celda(str(i + 1 + (n_x - 1) * j),
                               [i + (n_x - 1) * j, k + i + 1 + n_x * j, i + (n_x - 1) * (j + 1), k + i + n_x * j],
                               gamma=k_2))
    vol = VolumenFinito(v, s, c)


if __name__ == '__main__':
    main()
