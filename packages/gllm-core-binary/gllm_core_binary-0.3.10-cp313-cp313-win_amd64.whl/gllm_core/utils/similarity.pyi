def cosine(vector: list[float], matrix: list[list[float]]) -> list[float]:
    """Calculate cosine similarities between a vector and a matrix of vectors.

    Args:
        vector (list[float]): The input vector to compare against.
        matrix (list[list[float]]): The matrix of vectors to compare with.

    Returns:
        list[float]: The list of cosine similarities between the vector and each row of the matrix.
    """
