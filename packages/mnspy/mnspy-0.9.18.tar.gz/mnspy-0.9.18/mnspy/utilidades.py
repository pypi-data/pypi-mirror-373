from IPython.core.getipython import get_ipython
from IPython.display import display, Math, DisplayHandle
from numpy import matrix, ndarray, array2string, isclose


def es_notebook() -> bool:
    """Verifica si el código se está ejecutando en un entorno de notebook.

    Intenta determinar el tipo de shell de IPython para diferenciar entre un
    notebook (como Jupyter o QtConsole) y una terminal interactiva.

    Returns
    -------
    bool
        ``True`` si se ejecuta en un notebook, ``False`` en caso contrario.
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Notebook de Jupyter o QtConsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal ejecutando IPython
        else:
            return False  # Otro tipo de shell
    except NameError:
        return False  # Probablemente un intérprete estándar de Python


def mostrar_matrix(m: ndarray, n_decimal: int = None, aumentada: int =None) -> DisplayHandle | None:
    """Muestra una matriz NumPy como una tabla formateada en LaTeX.

    Si el código se ejecuta en un notebook (Jupyter), la matriz se renderiza
    utilizando LaTeX. De lo contrario, se imprime como texto plano en la consola.
    Permite especificar el número de decimales y resaltar una columna para
    representar una matriz aumentada.

    Parameters
    ----------
    m: ndarray
        Matriz a mostrar.
    n_decimal: int
        Número de decimales
    aumentada: int
        Agrega una línea vertical en la matriz en la columna con el índice
        de "aumentada", contada a partir de la última columna.

    Returns
    -------
    Render en LaTeX de la matriz si se está en un notebook; de lo contrario,
    imprime la matriz en formato de texto y no retorna nada.
    """
    m = matrix(m)
    if n_decimal is None:
        fmt = '{:}'
    else:
        fmt = '{:.' + str(n_decimal) + 'f}'
    if aumentada is None:
        texto_latex = r'\left[\begin{array}{' + 'c' * m.shape[1] + '}'
    else:
        texto_latex = r'\left[\begin{array}{' + 'c' * (m.shape[1] - aumentada) + '|' + 'c' * aumentada + '}'
    if es_notebook():
        texto_latex += _generar_matrix(m, fmt) + r'\end{array}\right]'
        return display(Math(texto_latex))
    else:
        print(array2string(m, formatter={'float_kind': lambda x: fmt.format(x)}))


def _generar_matrix(m: ndarray, fmt: str) -> str:
    """
    Convierte una matriz en una secuencia de datos en formato LaTeX.

    Parameters
    ----------
    m: ndarray
        Matriz a convertir.
    fmt: str
        Formato aplicado a cada elemento.

    Returns
    -------
    str
        String con la secuencia de datos de la matriz para LaTeX.
    """
    ni, nj = m.shape
    texto_latex = ''
    for i in range(ni):
        for j in range(nj):
            texto_latex += fmt.format(m[i, j])
            if j != (nj - 1):
                texto_latex += '&'
        if i != (ni - 1):
            texto_latex += r'\\'
    return texto_latex


def _formato_float_latex(num: float, tol_cero: float = 1E-10, formato: str ='{:.10g}'):
    """Formatea un número flotante para su visualización en LaTeX.

    Maneja la notación científica y redondea a cero los valores muy pequeños.

    Parameters
    ----------
    num : float
        Número a formatear.
    tol_cero : float, optional
        Tolerancia para considerar un número como cero, por defecto 1E-10.
    formato : str, optional
        Formato de string para el número, por defecto '{:.10g}'.

    Returns
    -------
    str
        El número formateado como un string de LaTeX.
    """
    num = num if not isclose(num, 0.0, tol_cero, tol_cero) else 0.0
    cad = formato.format(num)
    if 'e' in cad:
        significando, exponente = cad.split('e')
        return r"{} \times 10^{{{}}}".format(significando, int(exponente))
    elif 'E' in cad:
        significando, exponente = cad.split('E')
        return r"{} \times 10^{{{}}}".format(significando, int(exponente))
    return cad