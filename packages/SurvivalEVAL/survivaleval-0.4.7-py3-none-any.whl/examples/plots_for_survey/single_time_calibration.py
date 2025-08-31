import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from scipy.integrate import cumulative_trapezoid
import math
import seaborn as sns
import matplotlib.patches as patches
import matplotlib.lines as mlines
import pandas as pd
import lifelines
from lifelines import CoxPHFitter
from matplotlib.axis import Axis
from matplotlib.spines import Spine

from SurvivalEVAL import SingleTimeEvaluator


plt.style.use('seaborn-v0_8-paper')
plt.rcParams["figure.figsize"] = (7, 3)
plt.rc('axes', titlesize=9.5)     # fontsize of the axes title
plt.rc('axes', labelsize=9.5)    # fontsize of the x and y labels
# plt.rc('xtick', labelsize=10)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=10)    # fontsize of the tick labels
plt.rc('legend', fontsize=9.5)    # legend fontsize
plt.rc('figure', titlesize=9.5)  # fontsize of the figure title

plt.rcParams['font.size'] = 12


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
year = 3  # Set the target year for calibration
# Define time points for 1, 2, 3, 4, 5, 6 years (in days)
times = 365 * year * np.arange(1, 7)

# Predict the survival probability at the given time points
survs_cox = cph.predict_survival_function(x_test, times=[365 * year]).T.values.flatten()

# pass to evaluator
evler = SingleTimeEvaluator(survs_cox, df_test['time'].values, df_test['event'].values, target_time=365 * year)
p_value, obs_probs, exp_probs = evler.one_calibration(num_bins=10, method="DN")
# Returned probability are ranked from high to low. We want to draw the calibration bar plot from low to high.
bins = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

fig, axes = plt.subplots(nrows=1, ncols=2)
bar1 = axes[0].bar([x - 0.2 for x in bins], obs_probs, width=0.4, color='lightsalmon', align='center', edgecolor='k',
                   linewidth=1)
bar2 = axes[0].bar([x + 0.2 for x in bins], exp_probs, width=0.4, color='palegreen', align='center', edgecolor='k',
                   linewidth=1)

axes[0].legend((bar1[0], bar2[0]), ('Observed', 'Expected'))
axes[0].set_xlabel("Stratified Risk Groups")
axes[0].set_ylabel("Probability")
axes[0].set_title("(a) Calibration Histogram")

summary, _ = evler.integrated_calibration_index(draw_figure=False)

# for artist in cal_ax.get_children():
#     # Skip objects that can’t be removed (Axis, Spine, etc.)
#     if isinstance(artist, (Axis, Spine)):
#         continue
#     try:
#         artist.remove()           # detach from old Axes
#     except NotImplementedError:
#         continue                  # defensive: skip any other immovables
#     axes[1].add_artist(artist)     # attach to new Axes
axes[1].plot([0, 1], [0, 1], '--', label='Ideal', color="grey", linewidth=2)
axes[1].plot(exp_probs, obs_probs, 'o-', color='skyblue', label="DN-1-cal", linewidth=2)
axes[1].plot(summary["curve"]["grid"], summary["curve"]["cal_pred"], '-', color='orange', label="Smooth 1-cal", linewidth=2)
axes[1].set_xlabel("Expected Probability")
axes[1].set_ylabel("Observed Probability")
axes[1].set_title("(b) Percentile-Percentile Calibration Curve")
axes[1].legend()
plt.tight_layout()
plt.savefig('single_time_cal.png', dpi=400)


