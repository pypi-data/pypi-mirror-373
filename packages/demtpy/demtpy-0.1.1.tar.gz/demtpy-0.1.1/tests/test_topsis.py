import pytest
import numpy as np
from demtpy.topsis import TOPSIS

def test_topsis_basic():
    # 3 alternatif, 2 kriteria
    matrix = [
        [250, 16],   # A1
        [200, 20],   # A2
        [300, 14],   # A3
    ]
    weights = [0.6, 0.4]
    criteria_preference = [1, -1]  # Kriteria 1 benefit, kriteria 2 cost
    topsis = TOPSIS(matrix, weights, criteria_preference)
    scores = topsis.get_score()
    assert len(scores) == 3
    assert np.all(scores >= 0) and np.all(scores <= 1)
    # Pastikan ranking benar
    ranked = np.argsort(scores)[::-1]
    # Skor tertinggi harus alternatif terbaik
    assert ranked[0] in [0, 1, 2]


def test_topsis_equal_weights():
    matrix = [
        [1, 2],
        [2, 1],
    ]
    weights = [0.5, 0.5]
    criteria_preference = [1, 1]
    topsis = TOPSIS(matrix, weights, criteria_preference)
    scores = topsis.get_score()
    assert np.isclose(scores.sum(), 1, atol=1)


def test_topsis_invalid_input():
    # Matrix and weights length mismatch
    matrix = [
        [1, 2],
        [2, 1],
    ]
    weights = [1]
    criteria_preference = [1, 1]
    with pytest.raises(ValueError):
        TOPSIS(matrix, weights, criteria_preference)
