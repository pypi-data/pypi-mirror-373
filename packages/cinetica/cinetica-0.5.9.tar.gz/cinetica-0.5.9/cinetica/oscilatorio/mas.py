import math

class MovimientoArmonicoSimple:
    """
    Clase para calcular la posición, velocidad y aceleración en un Movimiento Armónico Simple (M.A.S.).
    """

    def __init__(self, amplitud, frecuencia_angular, fase_inicial=0):
        """
        Inicializa el objeto de Movimiento Armónico Simple.

        :param amplitud: Amplitud del movimiento (A).
        :param frecuencia_angular: Frecuencia angular (ω) en radianes/segundo.
        :param fase_inicial: Fase inicial (φ) en radianes. Por defecto es 0.
        """
        if amplitud <= 0:
            raise ValueError("La amplitud debe ser un valor positivo.")
        if frecuencia_angular <= 0:
            raise ValueError("La frecuencia angular debe ser un valor positivo.")

        self.amplitud = amplitud
        self.frecuencia_angular = frecuencia_angular
        self.fase_inicial = fase_inicial

    def posicion(self, tiempo):
        """
        Calcula la posición (x) en un tiempo dado.

        x(t) = A * cos(ωt + φ)

        :param tiempo: Tiempo (t) en segundos.
        :return: Posición en el tiempo dado.
        """
        return self.amplitud * math.cos(self.frecuencia_angular * tiempo + self.fase_inicial)

    def velocidad(self, tiempo):
        """
        Calcula la velocidad (v) en un tiempo dado.

        v(t) = -A * ω * sen(ωt + φ)

        :param tiempo: Tiempo (t) en segundos.
        :return: Velocidad en el tiempo dado.
        """
        return -self.amplitud * self.frecuencia_angular * math.sin(self.frecuencia_angular * tiempo + self.fase_inicial)

    def aceleracion(self, tiempo):
        """
        Calcula la aceleración (a) en un tiempo dado.

        a(t) = -A * ω^2 * cos(ωt + φ) = -ω^2 * x(t)

        :param tiempo: Tiempo (t) en segundos.
        :return: Aceleración en el tiempo dado.
        """
        return -self.amplitud * (self.frecuencia_angular ** 2) * math.cos(self.frecuencia_angular * tiempo + self.fase_inicial)

    def periodo(self):
        """
        Calcula el período (T) del movimiento.

        T = 2π / ω

        :return: Período del movimiento en segundos.
        """
        return 2 * math.pi / self.frecuencia_angular

    def frecuencia(self):
        """
        Calcula la frecuencia (f) del movimiento.

        f = 1 / T = ω / (2π)

        :return: Frecuencia del movimiento en Hertz.
        """
        return self.frecuencia_angular / (2 * math.pi)

    def energia_cinetica(self, tiempo, masa):
        """
        Calcula la energía cinética (Ec) en un tiempo dado.

        Ec = 0.5 * m * v(t)^2

        :param tiempo: Tiempo (t) en segundos.
        :param masa: Masa del objeto en kg.
        :return: Energía cinética en Joules.
        """
        if masa <= 0:
            raise ValueError("La masa debe ser un valor positivo.")
        return 0.5 * masa * (self.velocidad(tiempo) ** 2)

    def energia_potencial(self, tiempo, constante_elastica):
        """
        Calcula la energía potencial elástica (Ep) en un tiempo dado.

        Ep = 0.5 * k * x(t)^2

        :param tiempo: Tiempo (t) en segundos.
        :param constante_elastica: Constante elástica (k) en N/m.
        :return: Energía potencial en Joules.
        """
        if constante_elastica <= 0:
            raise ValueError("La constante elástica debe ser un valor positivo.")
        return 0.5 * constante_elastica * (self.posicion(tiempo) ** 2)

    def energia_total(self, masa, constante_elastica):
        """
        Calcula la energía mecánica total (E) del sistema.

        E = 0.5 * k * A^2 = 0.5 * m * A^2 * ω^2

        :param masa: Masa del objeto en kg.
        :param constante_elastica: Constante elástica (k) en N/m.
        :return: Energía total en Joules.
        """
        if masa <= 0 or constante_elastica <= 0:
            raise ValueError("La masa y la constante elástica deben ser valores positivos.")
        return 0.5 * constante_elastica * (self.amplitud ** 2)
