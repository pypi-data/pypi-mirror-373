from collections import Counter

import numpy as np
from numpy.typing import NDArray

from generalized_naive_bayes.utils.types import Vector1D


class GeneralizedNaiveBayesClassifier:
    def __init__(self) -> None:
        """
        Initialize the Gaussian Naive Bayes classifier.
        """
        self.eps = np.finfo(float).eps
        self.classes_ = None
        self.means_ = None
        self.vars_ = None
        self.class_log_prior_ = None

    def _get_priors_and_counts(self, y: Vector1D) -> None:
        """
        Calculate class priors and counts.
        """
        self.classes_, self.counts_ = np.unique(y, sorted=True, return_counts=True)
        self.priors_ = self.counts_ / np.sum(self.counts_)

    def _calculate_single_info_criterion(
        self, X: NDArray[np.float64], y: Vector1D
    ) -> NDArray[np.float64]:
        """
        Calculate single information criterion matrix.

        For each feature, compute the information criterion.
        Using the Gaussian formula for the information criterion.

        Parameters
        ----------
        X : NDArray[np.float64]
            Matrix of shape (n_samples, n_features) containing training data.
        y : Vector1D
            Matrix of shape (n_samples,) containing class labels.

        Returns
        -------
        NDArray[np.float64]
        """
        log_overall_var = np.log2(np.std(X, axis=0, ddof=1) + self.eps)

        log_class_var = np.zeros_like(log_overall_var)
        for idx, cls in enumerate(self.classes_):
            X_cls = X[y == cls]
            var_cls = np.std(X_cls, axis=0, ddof=1)
            log_class_var += self.priors_[idx] * np.log2(var_cls)

        final_single_info_matrix = 0.5 * (log_overall_var - log_class_var)
        return final_single_info_matrix

    def _calculate_double_info_criterion(
        self, X: NDArray[np.float64], y: Vector1D
    ) -> NDArray[np.float64]:
        """
        Calculate double information criterion matrix.

        For each pair of features, compute the information criterion.
        Using the Gaussian formula for the information criterion.

        Parameters
        ----------
        X : NDArray[np.float64]
            Matrix of shape (n_samples, n_features) containing training data.
        y : Vector1D
            Matrix of shape (n_samples,) containing class labels.

        Returns
        -------
        NDArray[np.float64]
        """
        log_overall_var = np.log2(np.std(X, axis=0, ddof=1) ** 2 + self.eps)

        x_col = log_overall_var[:, np.newaxis]
        x_row = log_overall_var[np.newaxis, :]
        var_sum_matrix = x_col + x_row

        class_sum = np.zeros_like(var_sum_matrix)

        for idx, cls in enumerate(self.classes_):
            X_cls = X[y == cls]

            cov_matrix = np.cov(X_cls, rowvar=False, ddof=1)

            variances = np.diag(cov_matrix)

            var_product_matrix = np.outer(variances, variances)
            cov_squared_matrix = cov_matrix**2
            determinant_matrix = var_product_matrix - cov_squared_matrix

            class_sum += self.priors_[idx] * np.log2(determinant_matrix + self.eps)

        final_double_info_matrix = 0.5 * (var_sum_matrix - class_sum)
        return final_double_info_matrix

    def _calculate_argmax_indices(self, matrix: np.ndarray) -> tuple[int, int]:
        """
        Find the row and column indices of the maximum element in a matrix.
        """
        max_position = np.argmax(matrix)  # Flattened index
        num_cols = matrix.shape[1]
        max_row = max_position // num_cols
        max_col = max_position % num_cols
        return int(max_row), int(max_col)

    def _mask_matrix_diag_inf(self, matrix: np.ndarray) -> np.ndarray:
        """
        Mask the diagonal by multiplying with a matrix that keeps off-diagonals the same
        but sets diagonal positions effectively to negative infinity.
        """
        mat_len = matrix.shape[0]
        mask_matrix = -2 * np.eye(mat_len) + np.ones((mat_len, mat_len))
        return matrix * mask_matrix

    def _calculate_nodes(self, X: np.ndarray, y: np.ndarray) -> list[tuple[int, int]]:
        """
        Calculate nodes based on single and double information criteria.
        """
        # Compute info matrices
        single_info_matrix = self.calculate_single_info_criterion(X=X, y=y)
        double_info_matrix = self.calculate_double_info_criterion(X=X, y=y)
        self.single_info_matrix = single_info_matrix
        self.double_info_matrix = double_info_matrix

        # Masked double info
        masked_final_info = self._mask_matrix_diag_inf(double_info_matrix)
        self.masked_init_info = masked_final_info

        # Difference matrix
        diff_matrix = double_info_matrix - single_info_matrix[:, np.newaxis]
        diff_matrix = self._mask_matrix_diag_inf(diff_matrix)
        self.diff_matrix = diff_matrix

        # Start with the initial node (argmax of masked double info)
        init_node = self._calculate_argmax_indices(masked_final_info)
        nodes = [init_node]

        # Track remaining columns and selectable rows
        remaining_cols = set(range(X.shape[1])) - set(init_node)
        selectable_rows = set(init_node)

        while remaining_cols:
            selectable_rows_list = sorted(selectable_rows)
            remaining_cols_list = sorted(remaining_cols)

            # Extract submatrix
            submatrix = diff_matrix[np.ix_(selectable_rows_list, remaining_cols_list)]

            # Get indices of max value within submatrix
            max_row_idx, max_col_idx = self._calculate_argmax_indices(submatrix)

            # Map indices back to original matrix positions
            new_row = selectable_rows_list[max_row_idx]
            new_col = remaining_cols_list[max_col_idx]
            new_node = (new_row, new_col)

            # Update nodes and sets
            nodes.append(new_node)
            remaining_cols.remove(new_col)
            selectable_rows.add(new_col)

        return nodes

    def _get_single_dividers(self, nodes):
        """
        Count how many times each feature index appears across nodes,
        and subtract one for features that appear more than once.
        """
        flat_list = [item for tup in nodes for item in tup]
        count = Counter(flat_list)

        return Counter({key: value - 1 for key, value in count.items() if value > 1})

    def fit_multivariate_gaussians(self, X: np.ndarray, y: np.ndarray, nodes):
        """
        Fit multivariate Gaussian parameters (mean vectors and covariance matrices)
        for each class and each pair of features specified in nodes.
        """
        n_classes = len(self.classes_)
        n_nodes = len(nodes)
        n_selected_features = 2

        multi_means = np.zeros((n_classes, n_nodes, n_selected_features), dtype=X.dtype)
        multi_cov = np.zeros(
            (n_classes, n_nodes, n_selected_features, n_selected_features),
            dtype=X.dtype,
        )

        for cls_idx, cls in enumerate(self.classes_):
            X_cls = X[y == cls]
            for node_idx, node in enumerate(nodes):
                X_cls_nodes = X_cls[:, node]  # Select two features
                mean_vector = X_cls_nodes.mean(axis=0)
                cov_matrix = np.cov(
                    X_cls_nodes, rowvar=False, ddof=1
                )  # unbiased covariance
                multi_means[cls_idx, node_idx] = mean_vector
                multi_cov[cls_idx, node_idx] = cov_matrix

        self.multi_means_ = multi_means
        self.multi_cov_ = multi_cov
        return self.multi_means_, self.multi_cov_

    def fit_univariate_gaussians(self, X: np.ndarray, y: np.ndarray):
        """
        Fit univariate Gaussian parameters (mean and standard deviation)
        for each class and each feature.
        """
        n_classes = len(self.classes_)
        n_features = X.shape[1]

        uni_means = np.zeros((n_classes, n_features), dtype=X.dtype)
        uni_std = np.zeros((n_classes, n_features), dtype=X.dtype)

        for cls_idx, cls in enumerate(self.classes_):
            X_cls = X[y == cls]
            mean_cls = X_cls.mean(axis=0)
            var_cls = np.var(X_cls, axis=0, ddof=1)  # unbiased variance
            uni_means[cls_idx] = mean_cls
            uni_std[cls_idx] = np.sqrt(var_cls)

        self.uni_means_ = uni_means
        self.uni_var_ = uni_std
        return self.uni_means_, self.uni_var_

    def calc_sum_multivariate_log_prob(self, X: np.ndarray, nodes):
        """
        Calculate the sum of log-probabilities for multivariate Gaussians.
        """
        n_classes = len(self.classes_)
        n_nodes = len(nodes)
        n_samples = X.shape[0]

        sum_log_likelihood = np.zeros((n_classes, n_nodes, n_samples), dtype=X.dtype)

        for cls_idx, cls in enumerate(self.classes_):
            for node_idx, node in enumerate(nodes):
                mean = self.multi_means[cls_idx][node_idx]
                cov = self.multi_covs[cls_idx][node_idx]

                # Pre-compute inverse and determinant for multivariate Gaussian
                cov_inv = np.linalg.inv(cov)
                det_cov = np.linalg.det(cov)
                const = -0.5 * (len(node) * np.log(2 * np.pi) + np.log(det_cov))

                # Compute log probability for each sample
                diff = X[:, node] - mean
                log_prob = const - 0.5 * np.einsum("ij,ij->i", diff @ cov_inv, diff)
                sum_log_likelihood[cls_idx, node_idx] = log_prob

        return sum_log_likelihood

    def calc_sum_univariate_log_prob(self, X: np.ndarray, counter):
        """
        Calculate the sum of log-probabilities for univariate Gaussians.
        """
        n_classes = len(self.classes_)
        n_terms = len(counter)
        n_samples = X.shape[0]

        sum_univariate_log_likelihood = np.zeros(
            (n_classes, n_terms, n_samples), dtype=X.dtype
        )

        for cls_idx, cls in enumerate(self.classes_):
            for count_idx, (key, value) in enumerate(counter.items()):
                mean = self.uni_means[cls_idx][key]
                std = self.uni_vars[cls_idx][key]

                # Avoid division by zero
                var = std**2
                log_const = -0.5 * np.log(2 * np.pi * var)
                log_prob = log_const - 0.5 * ((X[:, key] - mean) ** 2) / var

                # Multiply by feature repetition count
                sum_univariate_log_likelihood[cls_idx, count_idx] = log_prob * value

        return sum_univariate_log_likelihood

    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        Fit the model: compute nodes, counts, and Gaussian parameters.
        """
        self.nodes = self._calculate_nodes(X=X, y=y)
        self.counter = self._get_single_dividers(self.nodes)

        self.multi_means, self.multi_covs = self.fit_multivariate_gaussians(
            X, y, self.nodes
        )
        self.uni_means, self.uni_vars = self.fit_univariate_gaussians(X, y)

    def predict_proba(self, X: np.ndarray):
        """
        Predict log probabilities for each sample and class.
        """
        log_multi = self.calc_sum_multivariate_log_prob(X, self.nodes).sum(axis=1)
        log_uni = self.calc_sum_univariate_log_prob(X, self.counter).sum(axis=1)
        pred = (log_multi - log_uni).T
        return pred

    def predict(self, X: np.ndarray):
        """
        Predict class indices for each sample.
        """
        pred = self.predict_proba(X)
        return np.argmax(pred, axis=1)
