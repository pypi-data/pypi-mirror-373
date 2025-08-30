import math

class MovimientoCircularUniformementeVariado:
    """
    Clase para calcular y simular Movimiento Circular Uniformemente Variado (MCUV).
    """

    def __init__(self, radio: float, posicion_angular_inicial: float = 0.0, velocidad_angular_inicial: float = 0.0, aceleracion_angular_inicial: float = 0.0):
        """
        Inicializa el objeto MovimientoCircularUniformementeVariado con las condiciones iniciales.

        Args:
            radio (float): Radio de la trayectoria circular (m).
            posicion_angular_inicial (float): Posición angular inicial (radianes).
            velocidad_angular_inicial (float): Velocidad angular inicial (rad/s).
            aceleracion_angular_inicial (float): Aceleración angular inicial (rad/s^2).
        
        Raises:
            ValueError: Si el radio es menor o igual a cero.
        """
        if radio <= 0:
            raise ValueError("El radio debe ser un valor positivo.")

        self.radio = radio
        self.posicion_angular_inicial = posicion_angular_inicial
        self.velocidad_angular_inicial = velocidad_angular_inicial
        self.aceleracion_angular_inicial = aceleracion_angular_inicial

    def posicion_angular(self, tiempo: float) -> float:
        """
        Calcula la posición angular en MCUV.
        Ecuación: theta = theta0 + omega0 * t + 0.5 * alpha * t^2

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Posición angular final (radianes).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if tiempo < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.posicion_angular_inicial + self.velocidad_angular_inicial * tiempo + 0.5 * self.aceleracion_angular_inicial * (tiempo ** 2)

    def velocidad_angular(self, tiempo: float) -> float:
        """
        Calcula la velocidad angular en MCUV.
        Ecuación: omega = omega0 + alpha * t

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Velocidad angular final (rad/s).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if tiempo < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.velocidad_angular_inicial + self.aceleracion_angular_inicial * tiempo

    def aceleracion_angular(self) -> float:
        """
        Calcula la aceleración angular en MCUV (es constante).
        Ecuación: alpha = alpha0

        Returns:
            float: Aceleración angular (rad/s^2).
        """
        return self.aceleracion_angular_inicial

    def velocidad_tangencial(self, tiempo: float) -> float:
        """
        Calcula la velocidad tangencial en MCUV.
        Ecuación: v = omega * R

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Velocidad tangencial (m/s).
        """
        return self.velocidad_angular(tiempo) * self.radio

    def aceleracion_tangencial(self) -> float:
        """
        Calcula la aceleración tangencial en MCUV.
        Ecuación: at = alpha * R

        Returns:
            float: Aceleración tangencial (m/s^2).
        """
        return self.aceleracion_angular_inicial * self.radio

    def aceleracion_centripeta(self, tiempo: float) -> float:
        """
        Calcula la aceleración centrípeta en MCUV.
        Ecuación: ac = omega^2 * R

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Aceleración centrípeta (m/s^2).
        """
        return (self.velocidad_angular(tiempo) ** 2) * self.radio

    def aceleracion_total(self, tiempo: float) -> float:
        """
        Calcula la magnitud de la aceleración total en MCUV.
        Ecuación: a_total = sqrt(at^2 + ac^2)

        Args:
            tiempo (float): Tiempo transcurrido (s).

        Returns:
            float: Magnitud de la aceleración total (m/s^2).
        """
        at = self.aceleracion_tangencial()
        ac = self.aceleracion_centripeta(tiempo)
        return math.sqrt(at**2 + ac**2)

    def velocidad_angular_sin_tiempo(self, posicion_angular_final: float) -> float:
        """
        Calcula la velocidad angular final en MCUV sin conocer el tiempo.
        Ecuación: omega_f^2 = omega_0^2 + 2 * alpha * (theta_f - theta_0)

        Args:
            posicion_angular_final (float): Posición angular final (radianes).

        Returns:
            float: Velocidad angular final (rad/s).
        
        Raises:
            ValueError: Si la velocidad angular al cuadrado es negativa, indicando una situación físicamente imposible.
        """
        delta_theta = posicion_angular_final - self.posicion_angular_inicial
        omega_squared = (self.velocidad_angular_inicial ** 2) + 2 * self.aceleracion_angular_inicial * delta_theta
        if omega_squared < 0:
            raise ValueError("No se puede calcular la velocidad angular real (velocidad angular al cuadrado negativa).")
        return math.sqrt(omega_squared)

    def tiempo_por_posicion_angular(self, posicion_angular_final: float) -> tuple[float, float]:
        """
        Calcula el tiempo a partir de la posición angular final en MCUV, resolviendo la ecuación cuadrática.
        Ecuación: theta_f = theta0 + omega0 * t + 0.5 * alpha * t^2  =>  0.5 * alpha * t^2 + omega0 * t + (theta0 - theta_f) = 0

        Args:
            posicion_angular_final (float): Posición angular final del objeto (radianes).

        Returns:
            tuple[float, float]: Una tupla con los dos posibles valores de tiempo (s).
                                 Si solo hay una solución válida, el segundo valor será `math.nan`.
                                 Si no hay soluciones reales, ambos valores serán `math.nan`.
        
        Raises:
            ValueError: Si la aceleración angular es cero y la velocidad angular inicial también es cero,
                        o si el discriminante es negativo (no hay soluciones reales).
        """
        a = 0.5 * self.aceleracion_angular_inicial
        b = self.velocidad_angular_inicial
        c = self.posicion_angular_inicial - posicion_angular_final

        if a == 0:  # Caso de MCU
            if b == 0:
                if c == 0:
                    # Infinitas soluciones (objeto ya en posicion_angular_final y estacionario)
                    return (math.inf, math.nan)
                else:
                    # No hay solución (objeto nunca alcanzará posicion_angular_final)
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

    def tiempo_por_velocidad_angular(self, velocidad_angular_final: float) -> float:
        """
        Calcula el tiempo a partir de la velocidad angular final en MCUV.
        Ecuación: omega_f = omega_0 + alpha * t  =>  t = (omega_f - omega_0) / alpha

        Args:
            velocidad_angular_final (float): Velocidad angular final del objeto (rad/s).

        Returns:
            float: Tiempo transcurrido (s).
        
        Raises:
            ValueError: Si la aceleración angular es cero y la velocidad angular final no coincide con la inicial,
                        o si el tiempo calculado es negativo.
        """
        if self.aceleracion_angular_inicial == 0:
            if velocidad_angular_final != self.velocidad_angular_inicial:
                raise ValueError("La aceleración angular es cero, por lo que la velocidad angular no puede cambiar.")
            return math.inf # Velocidad angular constante, tiempo infinito para alcanzar la misma velocidad si ya la tiene
        
        tiempo = (velocidad_angular_final - self.velocidad_angular_inicial) / self.aceleracion_angular_inicial
        if tiempo < 0:
            raise ValueError("El tiempo calculado es negativo, lo cual no es físicamente posible.")
        return tiempo
