import pytest
import numpy as np
from cinetica.relativo import MovimientoRelativo

def test_velocidad_relativa_2d():
    mr = MovimientoRelativo()
    v_a = [10, 0]
    v_b = [2, 0]
    v_rel = mr.velocidad_relativa(v_a, v_b)
    assert np.array_equal(v_rel, [8, 0])

    v_a = [10, 5]
    v_b = [2, 3]
    v_rel = mr.velocidad_relativa(v_a, v_b)
    assert np.array_equal(v_rel, [8, 2])

    v_a = [0, 10]
    v_b = [0, 15]
    v_rel = mr.velocidad_relativa(v_a, v_b)
    assert np.array_equal(v_rel, [0, -5])

def test_velocidad_relativa_3d():
    mr = MovimientoRelativo()
    v_a = [10, 5, 3]
    v_b = [2, 1, 1]
    v_rel = mr.velocidad_relativa(v_a, v_b)
    assert np.array_equal(v_rel, [8, 4, 2])

def test_velocidad_relativa_dimension_mismatch():
    mr = MovimientoRelativo()
    v_a = [10, 0]
    v_b = [2, 0, 0]
    with pytest.raises(ValueError):
        mr.velocidad_relativa(v_a, v_b)

def test_velocidad_absoluta_a():
    mr = MovimientoRelativo()
    v_rel_ab = [8, 0]
    v_b = [2, 0]
    v_a = mr.velocidad_absoluta_a(v_rel_ab, v_b)
    assert np.array_equal(v_a, [10, 0])

    v_rel_ab = [8, 2, 1]
    v_b = [2, 3, 2]
    v_a = mr.velocidad_absoluta_a(v_rel_ab, v_b)
    assert np.array_equal(v_a, [10, 5, 3])

def test_velocidad_absoluta_b():
    mr = MovimientoRelativo()
    v_a = [10, 0]
    v_rel_ab = [8, 0]
    v_b = mr.velocidad_absoluta_b(v_a, v_rel_ab)
    assert np.array_equal(v_b, [2, 0])

    v_a = [10, 5, 3]
    v_rel_ab = [8, 2, 1]
    v_b = mr.velocidad_absoluta_b(v_a, v_rel_ab)
    assert np.array_equal(v_b, [2, 3, 2])

def test_magnitud_velocidad():
    mr = MovimientoRelativo()
    v = [3, 4]
    assert mr.magnitud_velocidad(v) == pytest.approx(5.0)

    v = [1, 2, 2]
    assert mr.magnitud_velocidad(v) == pytest.approx(3.0)

    v = [0, 0]
    assert mr.magnitud_velocidad(v) == pytest.approx(0.0)

def test_direccion_velocidad_2d():
    mr = MovimientoRelativo()
    v = [1, 0]
    assert mr.direccion_velocidad(v) == pytest.approx(0.0)

    v = [0, 1]
    assert mr.direccion_velocidad(v) == pytest.approx(np.pi/2)

    v = [-1, 0]
    assert mr.direccion_velocidad(v) == pytest.approx(np.pi)

    v = [0, -1]
    assert mr.direccion_velocidad(v) == pytest.approx(-np.pi/2)

    v = [1, 1]
    assert mr.direccion_velocidad(v) == pytest.approx(np.pi/4)

    v = [0, 0]
    assert mr.direccion_velocidad(v) == pytest.approx(0.0) # Opcional: definir comportamiento para vector nulo

def test_direccion_velocidad_3d():
    mr = MovimientoRelativo()
    v = [1, 0, 0]
    assert np.array_equal(mr.direccion_velocidad(v), [1, 0, 0])

    v = [0, 1, 0]
    assert np.array_equal(mr.direccion_velocidad(v), [0, 1, 0])

    v = [1, 1, 1]
    expected_unit_vector = np.array([1/np.sqrt(3), 1/np.sqrt(3), 1/np.sqrt(3)])
    assert np.allclose(mr.direccion_velocidad(v), expected_unit_vector)

    v = [0, 0, 0]
    assert np.array_equal(mr.direccion_velocidad(v), [0, 0, 0])
