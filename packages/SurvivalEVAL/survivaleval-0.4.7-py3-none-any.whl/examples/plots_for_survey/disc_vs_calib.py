#%% Discrimination vs Calibration
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from scipy.integrate import cumtrapz
import math
import seaborn as sns
import matplotlib.patches as patches
import matplotlib.lines as mlines


color_list = sns.color_palette("colorblind", 10)
custom_params = {"axes.spines.right": False, "axes.spines.top": False,}
sns.set_theme(style="white", rc=custom_params)

# sns.set_theme(style="whitegrid")
# plt.style.use('fivethirtyeight')
# plt.rcParams["figure.figsize"] = (5, 5)
plt.rc('axes', titlesize=10)     # fontsize of the axes title
plt.rc('axes', labelsize=10)    # fontsize of the x and y labels
# plt.rc('xtick', labelsize=10)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=10)    # fontsize of the tick labels
plt.rc('legend', fontsize=10)    # legend fontsize
plt.rc('figure', titlesize=10)  # fontsize of the figure title
height_unit = 2.4
width_unit = 2.8
plt.rcParams['font.size'] = 12


def weibull_pdf(x, scale, shape):
    return (shape / scale) * (x / scale)**(shape - 1) * np.exp(-(x / scale)**shape)


def gamma_pdf(x, scale, shape):
    return (x ** (shape - 1) * np.exp(-x / scale)) / (math.gamma(shape) * scale ** shape)


def lognormal_pdf(x, mu, sigma):
    return (1 / (x * sigma * np.sqrt(2 * np.pi))) * np.exp(-(np.log(x) - mu) ** 2 / (2 * sigma ** 2))


e_1 = 2.7
e_2 = 1.5
e_3 = 0.6
e_4 = 2.1
end_time = 3
N = 100000

# ISD figures and event times
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(width_unit*3, height_unit))

# good Cindex but poor calibration
s1 = 0.5 * np.random.weibull(a=1, size=int(0.55*N))   # generate your data sample with N elements
s2 = 2.5 * np.random.weibull(a=7, size=int(0.45*N))
sample_all = np.append(s1, s2)
kde = gaussian_kde(sample_all)
# these are the values over which your kernel will be evaluated
dist_space = np.arange(0, end_time, 0.001)
p_1 = kde(dist_space)
# plt.plot( dist_space, pdf )
cdf_1 = cumtrapz(p_1, dist_space, initial=0)
death_idx_1 = int(e_1/0.001)
# ab_1 = AnnotationBbox(death_imagebox, (e_1, 1 - cdf_1[death_idx_1]), frameon = False)

p_2 = weibull_pdf(dist_space, 0.5, 1.1)
cdf_2 = cumtrapz(p_2, dist_space, initial=0)
death_idx_2 = int(e_2/0.001)
p_3 = gamma_pdf(dist_space, 0.2, 1)
cdf_3 = cumtrapz(p_3, dist_space, initial=0)
death_idx_3 = int(e_3/0.001)
p_4 = lognormal_pdf(dist_space, 0.002, 0.1)
p_4[0] = 0
cdf_4 = cumtrapz(p_4, dist_space, initial=0)
death_idx_4 = int(e_4/0.001)


axes[0].plot(dist_space, 1 - cdf_1, c=color_list[0], linewidth=2, clip_on=False)
axes[0].plot(dist_space, 1 - cdf_2, c=color_list[1], linewidth=2, clip_on=False)
axes[0].plot(dist_space, 1 - cdf_3, c=color_list[2], linewidth=2, clip_on=False)
axes[0].plot(dist_space, 1 - cdf_4, c=color_list[3], linewidth=2, clip_on=False)
axes[0].plot(e_1, 1 - cdf_1[death_idx_1], marker='*', label='A', markersize=12, c=color_list[0], clip_on=False, zorder=10)
axes[0].plot(e_2, 1 - cdf_2[death_idx_2], marker='*', label='B', markersize=12, c=color_list[1], clip_on=False, zorder=10)
axes[0].plot(e_3, 1 - cdf_3[death_idx_3], marker='*', label='C', markersize=12, c=color_list[2], clip_on=False, zorder=10)
axes[0].plot(e_4, 1 - cdf_4[death_idx_4], marker='*', label='D', markersize=12, c=color_list[3], clip_on=False, zorder=10)
# axes.axhline(0.5, ls='dashdot', c='grey', label='50% Prob.')

axes[0].grid(axis='y')
axes[0].set_ylim([-0.0, 1.0])
axes[0].set_xlim([0, end_time])
axes[0].set_xlabel('Days')
axes[0].set_ylabel('Survival Probability')

# poor C-index but good calibration
s1 = 0.4 * np.random.weibull(a=1, size=int(0.7*N))   # generate your data sample with N elements
s2 = 3.3 * np.random.weibull(a=7, size=int(0.3*N))
sample_all = np.append(s1, s2)
kde = gaussian_kde(sample_all)
# these are the values over which your kernel will be evaluated
dist_space = np.arange(0, end_time, 0.001)
p_1 = kde(dist_space)
# plt.plot( dist_space, pdf )
cdf_1 = cumtrapz(p_1, dist_space, initial=0)
death_idx_1 = int(e_1/0.001)
# ab_1 = AnnotationBbox(death_imagebox, (e_1, 1 - cdf_1[death_idx_1]), frameon = False)

