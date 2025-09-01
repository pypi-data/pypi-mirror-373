from typing import List, Optional
import numpy as np

# def normalize(matrix: List[List[float]]) -> List[float]:
#     """
#     Return priority weight
#     :param matrix: A 2D comparison matrix criteria
#     :return:
#     """
#     comparison_matrix = np.array(matrix)

#     eigenvalues, eigenvectors = np.linalg.eig(comparison_matrix)
#     max_index = np.argmax(eigenvalues.real)

#     principal_eigenvector = eigenvectors[:, max_index].real

#     return principal_eigenvector / principal_eigenvector.sum()


# def consistency_index(matrix : List[List[float]]) -> float:
#     eigen_value, _ = np.linalg.eig(matrix)

#     n = len(matrix)

#     lambda_max = np.max(eigen_value.real)

#     return (lambda_max - n) / (n - 1)

# def consistency_ratio(ci: float, n: int) -> bool:
#     """

#     :param ci: Consistency index value
#     :param n: The number of criteria
#     :return: If CR < 0.1 return true else false
#     """
#     ri_dict = {
#         1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
#         6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
#     }

#     ri = ri_dict.get(n, 1.49)

#     cr = ci / ri

#     if cr < 0.1:
#         return True

#     return False


def calculate_global_scores(
    criteria_weights: List[float],
    alternative_weights: List[List[float]],
    critery_names: Optional[List[str]] = None,
    alternative_names: Optional[List[str]] = None,
):
    """
    Menggabungkan bobot kriteria, subkriteria, dan alternatif untuk menghasilkan skor global.
    :param criteria_weights: List bobot kriteria
    :param alternative_weights: List bobot alternatif (harus urut sesuai subkriteria)
    :param critery_names: Optional list of names for criteria
    :param alternative_names: Optional list of names for alternatives
    :return: List of tuple (nama alternatif, skor) sorted descending
    """

    criteria_weights = np.array(criteria_weights)
    alternative_weights = np.array(alternative_weights)

    # Validasi dimensi
    if alternative_weights.ndim != 2:
        raise ValueError("alternative_weights must be 2D matrix.")
    
    alternative_rows, alternative_cols = alternative_weights.shape
    if len(criteria_weights) != alternative_cols:
        raise ValueError("Jumlah kriteria pada criteria_weights dan alternative_weights tidak konsisten.")

    if alternative_names is None:
        alternative_names = [f"Alt-{i+1}" for i in range(alternative_rows)]
    if len(alternative_names) != alternative_rows:
        raise ValueError("Panjang alternative_names harus sama dengan jumlah alternatif.")

    global_scores = alternative_weights @ criteria_weights

    total = np.sum(global_scores)
    if total > 0:
        global_scores = global_scores / total

    ranked = sorted(zip(alternative_names, global_scores), key=lambda x: x[1], reverse=True)
    return ranked


class AHP:
    def __init__(self, comparison_matrix: List[List[float]]):
        """
        :param comparison_matrix: A square matrix
        """

        self.__comparison_matrix = np.array(comparison_matrix)
        
        row, column = self.__comparison_matrix.shape

        if row == 1 or column == 1:
            raise ValueError("Comparison matrix must be at least 2x2.")

        if row != column:
            raise ValueError("Comparison matrix must be square.")
        
        
        self.__weights: Optional[List[float]] = None
        self.__is_consistency: Optional[bool] = None

    @property
    def comparison_matrix(self):

        return self.__comparison_matrix

    @property
    def weights(self) -> List[float]:
        """

        :return: priority weight
        """
        if self.__weights is None:
            self.__weights = self.__normalize()

        return self.__weights

    @property
    def is_consistency(self) -> bool:
        if self.__is_consistency is None:
            self.__is_consistency = self.__consistency_ratio()

        return self.__is_consistency

    def __normalize(self) -> List[float]:
        """
        Return priority weight
        :return:
        """
        comparison_matrix = self.__comparison_matrix

        eigenvalues, eigenvectors = np.linalg.eig(comparison_matrix)
        max_index = np.argmax(eigenvalues.real)
        principal_eigenvector = eigenvectors[:, max_index].real

        return principal_eigenvector / principal_eigenvector.sum()

    def __consistency_index(self) -> float:
        eigen_value, _ = np.linalg.eig(self.__comparison_matrix)

        n = len(self.__comparison_matrix)

        lambda_max = np.max(eigen_value.real)

        return (lambda_max - n) / (n - 1)

    def __consistency_ratio(self) -> bool:
        ri_dict = {
            1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
            6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
        }

        n = len(self.__comparison_matrix)

        if n < 1:
            return False

        ri = ri_dict.get(n, 1.49)
        ci = self.__consistency_index()

        cr = ci / ri if ri != 0 else 0

        return cr < 0.1