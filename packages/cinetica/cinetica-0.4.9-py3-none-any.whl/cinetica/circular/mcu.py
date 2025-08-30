import math

class MovimientoCircularUniforme:
    """
    Clase para calcular y simular Movimiento Circular Uniforme (MCU).
    """

    def __init__(self, radio: float, posicion_angular_inicial: float = 0.0, velocidad_angular_inicial: float = 0.0):
        """
        Inicializa el objeto MovimientoCircularUniforme con las condiciones iniciales.

        Args:
            radio (float): Radio de la trayectoria circular (m).
            posicion_angular_inicial (float): Posición angular inicial (radianes).
            velocidad_angular_inicial (float): Velocidad angular inicial (rad/s).
        
        Raises:
            ValueError: Si el radio es menor o igual a cero.
        """
        if radio <= 0:
            raise ValueError("El radio debe ser un valor positivo.")

        self.radio = radio
        self.posicion_angular_inicial = posicion_angular_inicial
        self.velocidad_angular_inicial = velocidad_angular_inicial

    def posicion_angular(self, tiempo: float) -> float:
        """
        Calcula la posición angular en MCU.
        Ecuación: theta = theta0 + omega * t

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Posición angular final (radianes).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if tiempo < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.posicion_angular_inicial + self.velocidad_angular_inicial * tiempo

    def velocidad_angular(self) -> float:
        """
        Calcula la velocidad angular en MCU (es constante).
        Ecuación: omega = omega0

        Returns:
            float: Velocidad angular (rad/s).
        """
        return self.velocidad_angular_inicial

    def velocidad_tangencial(self) -> float:
        """
        Calcula la velocidad tangencial en MCU.
        Ecuación: v = omega * R

        Returns:
            float: Velocidad tangencial (m/s).
        """
        return self.velocidad_angular() * self.radio

    def aceleracion_centripeta(self) -> float:
        """
        Calcula la aceleración centrípeta en MCU.
        Ecuación: ac = omega^2 * R = v^2 / R

        Returns:
            float: Aceleración centrípeta (m/s^2).
        """
        return (self.velocidad_angular() ** 2) * self.radio

    def periodo(self) -> float:
        """
        Calcula el período en MCU.
        Ecuación: T = 2 * pi / omega

        Returns:
            float: Período (s).
        
        Notes:
            Retorna `math.inf` si la velocidad angular inicial es cero.
        """
        if self.velocidad_angular_inicial == 0:
            return math.inf  # Período infinito si la velocidad angular es cero
        return (2 * math.pi) / self.velocidad_angular_inicial

    def frecuencia(self) -> float:
        """
        Calcula la frecuencia en MCU.
        Ecuación: f = 1 / T = omega / (2 * pi)

        Returns:
            float: Frecuencia (Hz).
        
        Notes:
            Retorna `0.0` si la velocidad angular inicial es cero.
        """
        if self.velocidad_angular_inicial == 0:
            return 0.0  # Frecuencia cero si la velocidad angular es cero
        return self.velocidad_angular_inicial / (2 * math.pi)
