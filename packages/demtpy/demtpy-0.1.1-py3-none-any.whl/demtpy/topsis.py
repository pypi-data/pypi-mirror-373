from typing import List, Optional
import numpy as np

class TOPSIS:
    def __init__(self, matrix: List[List[float]], weights: List[float], criteria_preference: List[int]):
        self.__matrix = np.array(matrix)
        self.__weights = np.array(weights)
        self.__criteria_preference = np.array(criteria_preference)

        if self.__matrix.ndim != 2:
            raise ValueError("Input matrix must be 2-dimensional.")
        
        if self.__matrix.shape[1] != len(self.__weights):
            raise ValueError("Number of weights must match number of criteria (columns in matrix).")
        
        if len(self.__weights) != len(self.__criteria_preference):
            raise ValueError("Number of criteria preferences must match number of weights.")

    # def __normalize_matrix(self) -> List[float]:
    #     return self.__matrix / np.sqrt(np.sum(self.__matrix**2, axis=0))

    def __normalize(self):
        norm_matrix = self.__matrix / np.sqrt(np.sum(self.__matrix**2, axis=0))

        return norm_matrix * self.__weights

    def __get_ideal_best_worst(self):

        # normalize_weights = self.__normalize()

        # ideal_positive = np.zeros(normalize_weights.shape[1])
        # ideal_negative = np.zeros(normalize_weights.shape[1])

        # for j in range(normalize_weights.shape[1]):
        #     if self.__criteria_preference[j] == 1:
        #         ideal_positive[j] = np.max(normalize_weights[:, j])
        #         ideal_negative[j] = np.min(normalize_weights[:, j])
        #     else:
        #         ideal_positive[j] = np.min(normalize_weights[:, j])
        #         ideal_negative[j] = np.max(normalize_weights[:, j])

        # return ideal_positive, ideal_negative

        norm_weighted = self.__normalize()

        ideal_best = np.where(self.__criteria_preference == 1, norm_weighted.max(axis=0), norm_weighted.min(axis=0))
        ideal_worst = np.where(self.__criteria_preference == 1, norm_weighted.min(axis=0), norm_weighted.max(axis=0))

        return ideal_best, ideal_worst

    def __get_distance_ideal(self):

        normalize_weights = self.__normalize()
        ideal_positive, ideal_negative = self.__get_ideal_best_worst()

        ideal_positive_distance = np.sqrt(np.sum((ideal_positive - normalize_weights)**2, axis=1))
        ideal_negative_distance = np.sqrt(np.sum((normalize_weights - ideal_negative)**2, axis=1))

        return ideal_positive_distance, ideal_negative_distance

    def get_score(self):
        """
        :return: Array of preference scores for each alternative
        """

        ideal_positive_distance, ideal_negative_distance = self.__get_distance_ideal()
        
        v = ideal_negative_distance / (ideal_positive_distance + ideal_negative_distance)

        return v