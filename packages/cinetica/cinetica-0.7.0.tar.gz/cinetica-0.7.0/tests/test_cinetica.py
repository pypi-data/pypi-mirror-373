import pytest

from cinetica import __version__

def test_version():
    assert __version__ == "0.5.9"
