import lifelines
from lifelines import CoxPHFitter
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from scipy.integrate import cumulative_trapezoid
import math
import seaborn as sns
from sympy.printing.pretty.pretty_symbology import line_width

from SurvivalEVAL import LifelinesEvaluator


plt.style.use('seaborn-v0_8-paper')
plt.rcParams["figure.figsize"] = (8, 3.5)
plt.rc('axes', titlesize=9.5)     # fontsize of the axes title
plt.rc('axes', labelsize=9.5)    # fontsize of the x and y labels
# plt.rc('xtick', labelsize=10)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=10)    # fontsize of the tick labels
plt.rc('legend', fontsize=9.5)    # legend fontsize
plt.rc('figure', titlesize=9.5)  # fontsize of the figure title

plt.rcParams['font.size'] = 12

#%% 4 patients ISD
color_list = sns.color_palette("deep", 6)
# custom_params = {"axes.spines.right": False, "axes.spines.top": False,}
# sns.set_theme(style="white")

height_unit = 3
width_unit = 3.5


def weibull_pdf(x, scale, shape):
    return (shape / scale) * (x / scale)**(shape - 1) * np.exp(-(x / scale)**shape)


def gamma_pdf(x, scale, shape):
    return (x ** (shape - 1) * np.exp(-x / scale)) / (math.gamma(shape) * scale ** shape)


def lognormal_pdf(x, mu, sigma):
    return (1 / (x * sigma * np.sqrt(2 * np.pi))) * np.exp(-(np.log(x) - mu) ** 2 / (2 * sigma ** 2))


e_1 = 1.5
e_2 = 1.8
e_3 = 0.8
e_4 = 2.15
end_time = 3
N = 100000
s1 = 0.5 * np.random.weibull(a=1, size=int(0.4*N))   # generate your data sample with N elements
s2 = 2.8 * np.random.weibull(a=7, size=int(0.6*N))
sample_all = np.append(s1, s2)
kde = gaussian_kde(sample_all)
# these are the values over which your kernel will be evaluated
dist_space = np.arange(0, end_time, 0.001)
p_1 = kde(dist_space)
# plt.plot( dist_space, pdf )
cdf_1 = cumulative_trapezoid(p_1, dist_space, initial=0)
death_idx_1 = int(e_1/0.001)
# ab_1 = AnnotationBbox(death_imagebox, (e_1, 1 - cdf_1[death_idx_1]), frameon = False)

p_2 = weibull_pdf(dist_space, 1.1, 2)
cdf_2 = cumulative_trapezoid(p_2, dist_space, initial=0)
death_idx_2 = int(e_2/0.001)
p_3 = gamma_pdf(dist_space, 0.6, 3)
cdf_3 = cumulative_trapezoid(p_3, dist_space, initial=0)
death_idx_3 = int(e_3/0.001)
p_4 = lognormal_pdf(dist_space, 0.7, 0.2)
p_4[0] = 0
cdf_4 = cumulative_trapezoid(p_4, dist_space, initial=0)
death_idx_4 = int(e_4/0.001)

# D-calibration figures
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(width_unit*2.5, height_unit))

# d-calibration
ax[0].plot(dist_space, 1 - cdf_1, label='Patient A', c=color_list[0], linewidth=2, clip_on=False, zorder=10)
ax[0].plot(dist_space, 1 - cdf_2, label='Patient B', c=color_list[1], linewidth=2, clip_on=False, zorder=10)
ax[0].plot(dist_space, 1 - cdf_3, label='Patient C', c=color_list[2], linewidth=2, clip_on=False, zorder=10)
ax[0].plot(dist_space, 1 - cdf_4, label='Patient D', c=color_list[3], linewidth=2, clip_on=False, zorder=10)
ax[0].plot(e_1, 1 - cdf_1[death_idx_1], marker='^', markersize=10, c=color_list[0])
ax[0].plot(e_2, 1 - cdf_2[death_idx_2], marker='v', markersize=10, c=color_list[1])
ax[0].plot(e_3, 1 - cdf_3[death_idx_3], marker='v', markersize=10, c=color_list[2])
ax[0].plot(e_4, 1 - cdf_4[death_idx_4], marker='v', markersize=10, c=color_list[3])

ax[0].grid(False)
# ax[1, 2].spines.set_color('black')
ax[0].set_ylim([0, 1])
ax[0].set_xlim([0, end_time])
ax[0].set_yticks([0, 0.25, 0.5, 0.75, 1])
ax[0].set_xlabel('Days')
ax[0].set_ylabel('Survival Probability')
ax[0].set_title('(a) Prediction')

probs_at_event = np.array([1 - cdf_1[death_idx_1],
                           1 - cdf_2[death_idx_2],
                           1 - cdf_3[death_idx_3],
                           1 - cdf_4[death_idx_4]])
