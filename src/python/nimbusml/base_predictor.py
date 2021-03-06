# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------------------------
"""
Base class for all the predictors.
"""

__all__ = ["BasePredictor"]

import os

from sklearn.base import BaseEstimator
from sklearn.utils.multiclass import unique_labels
from sklearn.utils.validation import check_is_fitted

from . import Pipeline
from .internal.core.base_pipeline_item import BasePipelineItem
from .internal.utils.utils import trace, compare_shape, set_shape


class BasePredictor(BaseEstimator, BasePipelineItem):
    """
    Base class for all predictors.
    """

    @trace
    def __init__(self, **params):
        if 'type' not in params:
            raise KeyError("type must be specified")
        BasePipelineItem.__init__(self, **params)

    @trace
    def fit(self, X, y=None, **params):
        """
        Fit the model given training data

        :param X: array-like with shape=[n_samples, n_features] or else
        :py:class:`nimbusml.FileDataStream`
        :param y: array-like with shape=[n_samples]
        :return: self
        """
        if y is not None and not isinstance(y, (
                str, tuple)) and self.type in set(
                ['classifier', 'anomaly']):
            unique_classes = unique_labels(y)
            if len(unique_classes) < 2:
                raise ValueError(
                    "Classifier can't train when only one class is "
                    "present.")
            self.classes_ = unique_classes
        self.X_ = X
        self.y_ = y

        pipeline = Pipeline([self])
        try:
            pipeline.fit(X, y, **params)
        except RuntimeError as e:
            set_shape(self, X)
            self.model_ = pipeline.model
            raise e

        self.model_ = pipeline.model
        set_shape(self, X)
        return self

    @trace
    def _invoke_inference_method(self, method, X, **params):
        """
        Returns predictions. Can be predicted labels, probabilities
        or else decision values.
        """
        check_is_fitted(self, ["X_", "y_"])

        # Check that the input is of the same shape as the one passed
        # during
        # fit.
        compare_shape(self, X)

        # if not isinstance(X, DataFrame):
        #     X = check_array(X, accept_sparse=['csr'])

        pipeline = Pipeline([self], model=self.model_)
        data = getattr(pipeline, method)(X, **params)
        return data

    @trace
    def predict(self, X, **params):
        """
        Predict target value

        :param X: array-like with shape=[n_samples, n_features] or else
        :py:class:`nimbusml.FileDataStream`
        :return: pandas.DataFrame, [n_samples]
        """
        data = self._predict(X, **params)
        try:
            predictions = data['PredictedLabel'] if (
                        self.type == "classifier" or self.type ==
                        "clusterer") else data['Score']
        except KeyError as e:
            raise KeyError(
                "Type: {0}, unable to find column {1} in {2}".format(
                    self.type, str(e), data.columns))
        return predictions

    @trace
    def _predict(self, X, **params):
        return self._invoke_inference_method('predict', X, **params)

    @trace
    def _check_implements_method(self, method):
        """
        Checks if this class implements method
        """
        if not hasattr(self, method):
            raise AttributeError(method + "() is not available for "
                                 + str(self.__class__))

    @trace
    def _predict_proba(self, X, **params):
        """
        Generate probabilities if method exists
        """
        self._check_implements_method('predict_proba')
        return self._invoke_inference_method('predict_proba', X, **params)

    @trace
    def _decision_function(self, X, **params):
        """
        Generate decision values if method exists
        """
        self._check_implements_method('decision_function')
        return self._invoke_inference_method('decision_function', X,
                                             **params)

    @trace
    def summary(self):
        """
        Returns model summary.
        """
        if hasattr(self, 'model_summary_') and self.model_summary_:
            return self.model_summary_

        if not hasattr(
                self, 'model_') or self.model_ is None or not \
                os.path.isfile(self.model_):
            raise ValueError(
                "Model is not fitted. Train or load a model before "
                "summary().")

        pipeline = Pipeline([self], model=self.model_)
        self.model_summary_ = pipeline.summary()
        return self.model_summary_
