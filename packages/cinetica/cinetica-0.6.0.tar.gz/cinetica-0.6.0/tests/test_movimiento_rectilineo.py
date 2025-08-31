import pytest
from cinetica.rectilineo import MovimientoRectilineoUniforme, MovimientoRectilineoUniformementeVariado

def test_mru_posicion():
    mru = MovimientoRectilineoUniforme(posicion_inicial=10.0, velocidad_inicial=2.0)
    assert mru.posicion(5) == 20.0  # x = 10 + 2 * 5 = 20
    assert mru.posicion(0) == 10.0

def test_mru_velocidad():
    mru = MovimientoRectilineoUniforme(velocidad_inicial=5.0)
    assert mru.velocidad() == 5.0

def test_mruv_posicion():
    mruv = MovimientoRectilineoUniformementeVariado(posicion_inicial=0.0, velocidad_inicial=10.0, aceleracion_inicial=2.0)
    assert mruv.posicion(3) == 39.0  # x = 0 + 10*3 + 0.5*2*3^2 = 30 + 9 = 39
    assert mruv.posicion(0) == 0.0

def test_mruv_velocidad():
    mruv = MovimientoRectilineoUniformementeVariado(velocidad_inicial=5.0, aceleracion_inicial=3.0)
    assert mruv.velocidad(4) == 17.0  # v = 5 + 3 * 4 = 17
    assert mruv.velocidad(0) == 5.0

def test_mruv_aceleracion():
    mruv = MovimientoRectilineoUniformementeVariado(aceleracion_inicial=9.8)
    assert mruv.aceleracion() == 9.8

def test_mruv_velocidad_sin_tiempo():
    mruv = MovimientoRectilineoUniformementeVariado(posicion_inicial=0.0, velocidad_inicial=0.0, aceleracion_inicial=2.0)
    assert mruv.velocidad_sin_tiempo(16.0) == 8.0  # v^2 = 0^2 + 2*2*(16-0) = 64 => v = 8
    
    mruv_neg_vel = MovimientoRectilineoUniformementeVariado(posicion_inicial=10.0, velocidad_inicial=0.0, aceleracion_inicial=-1.0)
    with pytest.raises(ValueError):
        mruv_neg_vel.velocidad_sin_tiempo(20.0) # Should raise error as v_squared would be negative
