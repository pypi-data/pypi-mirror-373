import pytest
from demtpy.ahp import AHP
import numpy as np

# Test valid matrix
@pytest.mark.parametrize("matrix,expected_weights", [
    (
        [
            [1, 1, 3, 1, 3],
            [1, 1, 2, 1, 1],
            [1/3, 1/2, 1, 1, 2],
            [1, 1, 1, 1, 3],
            [1/3, 1, 1/2, 1/3, 1]
        ],
        None  # Weights are dynamic, just check sum to 1
    ),
    (
        [
            [1, 2, 3],
            [1/2, 1, 4],
            [1/3, 1/4, 1]
        ],
        None
    ),
])
def test_weights_sum_to_one(matrix, expected_weights):
    ahp = AHP(matrix)
    weights = ahp.weights
    assert np.isclose(sum(weights), 1.0)
    assert all(w >= 0 for w in weights)

# Test consistency ratio
@pytest.mark.parametrize("matrix,expected_consistency", [
    (
        [
            [1, 1, 3, 1, 3],
            [1, 1, 2, 1, 1],
            [1/3, 1/2, 1, 1, 2],
            [1, 1, 1, 1, 3],
            [1/3, 1, 1/2, 1/3, 1]
        ],
        True
    ),
    (
        [
            [1, 9, 9],
            [1/9, 1, 9],
            [1/9, 1/9, 1]
        ],
        False  # Should be inconsistent
    ),
])
def test_consistency(matrix, expected_consistency):
    ahp = AHP(matrix)
    assert ahp.is_consistency == expected_consistency

# Test invalid input (non-square matrix)
def test_invalid_matrix():
    matrix = [
        [1, 2, 3],
        [1, 2, 3]
    ]

    with pytest.raises(ValueError):
        ahp = AHP(matrix)

# Test edge case: 1x1 matrix
def test_one_by_one_matrix():
    matrix = [[1]]

    with pytest.raises(ValueError):
        ahp = AHP(matrix)
        print(ahp.comparison_matrix)

# Test edge case: 2x2 matrix
def test_two_by_two_matrix():
    matrix = [[1, 2], [0.5, 1]]
    ahp = AHP(matrix)
    weights = ahp.weights
    assert np.isclose(sum(weights), 1.0)
    assert ahp.is_consistency is True
