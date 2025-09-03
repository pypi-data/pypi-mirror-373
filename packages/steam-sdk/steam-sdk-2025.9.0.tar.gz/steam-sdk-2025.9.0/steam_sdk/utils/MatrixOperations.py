import numpy as np


def multiply_column_by_value(matrix: np.array, column_number: int, multiplication_factor: float):
    matrix[:, column_number] = multiplication_factor * matrix[:, column_number]
