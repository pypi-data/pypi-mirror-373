import math

class MovimientoRectilineoUniformementeVariado:
    """
    Clase para calcular posición, velocidad y aceleración en Movimiento Rectilíneo Uniformemente Variado (MRUV).
    """

    def __init__(self, posicion_inicial: float = 0.0, velocidad_inicial: float = 0.0, aceleracion_inicial: float = 0.0):
        """
        Inicializa el objeto MovimientoRectilineoUniformementeVariado con condiciones iniciales.

        Args:
            posicion_inicial (float): Posición inicial del objeto (m).
            velocidad_inicial (float): Velocidad inicial del objeto (m/s).
            aceleracion_inicial (float): Aceleración inicial del objeto (m/s^2).
        """
        self.posicion_inicial = posicion_inicial
        self.velocidad_inicial = velocidad_inicial
        self.aceleracion_inicial = aceleracion_inicial

    def posicion(self, tiempo: float) -> float:
        """
        Calcula la posición en MRUV.
        Ecuación: x = x0 + v0 * t + 0.5 * a * t^2

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Posición final (m).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if tiempo < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.posicion_inicial + self.velocidad_inicial * tiempo + 0.5 * self.aceleracion_inicial * (tiempo ** 2)

    def velocidad(self, tiempo: float) -> float:
        """
        Calcula la velocidad en MRUV.
        Ecuación: v = v0 + a * t

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Velocidad final (m/s).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if tiempo < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.velocidad_inicial + self.aceleracion_inicial * tiempo

    def aceleracion(self) -> float:
        """
        Calcula la aceleración en MRUV (es constante).
        Ecuación: a = a0

        Returns:
            float: Aceleración (m/s^2).
        """
        return self.aceleracion_inicial

    def velocidad_sin_tiempo(self, posicion_final: float) -> float:
        """
        Calcula la velocidad final en MRUV sin conocer el tiempo.
        Ecuación: v^2 = v0^2 + 2 * a * (x - x0)

        Args:
            posicion_final (float): Posición final del objeto (m).

        Returns:
            float: Velocidad final (m/s).
        
        Raises:
            ValueError: Si la velocidad al cuadrado es negativa, indicando una situación físicamente imposible.
        """
        delta_x = posicion_final - self.posicion_inicial
        v_squared = (self.velocidad_inicial ** 2) + 2 * self.aceleracion_inicial * delta_x
        if v_squared < 0:
            raise ValueError("No se puede calcular la velocidad real (velocidad al cuadrado negativa).")
        return math.sqrt(v_squared)

    def tiempo_por_posicion(self, posicion_final: float) -> tuple[float, float]:
        """
        Calcula el tiempo a partir de la posición final en MRUV, resolviendo la ecuación cuadrática.
        Ecuación: x = x0 + v0 * t + 0.5 * a * t^2  =>  0.5 * a * t^2 + v0 * t + (x0 - x_f) = 0

        Args:
            posicion_final (float): Posición final del objeto (m).

        Returns:
            tuple[float, float]: Una tupla con los dos posibles valores de tiempo (s).
                                 Si solo hay una solución válida, el segundo valor será `math.nan`.
                                 Si no hay soluciones reales, ambos valores serán `math.nan`.
        
        Raises:
            ValueError: Si la aceleración es cero y la velocidad inicial también es cero,
                        o si el discriminante es negativo (no hay soluciones reales).
        """
        a = 0.5 * self.aceleracion_inicial
        b = self.velocidad_inicial
        c = self.posicion_inicial - posicion_final

        if a == 0:  # Caso de MRU
            if b == 0:
                if c == 0:
                    # Infinitas soluciones (objeto ya en posicion_final y estacionario)
                    return (math.inf, math.nan)
                else:
                    # No hay solución (objeto nunca alcanzará posicion_final)
                    return (math.nan, math.nan)
            else:
                # Ecuación lineal: t = -c / b
                tiempo = -c / b
                if tiempo < 0:
                    raise ValueError("El tiempo calculado es negativo, lo cual no es físicamente posible.")
                return (tiempo, math.nan)

        discriminante = b**2 - 4 * a * c

        if discriminante < 0:
            return (math.nan, math.nan)  # No hay soluciones reales
        elif discriminante == 0:
            tiempo = (-b) / (2 * a)
            if tiempo < 0:
                raise ValueError("El tiempo calculado es negativo, lo cual no es físicamente posible.")
            return (tiempo, math.nan)
        else:
            tiempo1 = (-b + math.sqrt(discriminante)) / (2 * a)
            tiempo2 = (-b - math.sqrt(discriminante)) / (2 * a)
            
            valid_times = []
            if tiempo1 >= 0:
                valid_times.append(tiempo1)
            if tiempo2 >= 0:
                valid_times.append(tiempo2)
            
            if not valid_times:
                raise ValueError("Ambos tiempos calculados son negativos, lo cual no es físicamente posible.")
            elif len(valid_times) == 1:
                return (valid_times[0], math.nan)
            else:
                return (min(valid_times), max(valid_times))

    def tiempo_por_velocidad(self, velocidad_final: float) -> float:
        """
        Calcula el tiempo a partir de la velocidad final en MRUV.
        Ecuación: v = v0 + a * t  =>  t = (v - v0) / a

        Args:
            velocidad_final (float): Velocidad final del objeto (m/s).

        Returns:
            float: Tiempo transcurrido (s).
        
        Raises:
            ValueError: Si la aceleración es cero y la velocidad final no coincide con la inicial,
                        o si el tiempo calculado es negativo.
        """
        if self.aceleracion_inicial == 0:
            if velocidad_final != self.velocidad_inicial:
                raise ValueError("La aceleración es cero, por lo que la velocidad no puede cambiar.")
            return math.inf # Velocidad constante, tiempo infinito para alcanzar la misma velocidad si ya la tiene
        
        tiempo = (velocidad_final - self.velocidad_inicial) / self.aceleracion_inicial
        if tiempo < 0:
            raise ValueError("El tiempo calculado es negativo, lo cual no es físicamente posible.")
        return tiempo

    def desplazamiento_sin_tiempo(self, velocidad_final: float) -> float:
        """
        Calcula el desplazamiento (delta_x) en MRUV sin conocer el tiempo.
        Ecuación: v_f^2 = v_0^2 + 2 * a * delta_x  =>  delta_x = (v_f^2 - v_0^2) / (2 * a)

        Args:
            velocidad_final (float): Velocidad final del objeto (m/s).

        Returns:
            float: Desplazamiento (m).
        
        Raises:
            ValueError: Si la aceleración es cero y la velocidad final es diferente de la inicial,
                        o si el denominador es cero.
        """
        if self.aceleracion_inicial == 0:
            if velocidad_final != self.velocidad_inicial:
                raise ValueError("La aceleración es cero, por lo que la velocidad no puede cambiar y el desplazamiento es indefinido si las velocidades son diferentes.")
            return 0.0 # Si la aceleración es cero y las velocidades son iguales, el desplazamiento es 0 (o indefinido si no se mueve)
        
        denominador = 2 * self.aceleracion_inicial
        if denominador == 0:
            raise ValueError("El denominador es cero, no se puede calcular el desplazamiento.")
        
        delta_x = (velocidad_final**2 - self.velocidad_inicial**2) / denominador
        return delta_x
