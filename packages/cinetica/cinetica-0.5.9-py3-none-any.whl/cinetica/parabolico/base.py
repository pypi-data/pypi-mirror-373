import math

class MovimientoParabolicoBase:
    """
    Clase base para simular trayectorias en Movimiento Parabólico.
    Se asume que el lanzamiento se realiza desde el origen (0,0) y la gravedad actúa hacia abajo.
    """

    def __init__(self, velocidad_inicial: float, angulo_grados: float, gravedad: float = 9.81):
        """
        Inicializa el objeto MovimientoParabolicoBase con las condiciones iniciales.

        Args:
            velocidad_inicial (float): Magnitud de la velocidad inicial (m/s).
            angulo_grados (float): Ángulo de lanzamiento con respecto a la horizontal (grados).
            gravedad (float): Aceleración debido a la gravedad (m/s^2).
        
        Raises:
            ValueError: Si la velocidad inicial es negativa, el ángulo no está entre 0 y 90 grados, o la gravedad es menor o igual a cero.
        """
        if velocidad_inicial < 0:
            raise ValueError("La velocidad inicial no puede ser negativa.")
        if not (0 <= angulo_grados <= 90):
            raise ValueError("El ángulo de lanzamiento debe estar entre 0 y 90 grados.")
        if gravedad <= 0:
            raise ValueError("La gravedad debe ser un valor positivo.")

        self.velocidad_inicial = velocidad_inicial
        self.angulo_radianes = math.radians(angulo_grados)
        self.gravedad = gravedad

        self.velocidad_inicial_x = self.velocidad_inicial * math.cos(self.angulo_radianes)
        self.velocidad_inicial_y = self.velocidad_inicial * math.sin(self.angulo_radianes)

    def posicion(self, tiempo: float) -> tuple[float, float]:
        """
        Calcula la posición (x, y) del proyectil en un tiempo dado.

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            tuple: Una tupla (x, y) con las coordenadas de la posición (m).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if tiempo < 0:
            raise ValueError("El tiempo no puede ser negativo.")

        posicion_x = self.velocidad_inicial_x * tiempo
        posicion_y = (self.velocidad_inicial_y * tiempo) - (0.5 * self.gravedad * (tiempo ** 2))
        return (posicion_x, posicion_y)

    def velocidad(self, tiempo: float) -> tuple[float, float]:
        """
        Calcula la velocidad (vx, vy) del proyectil en un tiempo dado.

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            tuple: Una tupla (vx, vy) con las componentes de la velocidad (m/s).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if tiempo < 0:
            raise ValueError("El tiempo no puede ser negativo.")

        velocidad_x = self.velocidad_inicial_x
        velocidad_y = self.velocidad_inicial_y - (self.gravedad * tiempo)
        return (velocidad_x, velocidad_y)
