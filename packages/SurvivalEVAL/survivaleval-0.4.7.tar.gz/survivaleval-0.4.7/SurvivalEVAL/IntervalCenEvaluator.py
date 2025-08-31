import numpy as np
import pandas as pd
import warnings
from typing import Union, Optional, Callable
from scipy.integrate import trapezoid
import matplotlib.pyplot as plt
from abc import ABC
from functools import cached_property

from SurvivalEVAL.Evaluations.custom_types import Numeric, NumericArrayLike
from SurvivalEVAL.Evaluations.util import (check_and_convert, predict_rmst, predict_mean_st, predict_median_st,
                                           predict_prob_from_curve, predict_multi_probs_from_curve, quantile_to_survival)

from SurvivalEVAL.Evaluations.SingleTimeCalibration import one_cal_ic
from SurvivalEVAL.Evaluations.DistributionCalibration import d_cal_ic

class IntervalCenEvaluator:
    """
    Evaluator for interval-censored survival data.
    """

    def __init__(
            self,
            pred_survs: NumericArrayLike,
            time_coordinates: NumericArrayLike,
            left_limits: NumericArrayLike,
            right_limits: NumericArrayLike,
            train_left_limits: Optional[NumericArrayLike] = None,
            train_right_limits: Optional[NumericArrayLike] = None,
            predict_time_method: str = "Median",
            interpolation: str = "Linear"
    ):
        """
        Initialize the Evaluator

        Parameters
        ----------
        pred_survs: NumericArrayLike
            Accept shapes: (n_time_points,) or (n_samples, n_time_points).
            Predicted survival probabilities for the testing samples.
            At least one of `pred_survs` or `time_coordinates` must be a 2D array.
        time_coordinates: NumericArrayLike
            Accept shapes: (n_time_points,) or (n_samples, n_time_points).
            Time coordinates for the predicted survival probabilities.
            At least one of `pred_survs` or `time_coordinates` must be a 2D array.
        left_limits: NumericArrayLike, shape = (n_samples,)
            Left limits of the interval-censored testing data.
        right_limits: NumericArrayLike, shape = (n_samples,)
            Right limits of the interval-censored testing data.
        train_left_limits: Optional[NumericArrayLike], shape = (n_train_samples,), default: None
            Left limits of the interval-censored data for the training set.
        train_right_limits: Optional[NumericArrayLike], shape = (n_train_samples,), default: None
            Right limits of the interval-censored data for the training set.
        predict_time_method: str, default: "Median"
            Method to predict time from the survival curve. Options are "Median", "Mean", or "RMST".
        interpolation: str, default: "Linear"
            Interpolation method for the survival curve. Options are "Linear" or "Pchip".
        """
        # TODO: padding

        left_limits, right_limits = check_and_convert(left_limits, right_limits)
        self.left_limits = left_limits
        self.right_limits = right_limits

        if (train_left_limits is not None) and (train_right_limits is not None):
            train_left_limits, train_right_limits = check_and_convert(train_left_limits, train_right_limits)
        self.train_left_limits = train_left_limits
        self.train_right_limits = train_right_limits

        if predict_time_method == "Median":
            self.predict_time_method = predict_median_st
        elif predict_time_method == "Mean":
            self.predict_time_method = predict_mean_st
        elif predict_time_method == "RMST":
            self.predict_time_method = predict_rmst
        else:
            error = "Please enter one of 'Median', 'Mean', or 'RMST' for calculating predicted survival time."
            raise TypeError(error)

        self.interpolation = interpolation

    def _error_trainset(self, method_name: str):
        if (self.train_left_limits is None) or (self.train_right_limits is None):
            raise TypeError("Train set information is missing. "
                            "Evaluator cannot perform {} evaluation.".format(method_name))

    @property
    def pred_survs(self):
        return self._pred_survs

    @pred_survs.setter
    def pred_survs(self, val: NumericArrayLike):
        print("Setter called. Resetting predicted curves for this evaluator.")
        self._pred_survs = check_and_convert(val)
        self._clear_cache()

    @property
    def time_coordinates(self):
        return self._time_coordinates

    @time_coordinates.setter
    def time_coordinates(self, val: NumericArrayLike):
        print("Setter called. Resetting time coordinates for this evaluator.")
        self._time_coordinates = check_and_convert(val)
        self._clear_cache()

    @cached_property
    def predicted_event_times(self):
        return self.predict_time_from_curve(self.predict_time_method)

    def _clear_cache(self):
        # See how to clear cache in functools:
        # https://docs.python.org/3/library/functools.html#functools.cached_property
        # https://stackoverflow.com/questions/62662564/how-do-i-clear-the-cache-from-cached-property-decorator
        self.__dict__.pop('predicted_event_times', None)

    def predict_time_from_curve(
            self,
            predict_method: Callable,
    ) -> np.ndarray:
        """
        Predict survival time from survival curves.
        param predict_method: Callable
            A function that takes in a survival curve and returns a predicted survival time.
            There are three build-in methods: 'predict_median_st', 'predict_mean_st', and 'predict_rmst'.
            'predict_median_st' uses the median of the survival curve as the predicted survival time.
            'predict_mean_st' uses the expected time of the survival curve as the predicted survival time.
            'predict_rmst' uses the restricted mean survival time of the survival curve as the predicted survival time.
        :return: np.ndarray
            Predicted survival time for each sample.
        """
        if ((predict_method is not predict_mean_st) and (predict_method is not predict_median_st) and
                (predict_method is not predict_rmst)):
            error = "Prediction method must be 'predict_mean_st', 'predict_median_st', or 'predict_rmst'" \
                    "got '{}' instead".format(predict_method.__name__)
            raise TypeError(error)

        predicted_times = predict_method(self._pred_survs, self._time_coordinates, self.interpolation)
        return predicted_times

    def one_calibration(
            self,
            target_time: Numeric,
            num_bins: int = 10,
            binning_strategy: str = "C",
            method: str = "Turnbull"
    ) -> (float, list, list):
        """
        Calculate the one calibration score at a given time point from the predicted survival curve.

        Parameters
        ----------
        target_time
        num_bins
        binning_strategy
        method

        Returns
        -------
        p_value: float
            The p-value of the calibration test.
        observed_probabilities: list
            The observed probabilities in each bin.
        expected_probabilities: list
            The expected probabilities in each bin.
        """
        predict_probs = self.predict_probability_from_curve(target_time)
        return one_cal_ic(
            preds=1 - predict_probs,
            left_limits=self.left_limits,
            right_limits=self.right_limits,
            target_time=target_time,
            num_bins=num_bins,
            binning_strategy=binning_strategy,
            method=method
        )


    def d_calibration(
            self,
            num_bins: int = 10
    ) -> (float, np.ndarray):
        """
        Calculate the D calibration score from the predicted survival curve.
        Parameters
        ----------
        num_bins: int, default: 10
            Number of bins used to calculate the D calibration score.

        Returns
        -------
        p_value: float
            The p-value of the calibration test.
        hist: np.ndarray
            The histogram of the predicted probabilities in each bin.
        """
        pred_probs_left = self.predict_probability_from_curve(self.left_limits)
        pred_probs_right = self.predict_probability_from_curve(self.right_limits)
        return d_cal_ic(
            pred_probs_left=pred_probs_left,
            pred_probs_right=pred_probs_right,
            num_bins=num_bins
        )


