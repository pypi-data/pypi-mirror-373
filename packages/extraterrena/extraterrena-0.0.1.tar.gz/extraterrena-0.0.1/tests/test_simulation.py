import pytest
import numpy as np
from extraterrena import simulation


def test_simulate_linear_array_construct():
    data = simulation.simulate_linear_array_construct(
        4, 1e9, 30, 10, np.linspace(0, 1, 100)
    )

    assert isinstance(data, np.ndarray)
