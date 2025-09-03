import pytest
import numpy as np
from cinetica.oscilatorio import MovimientoArmonicoComplejo

def test_mac_init():
    # Test con componentes válidos
    comp1 = {'amplitud': 1.0, 'frecuencia_angular': 1.0, 'fase_inicial': 0.0}
    comp2 = {'amplitud': 0.5, 'frecuencia_angular': 2.0, 'fase_inicial': np.pi / 2}
    mac = MovimientoArmonicoComplejo([comp1, comp2])
    assert len(mac.mas_components) == 2
    assert mac.mas_components[0]['amplitud'] == 1.0

    # Test con lista vacía
    with pytest.raises(ValueError, match="mas_components debe ser una lista no vacía de diccionarios."):
        MovimientoArmonicoComplejo([])

    # Test con tipo incorrecto para mas_components
    with pytest.raises(ValueError, match="mas_components debe ser una lista no vacía de diccionarios."):
        MovimientoArmonicoComplejo("not a list")

    # Test con componente MAS incompleto
    with pytest.raises(ValueError, match="Cada componente MAS debe tener 'amplitud', 'frecuencia_angular' y 'fase_inicial'."):
        MovimientoArmonicoComplejo([{'amplitud': 1.0, 'frecuencia_angular': 1.0}])

    # Test con valores no numéricos
    with pytest.raises(ValueError, match="Los valores de amplitud, frecuencia_angular y fase_inicial deben ser numéricos."):
        MovimientoArmonicoComplejo([{'amplitud': "1.0", 'frecuencia_angular': 1.0, 'fase_inicial': 0.0}])

def test_mac_posicion():
    # MAS 1: A=1, w=1, phi=0  => x1(t) = 1 * cos(t)
    # MAS 2: A=0.5, w=2, phi=pi/2 => x2(t) = 0.5 * cos(2t + pi/2) = -0.5 * sin(2t)
    # MAC: x(t) = cos(t) - 0.5 * sin(2t)
    comp1 = {'amplitud': 1.0, 'frecuencia_angular': 1.0, 'fase_inicial': 0.0}
    comp2 = {'amplitud': 0.5, 'frecuencia_angular': 2.0, 'fase_inicial': np.pi / 2}
    mac = MovimientoArmonicoComplejo([comp1, comp2])

    # t = 0: x(0) = cos(0) - 0.5 * sin(0) = 1 - 0 = 1
    assert mac.posicion(0) == pytest.approx(1.0)

    # t = pi/2: x(pi/2) = cos(pi/2) - 0.5 * sin(pi) = 0 - 0 = 0
    assert mac.posicion(np.pi / 2) == pytest.approx(0.0)

    # t = pi: x(pi) = cos(pi) - 0.5 * sin(2pi) = -1 - 0 = -1
    assert mac.posicion(np.pi) == pytest.approx(-1.0)

    # Test con array de tiempos
    tiempos = np.array([0, np.pi / 2, np.pi])
    expected_positions = np.array([1.0, 0.0, -1.0])
    assert mac.posicion(tiempos) == pytest.approx(expected_positions)

def test_mac_velocidad():
    # MAS 1: x1(t) = cos(t) => v1(t) = -sin(t)
    # MAS 2: x2(t) = 0.5 * cos(2t + pi/2) => v2(t) = -0.5 * 2 * sin(2t + pi/2) = -sin(2t + pi/2) = -cos(2t)
    # MAC: v(t) = -sin(t) - cos(2t)
    comp1 = {'amplitud': 1.0, 'frecuencia_angular': 1.0, 'fase_inicial': 0.0}
    comp2 = {'amplitud': 0.5, 'frecuencia_angular': 2.0, 'fase_inicial': np.pi / 2}
    mac = MovimientoArmonicoComplejo([comp1, comp2])

    # t = 0: v(0) = -sin(0) - cos(0) = 0 - 1 = -1
    assert mac.velocidad(0) == pytest.approx(-1.0)

    # t = pi/2: v(pi/2) = -sin(pi/2) - cos(pi) = -1 - (-1) = 0
    assert mac.velocidad(np.pi / 2) == pytest.approx(0.0)

    # t = pi: v(pi) = -sin(pi) - cos(2pi) = 0 - 1 = -1
    assert mac.velocidad(np.pi) == pytest.approx(-1.0)

    # Test con array de tiempos
    tiempos = np.array([0, np.pi / 2, np.pi])
    expected_velocities = np.array([-1.0, 0.0, -1.0])
    assert mac.velocidad(tiempos) == pytest.approx(expected_velocities)

def test_mac_aceleracion():
    # MAS 1: v1(t) = -sin(t) => a1(t) = -cos(t)
    # MAS 2: v2(t) = -cos(2t) => a2(t) = -(-2) * sin(2t) = 2 * sin(2t)
    # MAC: a(t) = -cos(t) + 2 * sin(2t)
    comp1 = {'amplitud': 1.0, 'frecuencia_angular': 1.0, 'fase_inicial': 0.0}
    comp2 = {'amplitud': 0.5, 'frecuencia_angular': 2.0, 'fase_inicial': np.pi / 2}
    mac = MovimientoArmonicoComplejo([comp1, comp2])

    # t = 0: a(0) = -cos(0) + 2 * sin(0) = -1 + 0 = -1
    assert mac.aceleracion(0) == pytest.approx(-1.0)

    # t = pi/2: a(pi/2) = -cos(pi/2) + 2 * sin(pi) = 0 + 0 = 0
    assert mac.aceleracion(np.pi / 2) == pytest.approx(0.0)

    # t = pi: a(pi) = -cos(pi) + 2 * sin(2pi) = -(-1) + 0 = 1
    assert mac.aceleracion(np.pi) == pytest.approx(1.0)

    # Test con array de tiempos
    tiempos = np.array([0, np.pi / 2, np.pi])
    expected_accelerations = np.array([-1.0, 0.0, 1.0])
    assert mac.aceleracion(tiempos) == pytest.approx(expected_accelerations)
