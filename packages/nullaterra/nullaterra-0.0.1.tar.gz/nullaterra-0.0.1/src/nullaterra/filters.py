from abc import ABC, abstractmethod

import numpy as np


class Filter(ABC):
    """Takes in an array covariance matrix and returns
    a corrected array covariance matrix.
    """

    @abstractmethod
    def filter(
        self,
        acm: np.array,
    ): ...


class NullEigenvalueFilter(Filter):
    """Adjusts the covariance matrix by nulling the largest eigenvalues.

    :param Filter:
    :type Filter: _type_
    """

    def filter(self, acm: np.ndarray, num_eigenvalues: int = 1) -> np.ndarray:
        """Adjusts the covariance matrix by nulling the largest eigenvalue.

        :param acm: Array covariance matrix to adjust.
        :type acm: np.ndarray
        :param num_eigenvalues: Number of eigenvalues to null, defaults to 1.
        :type num_eigenvalues: int
        :return: Adjusted array covariance matrix with the first eigenvalue nulled.
        :rtype: np.ndarray
        """
        if num_eigenvalues <= 0:
            raise ValueError("Number of eigenvalues to null should be positive.")

        eigenvalues, eigenvectors = np.linalg.eigh(acm)
        eigenvalues[-num_eigenvalues:] = 0
        return eigenvectors @ np.diag(eigenvalues) @ eigenvectors.conj().T


class ShrinkEigenvalueFilter(Filter):
    """Shrinks largest eigenvalues of array covariance matrix instead of nulling them.

    Follows the methodology set out in Kocz (2010)

    :param Filter: _description_
    :type Filter: _type_
    """

    def filter(self, acm: np.ndarray, num_eigenvalues: int = 1) -> np.ndarray:
        """Shrinks the largest num_eigenvalues eigenvalues to the average of the
        remaining eigenvalues.

        :param acm: Array covariance matrix to be adjusted.
        :type acm: np.ndarray
        :param num_eigenvalues: Number of eigenvalues to shrink. Must be positive and less than number of rows of acm.
        :type num_eigenvalues: int
        :return: Array covariance matrix
        :rtype: np.ndarray
        """

        if num_eigenvalues <= 0:
            raise ValueError("Number of eigenvalues to shrink should be positive.")
        eigenvalues, eigenvectors = np.linalg.eigh(acm)
        mean_remaining_eigenvalues = np.mean(eigenvalues[:-num_eigenvalues])

        eigenvalues[-num_eigenvalues:] = mean_remaining_eigenvalues
        return eigenvectors @ np.diag(eigenvalues) @ eigenvectors.conj().T
