from mnspy.integrales import Integral
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class CuadraturaAdaptativa(Integral):
    """Clase para la implementación de la integral por el método de Cuadratura Adaptativa

    Attributes
    ----------
    f: callable
        Función a integrar.
    a: float
        Límite inferior de integración.
    b: float
        Límite superior de integración.
    integral : float
        Resultado del cálculo de la integral.

    Methods
    -------
    graficar()
        Genera una gráfica del proceso de integración.

    Examples
    -------
    from mnspy import CuadraturaAdaptativa

    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    gl = CuadraturaAdaptativa(g, 0, 0.8)
    gl.graficar()
    print(gl.integral)
    """
    def __init__(self, f: callable, a: float, b: float, tol: float = 1.e-8):
        """Constructor de la clase CuadraturaAdaptativa

        Parameters
        ----------
        f: callable
            Función a integrar, f(x).
        a: float
            Límite inferior de integración.
        b: float
            Límite superior de integración.
        tol: float
            Tolerancia de error permitida para la convergencia.
        """
        super().__init__(f=f, a=a, b=b)
        self._puntos = set()
        self._tol = tol
        f_a = self._f(self._a)
        f_c = self._f(0.5 * (self._a + self._b))
        f_b = self._f(self._b)
        self.integral = self._iterar(self._a, self._b, f_a, f_c, f_b)

    def _iterar(self, a, b, f_a, f_c, f_b) -> float:
        """Proceso recursivo para el cálculo de la integral con cuadratura adaptativa.

        El método divide el intervalo de integración si el error estimado
        supera la tolerancia, aplicando la regla de Simpson de forma recursiva.

        Parameters
        ----------
        a : float
            Límite inferior del subintervalo actual.
        b : float
            Límite superior del subintervalo actual.
        f_a : float
            Valor de la función en `a`, f(a).
        f_c : float
            Valor de la función en el punto medio, f((a+b)/2).
        f_b : float
            Valor de la función en `b`, f(b).

        Returns
        -------
        float
            Valor de la integral en el subintervalo.
        """
        h = b - a
        c = 0.5 * (a + b)
        f_d = self._f(0.5 * (a + c))
        f_e = self._f(0.5 * (c + b))
        q_1 = h / 6 * (f_a + 4 * f_c + f_b)
        q_2 = h / 12 * (f_a + 4 * f_d + 2 * f_c + 4 * f_e + f_b)
        self._puntos.update({a})
        self._puntos.update({c})
        self._puntos.update({b})
        self._puntos.update({0.5 * (a + c)})
        self._puntos.update({0.5 * (c + b)})
        if abs(q_1 - q_2) < self._tol:
            q = q_2 + (q_2 - q_1) / 15
        else:
            q_a = self._iterar(a, c, f_a, f_d, f_c)
            q_b = self._iterar(c, b, f_c, f_e, f_b)
            q = q_a + q_b
        return q

    def graficar(self):
        """Genera una gráfica del proceso de integración.

        Muestra la función y resalta los puntos evaluados por el algoritmo
        adaptativo.
        """
        x = list(self._puntos)
        y = list((self._f(x_i) for x_i in x))
        plt.stem(x, y, linefmt='C2--', markerfmt='C0o', basefmt='C2-', label='Cuadratura Adaptativa')
        plt.title(r'$\int{f(x)}\approx ' + str(self.integral) + '$')
        self._graficar_datos()


def main():
    """Función principal para demostración."""
    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    gl = CuadraturaAdaptativa(g, 0, 0.8)
    gl.graficar()
    print(gl.integral)


if __name__ == '__main__':
    main()