probs ={
    'Null': np.array([0, 0, 0, 0]),
    'B': np.array([1, 0, 0, 0]),
    'C': np.array([0, 0, 0, 1]),
    'D': np.array([0, 1, 0, 0]),
    'A': np.array([0.25 / (1 - cdf_1[death_idx_1]), 0.25 / (1 - cdf_1[death_idx_1]),
                   (1 - cdf_1[death_idx_1] - 0.5) / (1 - cdf_1[death_idx_1]), 0]),
}
left = np.zeros_like(probs_at_event)

for i, (key, value) in enumerate(probs.items()):
    if key == 'A':
        i = 0
    ax[1].barh([0, 0.25, 0.5, 0.75], value, height=0.25, color=color_list[i], label=key,
              align='edge', edgecolor='black', left=left, linewidth=1)
    left += value
# ax[1].hist(probs_at_event, bins=[0, 0.25, 0.5, 0.75, 1], color=color_list[5], rwidth=1, orientation='horizontal')
ax[1].set_ylim([0, 1])
ax[1].axvline(1, ls='dashed', c='grey', label='Perfect Cal.')
ax[1].set_xlabel('Counts')
# ax[1].set_ylabel('Survival Probability')
ax[1].grid(False)
ax[1].set_xlim([0, 2.5])
ax[1].set_xticks([0, 1, 2])
ax[1].set_xticklabels([0, 1, 2])
ax[1].set_yticks([0, 0.25, 0.5, 0.75, 1])
# ax[1].legend(loc='lower right')
ax[1].set_title('(b) D-calibration Histogram')

# hist = np.histogram(probs_at_event, bins=[0, 0.25, 0.5, 0.75, 1])
probs = left / 4
cum_probs = np.cumsum(probs)
cum_probs = np.insert(cum_probs, 0, 0)
ax[2].plot([0, 1], [0, 1], ls='dashed', c='grey', label='Ideal')
ax[2].plot([0, 0.25, 0.5, 0.75, 1], cum_probs, marker='o', markersize=8, c='skyblue', linewidth=2,
              clip_on=False, zorder=10)
ax[2].set_ylim([0, 1])
ax[2].set_xlim([0.0, 1.0])
ax[2].set_xticks([0, 0.25, 0.5, 0.75, 1])
ax[2].set_yticks([0, 0.25, 0.5, 0.75, 1])
ax[2].set_xlabel('Predicted Survival Probability')
ax[2].set_ylabel('Observed Survival Probability')
ax[2].grid(False)
ax[2].legend(loc='lower right')
ax[2].set_title('(c) D-calibration P-P Plot')


plt.tight_layout()
plt.savefig(f'd-cal_censor.png', dpi=400, transparent=True)

#%% real data example

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

# pass to evaluator
evler = LifelinesEvaluator(survs_cox, df_test['time'].values, df_test['event'].values)

# ==============================================================================
# residuals
p_value, combined_binning = evler.d_calibration(10)
predict_probs = combined_binning / combined_binning.sum()  # normalize the counts to get probabilities

# probs_at_event = combined_binning / combined_binning.sum()
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(7, 3))

# sideway histogram using combined binning
bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
#combined_binning has a size of 10, each one indicate the counts of the bin
ax[0].barh(bins[:-1], predict_probs, height=0.1, color='#CDE7F0', align='edge', edgecolor='black', label='Counts',
           linewidth=1)
# ax[0].hist(predict_probs, bins=bins, color=color_list[5], rwidth=1, orientation='horizontal', density=True)
# ax[0].set_ylim([-0.05, 1.05])
ax[0].axvline(0.1, ls='dashed', c='grey', label='Perfect Cal.')
ax[0].set_xlabel('Proportion')
ax[0].set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
# ax[0].set_ylabel('Survival Probability')
ax[0].grid(False)
# ax[0].set_xlim([0, 0.15])
ax[0].set_xticks([0, 0.05, 0.1, 0.15])
ax[0].set_xticklabels(['0%', '5%', '10%', '15%'])
# ax[0].legend(loc='lower right')
ax[0].set_ylabel('Predicted Survival Probability')
ax[0].set_title('(a) D-calibration Histogram')

# p-p calibration curve

cum_probs = np.cumsum(predict_probs)
cum_probs = np.insert(cum_probs, 0, 0)
ax[1].plot([0, 1], [0, 1], ls='dashed', c='grey', label='Ideal')
ax[1].plot(bins, cum_probs, marker='o', markersize=8, c='skyblue', linewidth=2,
              clip_on=False, zorder=10)
ax[1].text(0.05, 0.95, f'p-value: {p_value:.3f}', fontsize=9.5, color='black', ha='left', va='top')
# ax[1].set_ylim([-0.05, 1.05])
# ax[1].set_xlim([-0.0, 1.0])
ax[1].set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1])
ax[1].set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
ax[1].set_xlabel('Predicted Survival Probability')
ax[1].set_ylabel('Observed Survival Probability')
ax[1].grid(False)
ax[1].legend(loc='lower right')
ax[1].set_title('(b) D-calibration P-P Plot')

plt.tight_layout()
plt.savefig('d-cal_cox.png', dpi=400)
