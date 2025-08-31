import time
import numpy as np
import warnings
from scipy import integrate

from SurvivalEVAL.Evaluations.util import predict_rmst, predict_mean_st, predict_median_st, predict_median_st, interpolated_survival_curve

def f(x):
    return x*x

def predict_mean_st_old(
        survival_curve: np.ndarray,
        times_coordinate: np.ndarray,
        interpolation: str = "Linear"
) -> float:
    """
    Get the mean survival time from the survival curve. The mean survival time is defined as the area under the survival
    curve. The curve is first interpolated by the given monotonic cubic interpolation method (Linear or Pchip). Then the
    curve gets extroplated by the linear function of (0, 1) and the last time point. The area is calculated by the
    trapezoidal rule.
    Parameters
    ----------
    survival_curve: np.ndarray
        The survival curve of the sample. 1-D array.
    times_coordinate: np.ndarray
        The time coordinate of the survival curve. 1-D array.
    interpolation: str
        The monotonic cubic interpolation method. One of ['Linear', 'Pchip']. Default: 'Linear'.
        If 'Linear', use the interp1d method from scipy.interpolate.
        If 'Pchip', use the PchipInterpolator from scipy.interpolate.
    Returns
    -------
    mean_survival_time: float
        The mean survival time.
    """
    # deprecated warning
    warnings.warn("This function is deprecated. Use 'predict_mean_st' instead.", DeprecationWarning)

    # If all the predicted probabilities are 1 the integral will be infinite.
    if np.all(survival_curve == 1):
        warnings.warn("All the predicted probabilities are 1, the integral will be infinite.")
        return np.inf

    spline = interpolated_survival_curve(times_coordinate, survival_curve, interpolation)

    # predicting boundary
    max_time = float(max(times_coordinate))

    # simply calculate the slope by using the [0, 1] - [max_time, S(t|x)]
    slope = (1 - np.array(spline(max_time)).item()) / (0 - max_time)

    # zero_probability_time = min(times_coordinate[np.where(survival_curve == 0)],
    #                             max_time + (0 - np.array(spline(max_time)).item()) / slope)
    if 0 in survival_curve:
        zero_probability_time = min(times_coordinate[np.where(survival_curve == 0)])
    else:
        zero_probability_time = max_time + (0 - np.array(spline(max_time)).item()) / slope

    def _func_to_integral(time, maximum_time, slope_rate):
        return np.array(spline(time)).item() if time < maximum_time else (1 + time * slope_rate)
    # _func_to_integral = lambda time: spline(time) if time < max_time else (1 + time * slope)
    # limit controls the subdivision intervals used in the adaptive algorithm.
    # Set it to 1000 is consistent with Haider's R code
    mean_survival_time, *rest = integrate.quad(_func_to_integral, 0, zero_probability_time,
                                               args=(max_time, slope), limit=1000)
    return mean_survival_time


if __name__ == '__main__':
    # generate some random points
    logits = np.random.weibull(a=1, size=2000).reshape(100, 20)
    # geenrate pdf using softmax
    pdf = np.exp(logits) / np.exp(logits).sum(axis=1)[:, None]
    surv = 1 - np.cumsum(pdf, axis=1)
    surv = surv[:, :10]

    # generate some random time points
    time_points = np.random.uniform(0, 6, size=1000).reshape(100, 10)
    time_points = np.cumsum(time_points, axis=1)

    # add 1 at the start of the surv and add 0 at the start of time_points
    surv = np.concatenate([np.ones((100, 1)), surv], axis=1)
    time_points = np.concatenate([np.zeros((100, 1)), time_points], axis=1)

    # add a all 1s surv at the end
    surv = np.concatenate([surv, np.ones((1, 11))], axis=0)
    time_points = np.concatenate([time_points, time_points[-1, :].reshape(1, -1)], axis=0)

    start = time.time()
    rmst = predict_rmst(surv, time_points)
    end = time.time()
    print(f"Time taken for RMST: {end - start}")
    rmst_ = np.empty_like(rmst)
    for i in range(surv.shape[0]):
        rmst_[i] = predict_rmst(surv[i], time_points[i])
    assert np.all(rmst == rmst_), "RMST is not correct."

    start = time.time()
    mean_st = predict_mean_st(surv, time_points)
    end = time.time()
    print(f"Time taken for mean survival time: {end - start}")
    strat = time.time()
    mean_st_ = np.empty_like(mean_st)
    for i in range(surv.shape[0]):
        mean_st_[i] = predict_mean_st_old(surv[i], time_points[i])
    end = time.time()
    print(f"Time taken for mean survival time: {end - start}")

    # assert np.all(mean_st == mean_st_), "Mean survival time is not correct."

    start = time.time()
    median_st = predict_median_st(surv, time_points)
    end = time.time()
    median_st_ = np.empty_like(mean_st_)
    for i in range(surv.shape[0]):
        median_st_[i] = predict_median_st(surv[i], time_points[i])
    print(f"Time taken for median survival time: {end - start}")







