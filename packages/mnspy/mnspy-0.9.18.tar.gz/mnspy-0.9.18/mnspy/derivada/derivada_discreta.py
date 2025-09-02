import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class DerivadaDiscreta:
    """Calcula la derivada numérica a partir de un conjunto de puntos discretos.

    Attributes
    ----------
    x : ndarray
        Array con los datos de la variable independiente.
    y : ndarray
        Array con los datos de la variable dependiente.
    modo : str
        Método de diferencia finita utilizado.
    derivada: ndarray
        Array con los valores de la derivada calculada.

    Methods
    -------
    _derivar():
        Calcula la derivada para el conjunto de puntos.
    graficar():
        Grafica los datos y la derivada resultante para esos puntos

    Examples
    -------
    from mnspy import DerivadaDiscreta
    import numpy as np

    t = np.array(
        [4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.2, 5.4, 5.6, 5.8, 6.0, 6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4, 7.6, 7.8, 8.0])
    x = np.array(
        [-5.87, -4.23, -2.55, -0.89, 0.67, 2.09, 3.31, 4.31, 5.06, 5.55, 5.78, 5.77, 5.52, 5.08, 4.46, 3.72, 2.88, 2.00,
         1.10, 0.23, -0.59])
    vel = DerivadaDiscreta(t, x, modo='centrada')
    vel.graficar('Derivada x contra t', '$t$', '$x$', '$v$')
    print(vel.derivada)
    """

    def __init__(self, x: np.array, y: np.array, modo: str = 'centrada'):
        """Constructor de la clase DerivadaDiscreta.

        Parameters
        ----------
        x : np.ndarray
            Array con los datos de la variable independiente
        y : np.ndarray
            Array con los datos de la variable dependiente
        modo : str, optional
            Tipo de derivada que se realizará. Opciones:
            - ``'adelante'``: Diferencias finitas hacia adelante. El último punto usa una diferencia hacia atrás.
            - ``'atrás'``: Diferencias finitas hacia atrás. El primer punto usa una diferencia hacia adelante.
            - ``'centrada'``: Diferencias finitas centradas (por defecto). Los puntos extremos usan diferencias hacia adelante/atrás.
        """
        self._x = x
        self._y = y
        self._modo = modo
        self.derivada = None
        self._derivar()
        plt.ioff()  # deshabilitada interactividad matplotlib

    def _derivar(self):
        """Calcula la derivada del conjunto de datos.

        El resultado se almacena en el atributo `self.derivada`.
        en el atributo derivada.
        """
        n = len(self._x)
        self.derivada = np.zeros(n)

        if self._modo == 'adelante':
            # Diferencias hacia adelante para todos menos el último
            self.derivada[:-1] = (self._y[1:] - self._y[:-1]) / (self._x[1:] - self._x[:-1])
            # Diferencia hacia atrás para el último punto
            self.derivada[-1] = (self._y[-1] - self._y[-2]) / (self._x[-1] - self._x[-2])

        elif self._modo == 'atrás':
            # Diferencia hacia adelante para el primer punto
            self.derivada[0] = (self._y[1] - self._y[0]) / (self._x[1] - self._x[0])
            # Diferencias hacia atrás para el resto
            self.derivada[1:] = (self._y[1:] - self._y[:-1]) / (self._x[1:] - self._x[:-1])

        elif self._modo == 'centrada':
            # Primer y último punto usan diferencias no centradas
            self.derivada[0] = (self._y[1] - self._y[0]) / (self._x[1] - self._x[0])
            self.derivada[-1] = (self._y[-1] - self._y[-2]) / (self._x[-1] - self._x[-2])
            # Puntos intermedios usan diferencias centradas
            self.derivada[1:-1] = (self._y[2:] - self._y[:-2]) / (self._x[2:] - self._x[:-2])
        else:
            raise ValueError(f"Modo de derivada '{self._modo}' no es válido. Opciones: 'adelante', 'atrás', 'centrada'.")

    def graficar(self, label_tit: str = '', label_x: str = '', label_y: str = '', label_der: str = '') -> None:
        """Grafica los datos originales y su derivada.

        Parameters
        ----------
        label_tit: str
            Título asignado a la gráfica
        label_x: str
            Título asignado al eje x
        label_y: str
            Título asignado al eje y de la función
        label_der: str
            Título asignado al eje y de la derivada.

        Returns
        -------
        None
            Muestra una gráfica de Matplotlib con dos subplots.
        """
        fig, axs = plt.subplots(2, 1, sharex=True, figsize=(10, 8))
        axs[0].plot(self._x, self._y, 'o-', c='b', lw=2, label='Función')
        axs[0].set_ylabel(label_y)
        axs[0].title.set_text('Datos')
        axs[0].legend()
        axs[0].grid()
        axs[1].plot(self._x, self.derivada, 'o-', c='r', lw=2, label='Derivada')
        axs[1].set_ylabel(label_der)
        axs[1].set_xlabel(label_x)
        axs[1].title.set_text('Derivada modo =  ' + self._modo)
        axs[1].legend()
        axs[1].grid()
        fig.suptitle(label_tit)
        plt.show()

def main():
    """Función principal para demostración."""
    t = np.array(
        [4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.2, 5.4, 5.6, 5.8, 6.0, 6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4, 7.6, 7.8, 8.0])
    x = np.array(
        [-5.87, -4.23, -2.55, -0.89, 0.67, 2.09, 3.31, 4.31, 5.06, 5.55, 5.78, 5.77, 5.52, 5.08, 4.46, 3.72, 2.88, 2.00,
         1.10, 0.23, -0.59])
    vel = DerivadaDiscreta(t, x, modo='centrada')
    vel.graficar('Derivada x contra t', '$t$', '$x$', '$v$')
    print(vel.derivada)


if __name__ == '__main__':
    main()