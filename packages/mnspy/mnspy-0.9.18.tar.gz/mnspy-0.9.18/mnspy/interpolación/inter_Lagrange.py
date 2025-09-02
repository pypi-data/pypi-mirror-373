from mnspy.interpolación import Interpolacion
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

sp.init_printing(use_latex=True)

plt.rcParams.update(plt.rcParamsDefault)

class InterpolacionLagrange(Interpolacion):
    """Calcula el polinomio de interpolación de Lagrange.

    Este método construye un único polinomio que pasa exactamente por todos
    los puntos de datos proporcionados. Se basa en la construcción de
    polinomios base de Lagrange L_i(x).

    Attributes
    ----------
    x : np.ndarray
        Array con los datos de la variable independiente.
    y : np.ndarray
        Array con los datos de la variable dependiente.

    Methods
    -------
    evaluar(x: float):
        Evalúa el polinomio de interpolación en un punto `x`.
    obtener_polinomio():
        Genera la expresión simbólica del polinomio de interpolación.
    graficar():
        Genera una gráfica del polinomio y los puntos de datos.

    Examples
    -------
    from mnspy import InterpolacionLagrange
    import numpy as np

    x = np.array([1., 4., 6., 5.])
    y = np.log(x)
    inter = InterpolacionLagrange(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)
    print(inter.obtener_polinomio(expandido=True))
    """

    def __init__(self, x: np.ndarray, y: np.ndarray):
        """Constructor de la clase InterpolacionLagrange.

        Parameters
        ----------
        x: np.ndarray
            Array con los datos de la variable independiente
        y: np.ndarray
            Array con los datos de la variable dependiente
        """
        super().__init__(x, y)

    def evaluar(self, x: float) -> float:
        """Evalúa el polinomio de interpolación en un punto `x` dado.

        Implementa la fórmula: P(x) = sum_{i=0}^{n-1} y_i * L_i(x),
        donde L_i(x) es el i-ésimo polinomio base de Lagrange.

        Parameters
        ----------
        x : float
            Valor de la variable independiente en el que se desea interpolar.

        Returns
        -------
        float
            El valor interpolado y(x).
        """
        s = 0
        for i in range(self._n):
            p = self._y[i]
            # Calcula el polinomio base L_i(x)
            for j in range(self._n):
                if i != j:
                    p *= (x - self._x[j]) / (self._x[i] - self._x[j])
            s += p
        return s

    def obtener_polinomio(self, expandido: bool = False):
        """Genera la expresión simbólica del polinomio de interpolación de Lagrange.

        Parameters
        ----------
        expandido: bool
            Si es verdadero, retorna el polinomio expandido, en caso contrario muestra el polinomio en forma
            de suma de polinomios base de Lagrange.

        Returns
        -------
        Retorna el polinomio que pasa por los puntos de los datos de la interpolación
        """
        x = sp.symbols('x')
        pol = sum(
            [self._y[i] * np.prod([(x - self._x[j]) / (self._x[i] - self._x[j]) for j in range(self._n) if i != j]) for
             i in
             range(self._n)])
        if expandido:
            return sp.expand(pol)
        else:
            return pol

    def graficar(self, x: float) -> None:
        """Genera una gráfica del polinomio de interpolación.

        Dibuja el polinomio y resalta los puntos de datos originales, así como
        el punto interpolado `(x, y(x))`.

        Parameters
        ----------
        x : float
            Valor de `x` a interpolar y resaltar en la gráfica.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib.
        """
        y = self.evaluar(x)
        x_min = min(self._x)
        x_max = max(self._x)
        x_list = np.linspace(x_min, x_max, 1000)
        y_list = [self.evaluar(val) for val in x_list]
        plt.scatter(x, y, c='r', lw=2, label='Interpolación Lagrange', zorder=11)
        plt.plot(x_list, y_list, linestyle='dashed', c='k', lw=1, label='Polinomio')
        plt.annotate(f'$({x:.4g}, {y:.4g})$', (x, y), c='r', alpha=0.9, textcoords="offset points",
                     xytext=(0, 10), ha='center')
        super()._graficar_datos()


def main():
    x = np.array([1., 4., 6., 5.])
    y = np.log(x)
    inter = InterpolacionLagrange(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)
    print(inter.obtener_polinomio(expandido=True))


if __name__ == '__main__':
    main()
