import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import lifelines
from lifelines import CoxPHFitter

from SurvivalEVAL import LifelinesEvaluator
from SurvivalEVAL.NonparametricEstimator.SingleEvent import  NelsonAalen

color_list = sns.color_palette(n_colors=6)

plt.style.use('seaborn-v0_8-paper')
plt.rcParams["figure.figsize"] = (8, 3.5)
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
survs_cox = cph.predict_survival_function(x_test)

eval = LifelinesEvaluator(survs_cox, df_test['time'].values, df_test['event'].values,
                          predict_time_method='Median')

p, stats = eval.log_rank()
print(f'Log-rank test p-value: {p}, statistic: {stats}')
p, stats = eval.log_rank(weightings='wilcoxon')
print(f'Log-rank test p-value: {p}, statistic: {stats}')
p, stats = eval.log_rank(weightings='tarone-ware')
print(f'Log-rank test p-value: {p}, statistic: {stats}')
p, stats = eval.log_rank(weightings='peto')
print(f'Log-rank test p-value: {p}, statistic: {stats}')
p, stats = eval.log_rank(weightings='fleming-harrington', p=0.1, q=2)
print(f'Log-rank test p-value: {p}, statistic: {stats}')

pred_times = eval.predicted_event_times
cum_haz_empirical = NelsonAalen(df_test['time'].values, df_test['event'].values)
cum_haz_pred = NelsonAalen(pred_times, np.ones_like(df_test['event'].values, dtype=bool))
max_x = np.max(df_test['time'].values)
max_y = np.max(cum_haz_empirical.cumulative_hazard)

fig, ax = plt.subplots(nrows=1, ncols=1, tight_layout=True, dpi=400, figsize=(3.2, 3),)
ax.plot(cum_haz_empirical.survival_times, cum_haz_empirical.cumulative_hazard, color='grey', label='ideal (NA)', linewidth=2, linestyle='dashed')
ax.plot(cum_haz_pred.survival_times, cum_haz_pred.cumulative_hazard, color='skyblue', label='predicted', linewidth=2)
ax.legend()
ax.set_xlim(- max_x * 0.05, max_x * 1.05)
ax.set_ylim(- max_y * 0.05, max_y * 1.05)
ax.set_xlabel('Time (days)')
ax.set_ylabel('Cumlative hazard')
plt.savefig('log_rank_test.png', dpi=400)

