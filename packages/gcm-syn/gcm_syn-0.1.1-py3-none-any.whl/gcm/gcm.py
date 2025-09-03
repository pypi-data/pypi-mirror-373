import numpy as np
from scipy.stats import zscore

class GCM:
    """
    Generative Correlation Manifolds (GCM)

    A class to generate synthetic data with the same correlation structure
    as a source dataset. The method is based on the whitepaper "Generative
    Correlation Manifolds: Generating Synthetic Data with Preserved Higher-Order
    Correlations" by Jens E. d'Hondt.
    """
    def __init__(self):
        self.cholesky_ = None
        self.is_fitted_ = False

    def fit(self, X):
        """
        Fit the GCM model to the source data.

        This method computes the Cholesky decomposition of the correlation
        matrix of the source data. This decomposition is then used by the
        `sample` method to generate new data.

        Parameters:
        X : np.ndarray
            The source data to fit the model to. The data should be a 2D
            array where each row is a sample and each column is a feature.
        """
        if not isinstance(X, np.ndarray):
            X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)

        # Z-normalize the data
        X_z = zscore(X)

        # Compute the correlation matrix
        corr_matrix = np.corrcoef(X_z, rowvar=False)

        # Perform Cholesky decomposition
        self.cholesky_ = np.linalg.cholesky(corr_matrix)
        self.is_fitted_ = True

    def fit_from_correlation(self, corr_matrix):
        """
        Fit the GCM model from a correlation matrix.

        This method computes the Cholesky decomposition of the given
        correlation matrix. This decomposition is then used by the `sample`
        method to generate new data.

        Parameters:
        corr_matrix : np.ndarray
            The correlation matrix to fit the model to. The matrix should be
            a square, symmetric, and positive-semidefinite 2D array.
        """
        if not isinstance(corr_matrix, np.ndarray):
            corr_matrix = np.asarray(corr_matrix)
        if corr_matrix.ndim != 2 or corr_matrix.shape[0] != corr_matrix.shape[1]:
            raise ValueError("The correlation matrix must be a square 2D array.")

        # Perform Cholesky decomposition
        self.cholesky_ = np.linalg.cholesky(corr_matrix)
        self.is_fitted_ = True

    def sample(self, num_samples):
        """
        Generate synthetic samples.

        This method uses the fitted GCM model to generate new synthetic
        samples that have the same correlation structure as the source data.

        Parameters:
        num_samples : int
            The number of synthetic samples to generate.

        Returns:
        S : np.ndarray
            The generated synthetic dataset.
        """
        if not self.is_fitted_:
            raise RuntimeError("The model has not been fitted yet. Please call 'fit' before sampling.")

        # Generate independent random variables
        num_features = self.cholesky_.shape[0]
        Z = np.random.normal(0, 1, size=(num_samples, num_features))

        # Transform to create correlated data
        S = Z @ self.cholesky_.T

        return S