p_2 = weibull_pdf(dist_space, 2, 2)
cdf_2 = cumtrapz(p_2, dist_space, initial=0)
death_idx_2 = int(e_2/0.001)
p_3 = gamma_pdf(dist_space, 1.2, 2.7)
cdf_3 = cumtrapz(p_3, dist_space, initial=0)
death_idx_3 = int(e_3/0.001)
p_4 = lognormal_pdf(dist_space, 0.1, 0.5)
p_4[0] = 0
cdf_4 = cumtrapz(p_4, dist_space, initial=0)
death_idx_4 = int(e_4/0.001)

axes[1].plot(dist_space, 1 - cdf_1, c=color_list[0], linewidth=2, clip_on=False)
axes[1].plot(dist_space, 1 - cdf_2, c=color_list[1], linewidth=2, clip_on=False)
axes[1].plot(dist_space, 1 - cdf_3, c=color_list[2], linewidth=2, clip_on=False)
axes[1].plot(dist_space, 1 - cdf_4, c=color_list[3], linewidth=2, clip_on=False)
axes[1].plot(e_1, 1 - cdf_1[death_idx_1], marker='*', label='A', markersize=12, c=color_list[0], clip_on=False, zorder=10)
axes[1].plot(e_2, 1 - cdf_2[death_idx_2], marker='*', label='B', markersize=12, c=color_list[1], clip_on=False, zorder=10)
axes[1].plot(e_3, 1 - cdf_3[death_idx_3], marker='*', label='C', markersize=12, c=color_list[2], clip_on=False, zorder=10)
axes[1].plot(e_4, 1 - cdf_4[death_idx_4], marker='*', label='D', markersize=12, c=color_list[3], clip_on=False, zorder=10)
# axes.axhline(0.5, ls='dashdot', c='grey', label='50% Prob.')

axes[1].grid(axis='y')
axes[1].set_ylim([-0.0, 1.0])
axes[1].set_xlim([0, end_time])
axes[1].set_yticks([0, 0.25, 0.5, 0.75, 1])
axes[1].set_xlabel('Days')
axes[1].set_ylabel('Survival Probability')


# good C-index and calibration
s1 = 0.5 * np.random.weibull(a=1, size=int(0.23*N))   # generate your data sample with N elements
s2 = 3.2 * np.random.weibull(a=7, size=int(0.77*N))
sample_all = np.append(s1, s2)
kde = gaussian_kde(sample_all)
# these are the values over which your kernel will be evaluated
dist_space = np.arange(0, end_time, 0.001)
p_1 = kde(dist_space)
# plt.plot( dist_space, pdf )
cdf_1 = cumtrapz(p_1, dist_space, initial=0)
death_idx_1 = int(e_1/0.001)
# ab_1 = AnnotationBbox(death_imagebox, (e_1, 1 - cdf_1[death_idx_1]), frameon = False)

p_2 = weibull_pdf(dist_space, 1.5, 1.5)
cdf_2 = cumtrapz(p_2, dist_space, initial=0)
death_idx_2 = int(e_2/0.001)
p_3 = gamma_pdf(dist_space, 0.15, 2)
cdf_3 = cumtrapz(p_3, dist_space, initial=0)
death_idx_3 = int(e_3/0.001)
p_4 = lognormal_pdf(dist_space, 0.9, 0.15)
p_4[0] = 0
cdf_4 = cumtrapz(p_4, dist_space, initial=0)
death_idx_4 = int(e_4/0.001)

axes[2].plot(dist_space, 1 - cdf_1, c=color_list[0], linewidth=2, clip_on=False)
axes[2].plot(dist_space, 1 - cdf_2, c=color_list[1], linewidth=2, clip_on=False)
axes[2].plot(dist_space, 1 - cdf_3, c=color_list[2], linewidth=2, clip_on=False)
axes[2].plot(dist_space, 1 - cdf_4, c=color_list[3], linewidth=2, clip_on=False)
axes[2].plot(e_1, 1 - cdf_1[death_idx_1], marker='*', label='A', markersize=12, c=color_list[0], clip_on=False, zorder=10)
axes[2].plot(e_2, 1 - cdf_2[death_idx_2], marker='*', label='B', markersize=12, c=color_list[1], clip_on=False, zorder=10)
axes[2].plot(e_3, 1 - cdf_3[death_idx_3], marker='*', label='C', markersize=12, c=color_list[2], clip_on=False, zorder=10)
axes[2].plot(e_4, 1 - cdf_4[death_idx_4], marker='*', label='D', markersize=12, c=color_list[3], clip_on=False, zorder=10)
# axes.axhline(0.5, ls='dashdot', c='grey', label='50% Prob.')

axes[2].grid(axis='y')
axes[2].set_ylim([-0.0, 1.0])
axes[2].set_xlim([0, end_time])
axes[2].set_xlabel('Days')
axes[2].set_ylabel('Survival Probability')

# axes[0].legend(loc='lower center', bbox_to_anchor=(0.5, 1.02), fancybox=True,
#              ncols=2,)
plt.tight_layout()
plt.savefig(f'figs/illustration/disc_vs_cal.png', dpi=400, transparent=True)
