# This code is originally from paper:
# Graphical calibration curves and the integrated calibration index (ICI) for survival models
# And its original R code is in Appendix A (using splines)
# we choose the implementation using splines + CoxPH (instead of the hazard regression) because
# (1) the two methods can compariable performance and the difference is negligible (support by the paper)
# (2) as far as I know, there is no implementation of flexible adaptive hazard regression in Python
# Import necessary libraries for data handling, modeling, and plotting
import pandas as pd
import numpy as np
import lifelines
from lifelines import CoxPHFitter, WeibullAFTFitter
from patsy import dmatrix  # For spline basis matrix
import matplotlib.pyplot as plt  # For plotting
from scipy.stats import gaussian_kde  # For density plot

# ==============================================================================
# 1. Load the Data
# ==============================================================================
data = lifelines.datasets.load_gbsg2()
# preprocessing
data.rename(columns={'cens': 'event'}, inplace=True)
data['horTh'] = data['horTh'].map({'no': 0, 'yes': 1})
data['menostat'] = data['menostat'].map({'Pre': 0, 'Post': 1})
data['tgrade'] = data['tgrade'].map({'I': 1, 'II': 2, 'III': 3})
# randomly divide the data into training and validation sets
df_train = data.sample(frac=0.7, random_state=42)  # 70% for training
df_train = df_train.reset_index(drop=True)
df_test = data.drop(df_train.index)  # remaining 30% for testing
df_test = df_test.reset_index(drop=True)
x_test = df_test.drop(columns=['time', 'event']).values

# ==============================================================================
# 2. Fit a Cox Proportional Hazards Model
# ==============================================================================
cph = CoxPHFitter()
cph.fit(df_train, duration_col='time', event_col='event')

# Define time points for 1, 2, 3, 4, 5, 6 years (in days)
times = 365 * np.arange(1, 7)

# Predict the survival probability at the given time points
survs_cox = cph.predict_survival_function(x_test, times=[365]).T.values
cdfs_cox = 1 - survs_cox

# calculate the complementary log-log (CLL) transformation of the predicted probabilities
clls_cox = np.log(-np.log(survs_cox))

# ==============================================================================
# 4. Calibration: Fit Cox Models to the CLL-Transformed Predictions Using Splines
# ==============================================================================

spline_from_cox = dmatrix("bs(x, df=3, degree=3, include_intercept=False)", {"x": clls_cox}, return_type='dataframe')
design_info = spline_from_cox.design_info
df_cox = pd.concat([df_test[['time', 'event']], spline_from_cox], axis=1)
cal_cox = CoxPHFitter().fit(df_cox, duration_col='time', event_col='event')

# grid_cox = np.linspace(cdfs_cox[:, 0].quantile(0.01), cdfs_cox[:, 0].quantile(0.99), 100)
grid_cox = np.linspace(np.quantile(cdfs_cox, 0.01), np.quantile(cdfs_cox, 0.99), 100)
grid_cox_cll = np.log(-np.log(1 - grid_cox))
spline_grid_cox = dmatrix(design_info, {"x": grid_cox_cll}, return_type='dataframe')
cal_cox_pred = 1 - cal_cox.predict_survival_function(spline_grid_cox, times=[365]).T.values

# ==============================================================================
# 5. Plot Calibration Curve
# ==============================================================================
plt.figure(figsize=(8, 6))
plt.plot(grid_cox, cal_cox_pred, 'r-', label='Cox (calibrated)')
# plt.plot(grid_forest, cal_forest_pred, 'b--', label='Forest (calibrated)')
plt.plot([0,1], [0,1], 'k:', label='Ideal')  # 45-degree line: perfect calibration
plt.xlabel('Predicted probability of 1-year mortality')
plt.ylabel('Observed probability of 1-year mortality')
plt.title('1-year mortality')
plt.legend()
plt.show()

# Overlay density of Cox 1-year predicted probabilities
plt.figure()
kde = gaussian_kde(cdfs_cox[:, 0])
xvals = np.linspace(0, 1, 100)
plt.plot(xvals, kde(xvals))
plt.ylabel("Density")
plt.title("Density of Cox 1-year predicted probabilities")
plt.show()

# ==============================================================================
# 6. Calculate ICI, E50, E90 for 1-year Predictions
# ==============================================================================
# Compute calibrated predictions for the validation set
spline_val_cox = dmatrix(design_info, {"x": clls_cox}, return_type='dataframe')
# Calibrated observed probability of death within 1 year
cal_pred_cox = 1 - cal_cox.predict_survival_function(spline_val_cox, times=[365]).T.values

# Compute calibration metrics for Cox and Forest predictions
abs_err = np.abs(cdfs_cox - cal_pred_cox)
ici = abs_err.mean()
e50 = np.median(abs_err)
e90 = np.quantile(abs_err, 0.9)


