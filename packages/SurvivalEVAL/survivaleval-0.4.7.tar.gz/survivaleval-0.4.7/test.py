import numpy as np
import warnings
from scipy.interpolate import PchipInterpolator, interp1d

from SurvivalEVAL.Evaluations.util import interpolated_survival_curve, _check_dim_align, predict_median_st_ind

def predict_median_survival_time_new(
        survival_curves: np.ndarray,
        times_coordinates: np.ndarray,
        interpolation: str = "Linear"
) -> float:
    """
    Get the median survival time from the survival curve. The median survival time is defined as the time point where
    the survival curve crosses 0.5. The curve is first interpolated by the given monotonic cubic interpolation method
    (Linear or Pchip). Then the curve gets extroplated by the linear function of (0, 1) and the last time point. The
    median survival time is calculated by finding the time point where the survival curve crosses 0.5.
    Parameters
    ----------
    survival_curves: np.ndarray
        The survival curve of the sample. 1-D array.
    times_coordinates: np.ndarray
        The time coordinate of the survival curve. 1-D array.
    interpolation: str
        The monotonic cubic interpolation method. One of ['None', 'Linear', 'Pchip']. Default: 'Linear'.
        If 'None', use the step function to calculate the median survival time.
        If 'Linear', use the linear equation to solve the median survival time.
        If 'Pchip', use the PchipInterpolator from scipy.interpolate.
    Returns
    -------
    median_survival_time: float
        The median survival time.
    """
    _check_dim_align(survival_curves, times_coordinates)

    ndim_surv = survival_curves.ndim
    ndim_time = times_coordinates.ndim

    # If all the predicted probabilities are 1 the integral will be infinite.
    if np.all(survival_curves == 1):
        warnings.warn("All the predicted probabilities are 1, the median survival time will be infinite.")
        return np.inf

    min_prob = float(min(survival_curves))

    if 0.5 in survival_curves:
        median_probability_time = times_coordinates[np.where(survival_curves == 0.5)[0][0]]
    elif min_prob < 0.5:
        idx_before_median = np.where(survival_curves > 0.5)[0][-1]
        idx_after_median = np.where(survival_curves < 0.5)[0][0]
        min_time_before_median = times_coordinates[idx_before_median]
        max_time_after_median = times_coordinates[idx_after_median]

        if interpolation == "None":
            # find the time point where the survival curve (step function) crosses 0.5
            idx = np.where(survival_curves > 0.5)[0][0]
            median_probability_time = times_coordinates[idx]
        elif interpolation == "Linear":
            # given last time before median and first time after median, solve the linear equation
            slope = ((survival_curves[idx_after_median] - survival_curves[idx_before_median]) /
                     (max_time_after_median - min_time_before_median))
            intercept = survival_curves[idx_before_median] - slope * min_time_before_median
            median_probability_time = (0.5 - intercept) / slope
        elif interpolation == "Pchip":
            # reverse the array because the PchipInterpolator requires the x to be strictly increasing
            spline = interpolated_survival_curve(times_coordinates, survival_curves, interpolation)
            time_range = np.linspace(min_time_before_median, max_time_after_median, num=1000)
            prob_range = spline(time_range)
            inverse_spline = PchipInterpolator(prob_range[::-1], time_range[::-1])
            median_probability_time = np.array(inverse_spline(0.5)).item()
        else:
            raise ValueError("interpolation should be one of ['Linear', 'Pchip']")
    else:
        max_time = float(max(times_coordinates))
        min_prob = float(min(survival_curves))
        slope = (1 - min_prob) / (0 - max_time)
        median_probability_time = - 0.5 / slope
    return median_probability_time


def predict_median_survival_time(
        survival_curve: np.ndarray,
        times_coordinate: np.ndarray,
        interpolation: str = "Linear"
) -> float:
    """
    Get the median survival time from the survival curve. The median survival time is defined as the time point where
    the survival curve crosses 0.5. The curve is first interpolated by the given monotonic cubic interpolation method
    (Linear or Pchip). Then the curve gets extroplated by the linear function of (0, 1) and the last time point. The
    median survival time is calculated by finding the time point where the survival curve crosses 0.5.
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
    median_survival_time: float
        The median survival time.
    """
    # If all the predicted probabilities are 1 the integral will be infinite.
    if np.all(survival_curve == 1):
        warnings.warn("All the predicted probabilities are 1, the median survival time will be infinite.")
        return np.inf

    min_prob = float(min(survival_curve))

    if 0.5 in survival_curve:
        median_probability_time = times_coordinate[np.where(survival_curve == 0.5)[0][0]]
    elif min_prob < 0.5:
        idx_before_median = np.where(survival_curve > 0.5)[0][-1]
        idx_after_median = np.where(survival_curve < 0.5)[0][0]
        min_time_before_median = times_coordinate[idx_before_median]
        max_time_after_median = times_coordinate[idx_after_median]

        if interpolation == "Linear":
            # given last time before median and first time after median, solve the linear equation
            slope = ((survival_curve[idx_after_median] - survival_curve[idx_before_median]) /
                     (max_time_after_median - min_time_before_median))
            intercept = survival_curve[idx_before_median] - slope * min_time_before_median
            median_probability_time = (0.5 - intercept) / slope
        elif interpolation == "Pchip":
            # reverse the array because the PchipInterpolator requires the x to be strictly increasing
            spline = interpolated_survival_curve(times_coordinate, survival_curve, interpolation)
            time_range = np.linspace(min_time_before_median, max_time_after_median, num=1000)
            prob_range = spline(time_range)
            inverse_spline = PchipInterpolator(prob_range[::-1], time_range[::-1])
            median_probability_time = np.array(inverse_spline(0.5)).item()
        else:
            raise ValueError("interpolation should be one of ['Linear', 'Pchip']")
    else:
        max_time = float(max(times_coordinate))
        min_prob = float(min(survival_curve))
        slope = (1 - min_prob) / (0 - max_time)
        median_probability_time = - 0.5 / slope
    return median_probability_time

if __name__ == "__main__":
    # generate random survival curves and time coordinates for testing
    np.random.seed(42)
    logits = np.random.rand(10)
    pdf = logits/ logits.sum()
    survival_curves = 1 - np.cumsum(pdf)
    times_coordinates = np.linspace(0, 10, 10)
    interpolation = "Pchip"

    median_time = predict_median_survival_time(survival_curves, times_coordinates, interpolation)
    print(f"Median Survival Time: {median_time}")
    # Test the new function
    median_time_new = predict_median_survival_time_new(survival_curves, times_coordinates, interpolation)
    print(f"Median Survival Time (new): {median_time_new}")

    median_time_ind = predict_median_st_ind(survival_curves, times_coordinates, interpolation)
    print(f"Median Survival Time (index): {median_time_ind}")