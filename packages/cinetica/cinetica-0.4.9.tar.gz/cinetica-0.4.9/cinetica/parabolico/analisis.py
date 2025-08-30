import math
from .base import MovimientoParabolicoBase

class MovimientoParabolicoAnalisis:
    """
    Clase para calcular propiedades de análisis en Movimiento Parabólico,
    como tiempo de vuelo, altura máxima y alcance máximo.
    """

    def __init__(self, base_movimiento: MovimientoParabolicoBase):
        """
        Inicializa el objeto MovimientoParabolicoAnalisis con una instancia de MovimientoParabolicoBase.

        Args:
            base_movimiento (MovimientoParabolicoBase): Instancia de la clase base de movimiento parabólico.
        """
        self.base_movimiento = base_movimiento

    def tiempo_vuelo(self) -> float:
        """
        Calcula el tiempo total de vuelo del proyectil hasta que regresa a la altura inicial (y=0).

        Returns:
            float: Tiempo total de vuelo (s).
        
        Notes:
            Retorna `0.0` si el ángulo de lanzamiento es 0 grados.
        """
        if self.base_movimiento.angulo_radianes == 0: # Si el ángulo es 0, no hay tiempo de vuelo vertical
            return 0.0
        return (2 * self.base_movimiento.velocidad_inicial_y) / self.base_movimiento.gravedad

    def altura_maxima(self) -> float:
        """
        Calcula la altura máxima alcanzada por el proyectil.

        Returns:
            float: Altura máxima (m).
        
        Notes:
            Retorna `0.0` si el ángulo de lanzamiento es 0 grados.
        """
        if self.base_movimiento.angulo_radianes == 0: # Si el ángulo es 0, la altura máxima es 0
            return 0.0
        return (self.base_movimiento.velocidad_inicial_y ** 2) / (2 * self.base_movimiento.gravedad)

    def alcance_maximo(self) -> float:
        """
        Calcula el alcance horizontal máximo del proyectil (cuando y=0).

        Returns:
            float: Alcance horizontal máximo (m).
        """
        tiempo_total = self.tiempo_vuelo()
        return self.base_movimiento.velocidad_inicial_x * tiempo_total
