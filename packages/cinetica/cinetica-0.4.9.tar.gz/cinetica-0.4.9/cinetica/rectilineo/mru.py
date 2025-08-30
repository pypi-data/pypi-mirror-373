import math

class MovimientoRectilineoUniforme:
    """
    Clase para calcular posición y velocidad en Movimiento Rectilíneo Uniforme (MRU).
    """

    def __init__(self, posicion_inicial: float = 0.0, velocidad_inicial: float = 0.0):
        """
        Inicializa el objeto MovimientoRectilineoUniforme con condiciones iniciales.

        Args:
            posicion_inicial (float): Posición inicial del objeto (m).
            velocidad_inicial (float): Velocidad inicial del objeto (m/s).
        """
        self.posicion_inicial = posicion_inicial
        self.velocidad_inicial = velocidad_inicial

    def posicion(self, tiempo: float) -> float:
        """
        Calcula la posición en MRU.
        Ecuación: x = x0 + v * t

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Posición final (m).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if tiempo < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.posicion_inicial + self.velocidad_inicial * tiempo

    def velocidad(self) -> float:
        """
        Calcula la velocidad en MRU (es constante).
        Ecuación: v = v0

        Returns:
            float: Velocidad (m/s).
        """
        return self.velocidad_inicial
