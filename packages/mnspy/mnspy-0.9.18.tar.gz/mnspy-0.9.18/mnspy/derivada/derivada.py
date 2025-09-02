import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Derivada:
    """Calcula la derivada numérica de una función utilizando diferencias finitas.

    Attributes
    ----------
    f : callable
        Función a derivar.
    h : float
        Tamaño del paso (incremento en x) para el cálculo.
    modo : str
        Método de diferencia finita: 'adelante', 'atrás' o 'centrada'.
    orden_error : str
        Orden de error de la aproximación: 'h' o 'h2' para 'adelante'/'atrás',
        y 'h2' o 'h4' para 'centrada'.
    derivada: float
        Resultado del último cálculo de la derivada.

    Methods
    -------
    derivar(x: float):
        Calcula la derivada en el punto `x`.
    graficar():
        Grafica la función y la línea tangente en un punto dado.

    Examples
    -------
    from mnspy import Derivada
    import numpy as np

    def g(x):
        return (x + 7) * (x + 2) * (x - 4) * (x - 12) / 100

    der = Derivada(g, orden='h', n=4)
    der.derivar(2)
    print(der.derivada)
    der = Derivada(g, orden='h', modo='atrás', n=4)
    der.derivar(2)
    print(der.derivada)
    der = Derivada(g, orden='h', modo='atrás', h=0.4)
    der.derivar(2)
    print(der.derivada)
    der.graficar(2, delta=1.0)
    """
    def __init__(self, f: callable, n: int = 1, h: float = 1e-3, orden: str = 'h2', modo: str = 'centrada'):
        """Constructor de la clase Derivada.

        Parameters
        ----------
        f : callable
            Función a derivar, f(x).
        n : int, optional
            Grado de la derivada (1, 2, 3 o 4). Por defecto es 1.
        h : float, optional
            Tamaño del paso. Por defecto es 1e-3.
        orden : str, optional
            Orden de error de la aproximación.
            - Para modo 'adelante' y 'atrás': 'h' o 'h2'.
            - Para modo 'centrada': 'h2' o 'h4'.
            Por defecto es 'h2'.
        modo : str, optional
            Método de diferencia finita a utilizar: 'adelante', 'atrás' o 'centrada'.
            Por defecto es 'centrada'.
        """
        self._f = f
        self._n = n
        self._h = h
        self._orden = orden
        self._modo = modo
        self.derivada = None
        plt.ioff()  # deshabilitada interactividad matplotlib

    def derivar(self, x: float):
        """Calcula la derivada en el punto `x` según el modo y orden configurados.

        El resultado se almacena en el atributo `self.derivada`.

        Nota del desarrollador: Este método podría ser refactorizado utilizando un
        diccionario de funciones para mapear las combinaciones de (modo, n, orden)
        a sus respectivas fórmulas, lo que reduciría la complejidad y la
        repetición del código.

        Parameters
        ----------
        x: float
            Punto en el que se evaluará la derivada.
        """
        # --- Fórmulas de Diferencias Finitas Hacia Adelante ---
        if self._modo == 'adelante':
            if self._n == 1:
                if self._orden == 'h':
                    self.derivada = (self._f(x + self._h) - self._f(x)) / self._h
                else:
                    self.derivada = (-self._f(x + 2 * self._h) + 4 * self._f(x + self._h) - 3 * self._f(x)) / (
                            2 * self._h)
            elif self._n == 2:
                if self._orden == 'h':
                    self.derivada = (self._f(x + 2 * self._h) - 2 * self._f(x + self._h) + self._f(x)) / (
                            self._h ** 2)
                else:
                    self.derivada = (-self._f(x + 3 * self._h) + 4 * self._f(x + 2 * self._h) - 5 * self._f(
                        x + self._h) + 2 * self._f(x)) / (self._h ** 2)
            elif self._n == 3:
                if self._orden == 'h':
                    self.derivada = (self._f(x + 3 * self._h) - 3 * self._f(x + 2 * self._h) + 3 * self._f(
                        x + self._h) - self._f(x)) / (self._h ** 3)
                else:
                    self.derivada = (-3 * self._f(x + 4 * self._h) + 14 * self._f(x + 3 * self._h) - 24 * self._f(
                        x + 2 * self._h) + 18 * self._f(x + self._h) - 5 * self._f(x)) / (2 * self._h ** 3)
            else:
                if self._orden == 'h':
                    self.derivada = (self._f(x + 4 * self._h) - 4 * self._f(x + 3 * self._h) + 6 * self._f(
                        x + 2 * self._h) - 4 * self._f(x + self._h) + self._f(x)) / (self._h ** 4)
                else:
                    self.derivada = (- 2 * self._f(x + 5 * self._h) + 11 * self._f(x + 4 * self._h) - 24 * self._f(
                        x + 3 * self._h) + 26 * self._f(x + 2 * self._h) - 14 * self._f(x + self._h) + 3 * self._f(
                        x)) / (
                                            self._h ** 4)
        # --- Fórmulas de Diferencias Finitas Hacia Atrás ---
        elif self._modo == 'atrás':
            if self._n == 1:
                if self._orden == 'h':
                    self.derivada = (self._f(x) - self._f(x - self._h)) / self._h
                else:
                    self.derivada = (3 * self._f(x) - 4 * self._f(x - self._h) + self._f(x - 2 * self._h)) / (
                            2 * self._h)
            elif self._n == 2:
                if self._orden == 'h':
                    self.derivada = (self._f(x) - 2 * self._f(x - self._h) + self._f(x - 2 * self._h)) / (
                            self._h ** 2)
                else:
                    self.derivada = (2 * self._f(x) - 5 * self._f(x - self._h) + 4 * self._f(
                        x - 2 * self._h) - self._f(
                        x - 3 * self._h)) / (self._h ** 2)
            elif self._n == 3:
                if self._orden == 'h':
                    self.derivada = (self._f(x) - 3 * self._f(x - self._h) + 3 * self._f(x - 2 * self._h) - self._f(
                        x - 3 * self._h)) / (self._h ** 3)
                else:
                    self.derivada = (5 * self._f(x) - 18 * self._f(x - self._h) + 24 * self._f(
                        x - 2 * self._h) - 14 * self._f(x - 3 * self._h) + 3 * self._f(x - 4 * self._h)) / (
                                            2 * self._h ** 3)
            else:
                if self._orden == 'h':
                    self.derivada = (self._f(x) - 4 * self._f(x - self._h) + 6 * self._f(
                        x - 2 * self._h) - 4 * self._f(
                        x - 3 * self._h) + self._f(x - 4 * self._h)) / (self._h ** 4)
                else:
                    self.derivada = (3 * self._f(x) - 14 * self._f(x - self._h) + 26 * self._f(
                        x - 2 * self._h) - 24 * self._f(x - 3 * self._h) + 11 * self._f(
                        x - 4 * self._h) - 2 * self._f(
                        x - 5 * self._h)) / (self._h ** 4)
        # --- Fórmulas de Diferencias Finitas Centradas ---
        else:
            self._modo = 'centrada'
            if self._n == 1:
                if self._orden == 'h2':
                    self.derivada = (self._f(x + self._h) - self._f(x - self._h)) / (2 * self._h)
                else:
                    self.derivada = (-self._f(x + 2 * self._h) + 8 * self._f(x + self._h) - 8 * self._f(
                        x - self._h) + self._f(
                        x - 2 * self._h)) / (12 * self._h)
            elif self._n == 2:
                if self._orden == 'h2':
                    self.derivada = (self._f(x + self._h) - 2 * self._f(x) + self._f(x - self._h)) / (self._h ** 2)
                else:
                    self.derivada = (-self._f(x + 2 * self._h) + 16 * self._f(x + self._h) - 30 * self._f(
                        x) + 16 * self._f(
                        x - self._h) - self._f(x - 2 * self._h)) / (12 * self._h ** 2)
            elif self._n == 3:
                if self._orden == 'h2':
                    self.derivada = (self._f(x + 2 * self._h) - 2 * self._f(x + self._h) + 2 * self._f(
                        x - self._h) - self._f(
                        x - 2 * self._h)) / (2 * self._h ** 3)
                else:
                    self.derivada = (-self._f(x + 3 * self._h) + 8 * self._f(x + 2 * self._h) - 13 * self._f(
                        x + self._h) + 13 * self._f(x - self._h) - 8 * self._f(x - 2 * self._h) + self._f(
                        x - 3 * self._h)) / (
                                            8 * self._h ** 3)
            else:
                if self._orden == 'h2':
                    self.derivada = (self._f(x + 2 * self._h) - 4 * self._f(x + self._h) + 6 * self._f(
                        x) - 4 * self._f(
                        x - self._h) + self._f(x - 2 * self._h)) / (self._h ** 4)
                else:
                    self.derivada = (-self._f(x + 3 * self._h) + 12 * self._f(x + 2 * self._h) - 39 * self._f(
                        x + self._h) + 56 * self._f(x) - 39 * self._f(x - self._h) + 12 * self._f(
                        x - 2 * self._h) - self._f(
                        x - 3 * self._h)) / (6 * self._h ** 4)

    def graficar(self, x: float, x_min: float = None, x_max: float = None, delta: float = 10) -> None:
        """Grafica la función y la línea tangente en el punto `x`.

        Parameters
        ----------
        x : float
            Punto en el que se dibujará la tangente.
        x_min : float, optional
            Límite inferior del eje x para la gráfica.
        x_max : float, optional
            Límite superior del eje x para la gráfica.
        delta : float, optional
            Si `x_min` y `x_max` no se proporcionan, define el rango de la gráfica
            alrededor de `x`. Por defecto es 10.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        n = self._n
        self._n = 1
        self.derivar(x)
        self._n = n
        if x_min is None:
            x_min = x - delta
        if x_max is None:
            x_max = x + delta
        if self._orden == 'h':
            orden = r'$\mathcal{O}(h)$'
        elif self._orden == 'h2':
            orden = r'$\mathcal{O}(h^{2})$'
        else:
            orden = r'$\mathcal{O}(h^{4})$'
        y = self._f(x)
        x_list = np.linspace(x_min, x_max, 100)
        y_list = self._f(x_list)
        plt.scatter(x, y, c='r', lw=2, label='Punto (' + str(x) + ', ' + str(self._f(x)) + ')')
        plt.plot(x_list, y_list, linestyle='-', c='b', lw=2, label='$f(x)$')
        plt.title('Derivada = ' + str(self.derivada))
        plt.suptitle('h = ' + str(self._h) + ', modo = ' + self._modo + ', orden = ' + orden)
        plt.axline((x, y), slope=self.derivada, linestyle='dashed', c='r', lw=2,
                   label='Derivada')
        plt.grid()
        plt.legend()
        plt.show()


def main():
    """Función principal para demostración."""
    def g(x):
        return (x + 7) * (x + 2) * (x - 4) * (x - 12) / 100

    der = Derivada(g, orden='h', n=4)
    der.derivar(2)
    print(der.derivada)
    der = Derivada(g, orden='h', modo='atrás', n=4)
    der.derivar(2)
    print(der.derivada)
    der = Derivada(g, orden='h', modo='atrás', h=0.4)
    der.derivar(2)
    print(der.derivada)
    der.graficar(2, 1.5, 2.5)
    print(der.derivada)


if __name__ == '__main__':
    main()
