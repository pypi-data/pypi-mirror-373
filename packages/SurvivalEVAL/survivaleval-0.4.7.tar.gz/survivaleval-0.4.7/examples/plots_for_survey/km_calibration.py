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
from lifelines import CoxPHFitter, KaplanMeierFitter
from matplotlib.axis import Axis
from matplotlib.spines import Spine

from SurvivalEVAL import LifelinesEvaluator

color_list = sns.color_palette(n_colors=6)

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

# Predict the survival probability at the given time points
survs_cox = cph.predict_survival_function(x_test)
times = survs_cox.index.values
# draw the survival curves
fig, ax = plt.subplots(ncols=2, nrows=1, figsize=(6, 2.5))
for i in range(20):
    ax[0].plot(times, survs_cox[i], label=f'Sample {i+1}', color=color_list[i % len(color_list)])
ax[0].set_ylabel('Survival Probability')
ax[0].set_ylim(-0.05, 1.05)
ax[0].set_xlabel('Time (days)')
ax[0].set_title('(a) Sampled Survival Curves')

eval = LifelinesEvaluator(survs_cox, df_test['time'].values, df_test['event'].values)

average_pred_surv = survs_cox.mean(axis=1)
km = KaplanMeierFitter().fit(df_test['time'], df_test['event'])
km_surv = km.survival_function_.values
km_times = km.survival_function_.index.values
ax[1].plot(times, average_pred_surv, label='Average prediction', color='skyblue', linewidth=2)
ax[1].plot(km_times, km_surv, label='Ideal (KM)', color='grey', linestyle='--', linewidth=2)
ax[1].set_ylabel('Survival Probability')
ax[1].set_xlabel('Time (days)')
ax[1].set_ylim(-0.05, 1.05)
ax[1].legend()
ax[1].set_title('(b) KM-calibration')

plt.tight_layout()
plt.savefig('km_calibration.png', dpi=400)