import numpy as np
import matplotlib.pyplot as plt
from IPython.core.pylabtools import figsize
from scipy.stats import gaussian_kde
from scipy.integrate import cumulative_trapezoid
import math
import seaborn as sns
import matplotlib.patches as patches
import matplotlib.lines as mlines

color_list = sns.color_palette("deep", 6)


plt.style.use('seaborn-v0_8-paper')
plt.rc('axes', titlesize=9.5)     # fontsize of the axes title
plt.rc('axes', labelsize=9.5)    # fontsize of the x and y labels
# plt.rc('xtick', labelsize=10)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=10)    # fontsize of the tick labels
plt.rc('legend', fontsize=9.5)    # legend fontsize
plt.rc('figure', titlesize=9.5)  # fontsize of the figure title

plt.rcParams['font.size'] = 12


e_1 = 1.5
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



fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(9.6, 7.5/3))

# axes[0].axhline(0.5, ls='dashdot', c='grey')
# axes[0].axvline(e_1, ls='--', c=color_list[0], alpha=0.5)
axes[0].plot(dist_space, 1 - cdf_1, label='Patient A', c=color_list[0])
# axes[0].plot(e_1, -0.05, marker='*', markersize=12, c=color_list[0], clip_on=False, zorder=10)
# axes[0].plot(dist_space[np.where(cdf_1>0.5)[0][0]], 0.5, marker='v', markersize=10, c=color_list[0])
# axes[0].plot(1, 0.15, marker='*', markersize=9, c=color_list[0])
# axes[0].plot(1.2, 0.15, marker='*', markersize=9, c=color_list[1])
axes[0].grid(False)
axes[0].set_ylim([-0.05, 1.05])
axes[0].set_yticks([0, 0.5, 1])
axes[0].set_title('(a) Survival Function', weight='bold')
axes[0].set_xlabel('time')
axes[0].set_ylabel('Probability')


axes[1].axvline(2, ymax=1 - cdf_1[2000], ls='--', c=color_list[5])
axes[1].axhline(1 - cdf_1[2000], xmax=2/3, ls='--', c=color_list[5])
axes[1].plot(2, 1 - cdf_1[2000], marker='v', markersize=10, c=color_list[0])
axes[1].plot(dist_space, 1 - cdf_1, label='Patient A', c=color_list[0])
axes[1].grid(False)
axes[1].set_ylim([-0.05, 1.05])
axes[1].set_yticks([0, 0.5, 1])
axes[1].set_title('(b) Survival Probability', weight='bold')
axes[1].set_xlabel('time')
axes[1].set_ylabel('Probability')


axes[2].axhline(0.5, xmax=dist_space[np.where(cdf_1>0.5)[0][0]]/3.1, ls='dashdot', c='grey')
axes[2].axvline(dist_space[np.where(cdf_1 > 0.5)[0][0]], ymax=0.5, ls='--', c=color_list[0], alpha=0.5)
axes[2].plot(dist_space[np.where(cdf_1>0.5)[0][0]], 0.5, marker='v', markersize=10, c=color_list[0], label=r'Predict $\hat{t}_i$')
axes[2].plot(dist_space, 1 - cdf_1, label='Patient A', c=color_list[0])
axes[2].fill_between(dist_space, 0, 1 - cdf_1, alpha=0.1, color=color_list[0])

axes[2].grid(False)
axes[2].set_ylim([-0.05, 1.05])
axes[2].set_yticks([0, 0.5, 1])
axes[2].set_title('(c) Survival Times', weight='bold')
axes[2].set_xlabel('time')
axes[2].set_ylabel('Probability')

# lines.append(black_star)
# lines.append(black_trangle)
# labels.append(r'True $t_i$')
# labels.append(r'Predictions')
# lgd = fig.legend(lines, labels, bbox_to_anchor=(0.88, 0.02), prop={'size': 9.5}, ncol=6)

# plt.axhline(0.5, ls='--', c='grey')
# plt.legend()
plt.tight_layout()

# plt.show()
# plt.savefig('Figs/all_metrics.pdf', dpi=400, bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig('Figs/output_types.png', dpi=400, bbox_inches='tight',
            transparent=False)

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(6, 2.5))

# ax0 is the cdf function
axes[0].plot(dist_space, cdf_1, label='Patient A', c=color_list[0])
axes[0].plot(dist_space, dist_space, ls='--', c='black')
axes[0].set_ylim([-0.05, 1.05])
axes[0].set_yticks([0, 0.5, 1])
axes[0].set_title('(a) Cumulative Distribution Function', weight='bold')
axes[0].set_xlabel('time')
axes[0].set_ylabel('Probability')
# ax1 is the quantile function
axes[1].plot(cdf_1, dist_space, label='Patient A', c=color_list[0])
axes[1].plot(np.linspace(0, 1.5, 1000), np.linspace(0, 1.5, 1000), ls='--', c='black')
axes[1].set_xlim([-0.05, 1.05])
axes[1].set_xticks([0, 0.5, 1])
axes[1].set_yticks([0, 1, 2, 3])
axes[1].set_title('(b) Quantile Function', weight='bold')
axes[1].set_xlabel('Probability')
axes[1].set_ylabel('time')

plt.tight_layout()
plt.savefig('Figs/output_types_cdf_quantile.png', dpi=400, bbox_inches='tight',
            transparent=False)
