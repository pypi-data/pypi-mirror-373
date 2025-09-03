import numpy as np
from sklearn.base import BaseEstimator
from sklearn.utils._set_output import _SetOutputMixin
from sklearn.utils.validation import check_is_fitted, validate_data

__all__ = ["FAME3RScoreEstimator"]


class FAME3RScoreEstimator(BaseEstimator, _SetOutputMixin):
    """Computes the FAME score for a set of features.

    The FAME score is defined as the mean Tanimoto similarity of the feature
    vector to the ``n`` closest vectors in the training set.

    It is intended for this estimator to only be used with binary feature
    ("fingerprint") vectors, as Tanimoto similarity is not well-behaved on
    arbitrary vectors.

    Parameters
    ----------
    n_neighbors : int, default=3

        Number of nearest neigbors to consider during FAME score
        calculation. Defaults to 3, as defined in the original paper.

    Examples
    --------
    >>> from fame3r import FAME3RVectorizer, FAME3RScoreEstimator
    >>> from sklearn.pipeline import make_pipeline
    >>> pipeline = make_pipeline(
    >>>    FAME3RVectorizer(output=["fingerprint"]),
    >>>    FAME3RScoreEstimator()
    >>> ).fit([["CC[C:1]"], ["CC[N:1]"], ["CC[O:1]"]])
    >>> pipeline.predict([["[C:1]CC"]])
    array([0.66666667])
    """

    def __init__(self, n_neighbors: int = 3):
        self.n_neighbors: int = n_neighbors

    def fit(self, X, y=None):
        """Fit the estimator to the training set of known samples.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            Training data.

        y : (ignored)
            Not used, present for API consistency by convention.

        Returns
        -------
        self : object
            FAME3RVectorizer class instance.
        """

        X = validate_data(
            self,
            X,
            dtype="numeric",
            ensure_2d=True,
            ensure_min_samples=self.n_neighbors,
            estimator=FAME3RScoreEstimator,
        )

        self._reference_data = X

        return self

    def predict(self, X):
        """Compute the FAME score of the given samples.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            Query data.

        Returns
        -------
        y : ndarray of shape (n_samples,)
            The predicted FAME scores.
        """
        check_is_fitted(self)
        X = validate_data(
            self,
            X,
            reset=False,
            dtype="numeric",
            ensure_2d=True,
            ensure_min_samples=0,
            estimator=FAME3RScoreEstimator,
        )

        return np.concat(
            [
                _fame_score(self._reference_data, X_batch, n_neighbors=self.n_neighbors)
                for X_batch in np.array_split(X, 100)
            ]
        )

    def get_feature_names_out(self, input_features=None):
        """Get output feature names for transformation.

        Parameters
        ----------
        input_features : array-like of str or None, default=None
            Not used, present here for API consistency by convention.

        Returns
        -------
        feature_names_out : ndarray of str objects
            Transformed feature names.
        """
        return ["FAME3RScore"]


def _fame_score(reference, X, *, n_neighbors):
    similarity_matrix = _tanimoto_similarity_matrix(reference, X)

    return np.mean(
        np.sort(similarity_matrix, axis=0)[-n_neighbors:],
        axis=0,
    )


def _tanimoto_similarity_matrix(A, B):
    A = np.asarray(A)
    B = np.asarray(B)

    intersection = np.matmul(A, B.T)
    A_sqare_norm = np.sum(A**2, axis=1)
    B_sqare_norm = np.sum(B**2, axis=1)
    union = A_sqare_norm[:, None] + B_sqare_norm[None, :] - intersection

    return np.divide(
        intersection,
        union,
        out=np.zeros_like(intersection, dtype=np.float64),
        where=union != 0,
    )
