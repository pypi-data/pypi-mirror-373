import pytest
from cinetica.parabolico import MovimientoParabolicoBase, MovimientoParabolicoAnalisis
import math

def test_base_init_valid_params():
    mp_base = MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=45)
    assert mp_base.velocidad_inicial == 10.0
    assert mp_base.angulo_radianes == math.radians(45)
    assert mp_base.gravedad == 9.81
    assert mp_base.velocidad_inicial_x == pytest.approx(10.0 * math.cos(math.radians(45)))
    assert mp_base.velocidad_inicial_y == pytest.approx(10.0 * math.sin(math.radians(45)))

def test_base_init_invalid_velocidad_inicial():
    with pytest.raises(ValueError, match="La velocidad inicial no puede ser negativa."):
        MovimientoParabolicoBase(velocidad_inicial=-10.0, angulo_grados=45)

def test_base_init_invalid_angulo():
    with pytest.raises(ValueError, match="El ángulo de lanzamiento debe estar entre 0 y 90 grados."):
        MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=100)
    with pytest.raises(ValueError, match="El ángulo de lanzamiento debe estar entre 0 y 90 grados."):
        MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=-10)

def test_base_init_invalid_gravedad():
    with pytest.raises(ValueError, match="La gravedad debe ser un valor positivo."):
        MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=45, gravedad=0)
    with pytest.raises(ValueError, match="La gravedad debe ser un valor positivo."):
        MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=45, gravedad=-5)

def test_base_posicion():
    mp_base = MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=30, gravedad=10.0) # Usar g=10 para cálculos más simples
    # x = v0x * t
    # y = v0y * t - 0.5 * g * t^2
    # v0x = 10 * cos(30) = 10 * 0.866 = 8.66
    # v0y = 10 * sin(30) = 10 * 0.5 = 5
    # t = 1s
    # x = 8.66 * 1 = 8.66
    # y = 5 * 1 - 0.5 * 10 * 1^2 = 5 - 5 = 0
    pos_x, pos_y = mp_base.posicion(tiempo=1.0)
    assert pos_x == pytest.approx(8.660254037844387)
    assert pos_y == pytest.approx(0.0)

    # t = 0s
    pos_x_0, pos_y_0 = mp_base.posicion(tiempo=0.0)
    assert pos_x_0 == pytest.approx(0.0)
    assert pos_y_0 == pytest.approx(0.0)

def test_base_posicion_invalid_tiempo():
    mp_base = MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=45)
    with pytest.raises(ValueError, match="El tiempo no puede ser negativo."):
        mp_base.posicion(tiempo=-1.0)

def test_base_velocidad():
    mp_base = MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=30, gravedad=10.0) # Usar g=10
    # vx = v0x = 8.66
    # vy = v0y - g * t = 5 - 10 * 1 = -5
    vel_x, vel_y = mp_base.velocidad(tiempo=1.0)
    assert vel_x == pytest.approx(8.660254037844387)
    assert vel_y == pytest.approx(-5.0)

    # t = 0s
    vel_x_0, vel_y_0 = mp_base.velocidad(tiempo=0.0)
    assert vel_x_0 == pytest.approx(8.660254037844387)
    assert vel_y_0 == pytest.approx(5.0)

def test_base_velocidad_invalid_tiempo():
    mp_base = MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=45)
    with pytest.raises(ValueError, match="El tiempo no puede ser negativo."):
        mp_base.velocidad(tiempo=-1.0)

def test_analisis_tiempo_vuelo():
    mp_base = MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=30, gravedad=10.0) # Usar g=10
    mp_analisis = MovimientoParabolicoAnalisis(mp_base)
    # T = 2 * v0y / g = 2 * 5 / 10 = 1
    assert mp_analisis.tiempo_vuelo() == pytest.approx(1.0)

    mp_base_horizontal = MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=0, gravedad=10.0)
    mp_analisis_horizontal = MovimientoParabolicoAnalisis(mp_base_horizontal)
    assert mp_analisis_horizontal.tiempo_vuelo() == pytest.approx(0.0)

def test_analisis_altura_maxima():
    mp_base = MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=30, gravedad=10.0) # Usar g=10
    mp_analisis = MovimientoParabolicoAnalisis(mp_base)
    # H = v0y^2 / (2 * g) = 5^2 / (2 * 10) = 25 / 20 = 1.25
    assert mp_analisis.altura_maxima() == pytest.approx(1.25)

    mp_base_horizontal = MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=0, gravedad=10.0)
    mp_analisis_horizontal = MovimientoParabolicoAnalisis(mp_base_horizontal)
    assert mp_analisis_horizontal.altura_maxima() == pytest.approx(0.0)

def test_analisis_alcance_maximo():
    mp_base = MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=30, gravedad=10.0) # Usar g=10
    mp_analisis = MovimientoParabolicoAnalisis(mp_base)
    # R = v0x * T = 8.66 * 1 = 8.66
    assert mp_analisis.alcance_maximo() == pytest.approx(8.660254037844387)

    mp_base_horizontal = MovimientoParabolicoBase(velocidad_inicial=10.0, angulo_grados=0, gravedad=10.0)
    mp_analisis_horizontal = MovimientoParabolicoAnalisis(mp_base_horizontal)
    assert mp_analisis_horizontal.alcance_maximo() == pytest.approx(0.0)
