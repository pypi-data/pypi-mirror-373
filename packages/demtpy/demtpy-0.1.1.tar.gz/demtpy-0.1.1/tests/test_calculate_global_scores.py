
import pytest
import numpy as np
from demtpy.ahp import calculate_global_scores

def test_calculate_global_scores_basic():
    # 5 kriteria, 3 alternatif
    criteria_weights = [0.285, 0.218, 0.153, 0.232, 0.111]
    # alternative_weights: 3 alternatif x 5 kriteria
    alternative_weights = [
        [0.589, 0.557, 0.407, 0.492, 0.62,],  # A
        [0.252, 0.32, .329, .396, .224],  # B
        [0.159, 0.123, .264, .111, .156],  # C
    ]
    alternative_names = ["A", "B", "C"]
    ranked = calculate_global_scores(criteria_weights, alternative_weights, alternative_names=alternative_names)

    total = 0.535 + 0.309 + 0.156
    expected = [0.535/total, 0.309/total, 0.156/total]

    for (name, score), exp in zip(ranked, expected):
        assert np.isclose(score, exp, atol=0.01)

    assert ranked[0][0] == "A"
    assert ranked[1][0] == "B"
    assert ranked[2][0] == "C"

def test_calculate_global_scores_normalization():
    criteria_weights = [0.5, 0.5]
    alternative_weights = [
        [1, 0],
        [0, 1],
    ]
    alternative_names = ["X", "Y"]
    ranked = calculate_global_scores(criteria_weights, alternative_weights, alternative_names=alternative_names)
    # Skor: X: 0.5*1 + 0.5*0 = 0.5, Y: 0.5*0 + 0.5*1 = 0.5
    total = 0.5 + 0.5
    expected = [0.5/total, 0.5/total]
    for (name, score), exp in zip(ranked, expected):
        assert np.isclose(score, exp)
    assert ranked[0][1] == ranked[1][1]

def test_calculate_global_scores_invalid_names():
    criteria_weights = [1.0]
    alternative_weights = [[0.5], [0.5]]
    alternative_names = ["A"]  # Salah, harus 2
    with pytest.raises(ValueError):
        calculate_global_scores(criteria_weights, alternative_weights, alternative_names=alternative_names)