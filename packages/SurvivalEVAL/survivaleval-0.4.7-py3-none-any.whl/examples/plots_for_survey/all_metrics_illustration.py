import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from scipy.integrate import cumulative_trapezoid
import math
import seaborn as sns
import matplotlib.patches as patches
import matplotlib.lines as mlines

# import matplotlib.image as image
# from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
#
# death_img_file = "Figs/illustration/death.png"
# death_img = image.imread(death_img_file)
# death_imagebox = OffsetImage(death_img, zoom = 0.02)

color_list = sns.color_palette("deep", 6)


plt.style.use('seaborn-v0_8-paper')
plt.rcParams["figure.figsize"] = (9.6, 8)
plt.rc('axes', titlesize=9.5)     # fontsize of the axes title
plt.rc('axes', labelsize=9.5)    # fontsize of the x and y labels
# plt.rc('xtick', labelsize=10)    # fontsize of the tick labels
# plt.rc('ytick', labelsize=10)    # fontsize of the tick labels
plt.rc('legend', fontsize=9.5)    # legend fontsize
plt.rc('figure', titlesize=9.5)  # fontsize of the figure title

plt.rcParams['font.size'] = 12


def weibull_pdf(x, scale, shape):
    return (shape / scale) * (x / scale)**(shape - 1) * np.exp(-(x / scale)**shape)

def gamma_pdf(x, scale, shape):
    return (x ** (shape - 1) * np.exp(-x / scale)) / (math.gamma(shape) * scale ** shape)

def lognormal_pdf(x, mu, sigma):
    return (1 / (x * sigma * np.sqrt(2 * np.pi))) * np.exp(-(np.log(x) - mu) ** 2 / (2 * sigma ** 2))

def heaviside(x, time):
    function = np.zeros_like(x)
    function[x < time] = 1
    return function

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


fig, axes = plt.subplots(nrows=3, ncols=3)

# subfigure 0, concordance index
axes[0, 0].axhline(0.5, ls='dashdot', c='grey')
# axes[0, 0].axvline(e_1, ls='--', c=color_list[0], alpha=0.5)
# axes[0, 0].axvline(e_2, ls='--', c=color_list[1], alpha=0.5)
axes[0, 0].plot(dist_space, 1 - cdf_1, label='Patient A', c=color_list[0])
axes[0, 0].plot(dist_space, 1 - cdf_2, label='Patient B', c=color_list[1])
axes[0, 0].plot(e_1, -0.05, marker='*', markersize=12, c=color_list[0], clip_on=False, zorder=10)
axes[0, 0].plot(e_2, -0.05, marker='*', markersize=12, c=color_list[1], clip_on=False, zorder=10)
axes[0, 0].plot(dist_space[np.where(cdf_1>0.5)[0][0]], 0.5, marker='v', markersize=10, c=color_list[0])
axes[0, 0].plot(dist_space[np.where(cdf_2>0.5)[0][0]], 0.5, marker='v', markersize=10, c=color_list[1])
# axes[0, 0].text(-0.05, 0.15, 'True  Risk', fontsize=10, horizontalalignment='left', verticalalignment="center")
axes[0, 0].text(-0.05, 0.05, 'Pred. Order', fontsize=9, horizontalalignment='left', verticalalignment="center")
# axes[0, 0].plot(1, 0.15, marker='*', markersize=9, c=color_list[0])
# axes[0, 0].plot(1.2, 0.15, marker='*', markersize=9, c=color_list[1])
axes[0, 0].plot(1, 0.05, marker='v', markersize=7.5, c=color_list[1])
axes[0, 0].plot(1.2, 0.05, marker='v', markersize=7.5, c=color_list[0])
axes[0, 0].grid(False)
axes[0, 0].set_ylim([-0.05, 1.05])
axes[0, 0].set_yticks([0, 0.5, 1])
axes[0, 0].set_title('(a) C-index', weight='bold')
axes[0, 0].set_xlabel('Year')
axes[0, 0].set_ylabel('Survival Probability')


# subfigure 1, l1 loss
axes[0, 1].axhline(0.5, ls='dashdot', c='grey')
axes[0, 1].axvline(e_1, ls='--', c=color_list[0], alpha=0.5)
axes[0, 1].axvline(dist_space[np.where(cdf_1 > 0.5)[0][0]], ls='--', c=color_list[0], alpha=0.5)
axes[0, 1].plot(dist_space, 1 - cdf_1, label='Patient A', c=color_list[0])
axes[0, 1].plot(e_1, -0.05, marker='*', markersize=12, c=color_list[0], label=r'True $t_i$', clip_on=False, zorder=10)
axes[0, 1].plot(dist_space[np.where(cdf_1>0.5)[0][0]], 0.5, marker='v', markersize=10, c=color_list[0], label=r'Predict $\hat{t}_i$')
curve_arrow = patches.FancyArrowPatch((e_1 - 0.04, 0.35), (dist_space[np.where(cdf_1 > 0.5)[0][0]] + 0.04, 0.35), connectionstyle="arc3,rad=0", arrowstyle='<->', mutation_scale=10, color='black', linewidth=1.5)
axes[0, 1].add_patch(curve_arrow)
axes[0, 1].grid(False)
axes[0, 1].set_ylim([-0.05, 1.05])
axes[0, 1].set_yticks([0, 0.5, 1])
axes[0, 1].set_title('(b) MAE / MSE', weight='bold')
axes[0, 1].set_xlabel('Year')
axes[0, 1].set_ylabel('Survival Probability')

# subfigure 3, log-rank test
# axes[0, 2].axis('off')
axes[0, 2].axhline(0.5, ls='dashdot', c='grey')
axes[0, 2].plot(dist_space, 1 - cdf_1, label='Patient A', c=color_list[0])
axes[0, 2].plot(dist_space, 1 - cdf_2, label='Patient B', c=color_list[1])
axes[0, 2].plot(dist_space, 1 - cdf_3, label='Patient C', c=color_list[2])
axes[0, 2].plot(dist_space, 1 - cdf_4, label='Patient D', c=color_list[3])
axes[0, 2].plot(dist_space[np.where(cdf_1>0.5)[0][0]], 0.5, marker='v', markersize=10, c=color_list[0])
axes[0, 2].plot(dist_space[np.where(cdf_2>0.5)[0][0]], 0.5, marker='v', markersize=10, c=color_list[1])
axes[0, 2].plot(dist_space[np.where(cdf_3>0.5)[0][0]], 0.5, marker='v', markersize=10, c=color_list[2])
axes[0, 2].plot(dist_space[np.where(cdf_4>0.5)[0][0]], 0.5, marker='v', markersize=10, c=color_list[3])
axes[0, 2].plot(e_1, -0.05, marker='*', markersize=12, c=color_list[0], clip_on=False, zorder=10)
axes[0, 2].plot(e_2, -0.05, marker='*', markersize=12, c=color_list[1], clip_on=False, zorder=10)
axes[0, 2].plot(e_3, -0.05, marker='*', markersize=12, c=color_list[2], clip_on=False, zorder=10)
axes[0, 2].plot(e_4, -0.05, marker='*', markersize=12, c=color_list[3], clip_on=False, zorder=10)
# axes[0, 2].text(2.39, 0.8, '2 events in \n [0.5, 1]', fontsize=9, horizontalalignment='center')
# axes[0, 2].text(0.6, 0.15, '2 events in \n [0, 0.5)', fontsize=9, horizontalalignment='center')
group_1 = patches.FancyBboxPatch((.8, 0.5), 1.6, 0.001, linewidth=0.5, edgecolor='none', facecolor=color_list[4], alpha=0.5, boxstyle=patches.BoxStyle("round", pad=0.07))
axes[0, 2].add_patch(group_1)
group_2 = patches.FancyBboxPatch((0.7, -0.05), 1.6, 0.001, linewidth=0.5, edgecolor='none', zorder=8, facecolor=color_list[5], alpha=0.5, clip_on=False, boxstyle=patches.BoxStyle("round", pad=0.07))
axes[0, 2].add_patch(group_2)

# add curve arrow between the two groups
curve_arrow = patches.FancyArrowPatch((0.7, 0.5), (0.6, -0.05), connectionstyle="arc3,rad=0.3", arrowstyle='<->', mutation_scale=10, color='black', linewidth=1.5)
axes[0, 2].add_patch(curve_arrow)
axes[0, 2].grid(False)
# axes[0, 2].spines.set_color('black')
axes[0, 2].set_ylim([-0.05, 1.05])
axes[0, 2].set_yticks([0, 0.5, 1])
axes[0, 2].set_title('(c) Log-rank test', weight='bold')
axes[0, 2].set_xlabel('Year')
axes[0, 2].set_ylabel('Survival Probability')


# subfigure 4, AUC
axes[1, 0].axvline(1.65, ls='--', c=color_list[5])
axes[1, 0].plot(dist_space, 1 - cdf_1, label='Patient A', c=color_list[0])
axes[1, 0].plot(dist_space, 1 - cdf_2, label='Patient B', c=color_list[1])
axes[1, 0].plot(e_1, -0.05, marker='*', markersize=12, c=color_list[0], clip_on=False, zorder=10)
axes[1, 0].plot(e_2, -0.05, marker='*', markersize=12, c=color_list[1], clip_on=False, zorder=10)
axes[1, 0].plot(1.65, 1 - cdf_1[1650], marker='v', markersize=10, c=color_list[0])
axes[1, 0].plot(1.65, 1 - cdf_2[1650], marker='v', markersize=10, c=color_list[1])
# axes[1, 0].text(-0.05, 0.15, 'True  Risk', fontsize=10, horizontalalignment='left', verticalalignment="center")
axes[1, 0].text(-0.05, 0.05, 'Pred. Order', fontsize=9, horizontalalignment='left', verticalalignment="center")
# axes[1, 0].plot(1, 0.15, marker='*', markersize=9, c=color_list[0])
# axes[1, 0].plot(1.2, 0.15, marker='*', markersize=9, c=color_list[1])
axes[1, 0].plot(1, 0.05, marker='v', markersize=7.5, c=color_list[1])
axes[1, 0].plot(1.2, 0.05, marker='v', markersize=7.5, c=color_list[0])
axes[1, 0].grid(False)
axes[1, 0].set_ylim([-0.05, 1.05])
axes[1, 0].set_yticks([0, 0.5, 1])
axes[1, 0].set_title(r'(d) AUC ($t^*=1.65$)', weight='bold')
axes[1, 0].set_xlabel('Year')
axes[1, 0].set_ylabel('Survival Probability')


# subfigure 5, Brier Score
axes[1, 1].axvline(1.65, ls='--', c=color_list[5])
axes[1, 1].axhline(0, ls='--', c=color_list[0], alpha=0.5)
axes[1, 1].axhline(1 - cdf_1[int(1.65*1000)], ls='--', c=color_list[0], alpha=0.5)
axes[1, 1].plot(dist_space, 1 - cdf_1, label='Patient A', c=color_list[0])
# axes[1, 1].plot(dist_space[:death_idx_1], 1 - cdf_1[:death_idx_1], ls='-', label='Patient A', c=color_list[0])
# axes[1, 1].plot(dist_space[death_idx_1:], 1 - cdf_1[death_idx_1:], ls=(0, (1, 1)), label='Patient A', c=color_list[0])
axes[1, 1].plot(e_1, -0.05, marker='*', markersize=12, c=color_list[0], clip_on=False, zorder=10)
axes[1, 1].plot(1.65, 1 - cdf_1[1650], marker='v', markersize=10, c=color_list[0])
curve_arrow = patches.FancyArrowPatch((1.35, - 0.03), (1.35, 1 - cdf_1[int(1.65*1000)] + 0.03), connectionstyle="arc3,rad=0", arrowstyle='<->', mutation_scale=10, color='black', linewidth=1.5)
axes[1, 1].add_patch(curve_arrow)

axes[1, 1].grid(False)
axes[1, 1].set_ylim([-0.05, 1.05])
axes[1, 1].set_yticks([0, 0.5, 1])
axes[1, 1].set_title(r'(e) Brier score ($t^*=1.65$)', weight='bold')
axes[1, 1].set_xlabel('Year')
axes[1, 1].set_ylabel('Survival Probability')


# subfigure 6, 1-calibration
axes[1, 2].axvline(1.65, ls='--', c=color_list[5])
axes[1, 2].plot(dist_space, 1 - cdf_1, label='Patient A', c=color_list[0])
axes[1, 2].plot(dist_space, 1 - cdf_2, label='Patient B', c=color_list[1])
axes[1, 2].plot(dist_space, 1 - cdf_3, label='Patient C', c=color_list[2])
axes[1, 2].plot(dist_space, 1 - cdf_4, label='Patient D', c=color_list[3])
axes[1, 2].plot(e_1, -0.05, marker='*', markersize=12, c=color_list[0], clip_on=False, zorder=10)
axes[1, 2].plot(e_2, -0.05, marker='*', markersize=12, c=color_list[1], clip_on=False, zorder=10)
axes[1, 2].plot(e_3, -0.05, marker='*', markersize=12, c=color_list[2], clip_on=False, zorder=10)
axes[1, 2].plot(e_4, -0.05, marker='*', markersize=12, c=color_list[3], clip_on=False, zorder=10)
axes[1, 2].plot(1.65, 1 - cdf_1[1650], marker='v', markersize=10, c=color_list[0])
axes[1, 2].plot(1.65, 1 - cdf_2[1650], marker='v', markersize=10, c=color_list[1])
axes[1, 2].plot(1.65, 1 - cdf_3[1650], marker='v', markersize=10, c=color_list[2])
axes[1, 2].plot(1.65, 1 - cdf_4[1650], marker='v', markersize=10, c=color_list[3])
group_1 = patches.FancyBboxPatch((1.61, 0.12), 0.1, 0.75, linewidth=1, edgecolor='none', facecolor=color_list[4], alpha=0.5, boxstyle=patches.BoxStyle("round", pad=0.07))
axes[1, 2].add_patch(group_1)
group_2 = patches.FancyBboxPatch((0.7, -0.05), 1.6, 0.001, linewidth=0.5, edgecolor='none', zorder=8, facecolor=color_list[5], alpha=0.5, clip_on=False, boxstyle=patches.BoxStyle("round", pad=0.07))
axes[1, 2].add_patch(group_2)

# add curve arrow between the two groups, arrow arc face up
curve_arrow = patches.FancyArrowPatch((2.2, 0.02), (1.75, 0.3),  connectionstyle="arc3,rad=0.3", arrowstyle='<->', mutation_scale=10, color='black', linewidth=1.5)
axes[1, 2].add_patch(curve_arrow)

# group_2 = patches.FancyBboxPatch((1.645, 0.65), 0.01, 0.20, linewidth=1, edgecolor='none', facecolor=color_list[4], alpha=0.5, boxstyle=patches.BoxStyle("round", pad=0.07))
# axes[1, 2].add_patch(group_2)
# axes[1, 2].text(2.1, 0.82, 'Two event', fontsize=9, horizontalalignment='center')
# axes[1, 2].text(2.1, 0.09, 'Group 2', fontsize=9, horizontalalignment='center')
axes[1, 2].text(2.42, 0.87, 'Avg. pred. prob. \n= 51.4%', fontsize=9, horizontalalignment='center')
axes[1, 2].text(0.6, 0.05, '2/4 events', fontsize=9, horizontalalignment='center')

axes[1, 2].grid(False)
axes[1, 2].set_ylim([-0.05, 1.05])
axes[1, 2].set_yticks([0, 0.5, 1])
axes[1, 2].set_title(r'(f) 1-calibration ($t^*=1.65$)', weight='bold')
axes[1, 2].set_xlabel('Year')
axes[1, 2].set_ylabel('Survival Probability')


# subfigure 7, td-C-index
# axes[2, 0].axhline(0.5, ls='dashdot', c='grey')
axes[2, 0].axvline(e_1, ls='--', c=color_list[0], alpha=0.5)
# axes[2, 0].axvline(e_2, ls='--', c=color_list[1], alpha=0.5)
axes[2, 0].plot(dist_space, 1 - cdf_1, label='Patient A', c=color_list[0])
axes[2, 0].plot(dist_space, 1 - cdf_2, label='Patient B', c=color_list[1])
axes[2, 0].plot(e_1, -0.05, marker='*', markersize=12, c=color_list[0], clip_on=False, zorder=10)
axes[2, 0].plot(e_2, -0.05, marker='*', markersize=12, c=color_list[1], clip_on=False, zorder=10)
axes[2, 0].plot(e_1, 1 - cdf_1[int(e_1*1000)], marker='v', markersize=10, c=color_list[0])
axes[2, 0].plot(e_1, 1 - cdf_2[int(e_1*1000)], marker='v', markersize=10, c=color_list[1])
# axes[2, 0].plot(dist_space[np.where(cdf_1>0.5)[0][0]], 0.5, marker='v', markersize=10, c=color_list[0])
# axes[2, 0].plot(dist_space[np.where(cdf_2>0.5)[0][0]], 0.5, marker='v', markersize=10, c=color_list[1])
# axes[2, 0].text(-0.05, 0.15, 'True  Risk', fontsize=10, horizontalalignment='left', verticalalignment="center")
axes[2, 0].text(-0.05, 0.05, 'Pred. Order', fontsize=9, horizontalalignment='left', verticalalignment="center")
# axes[2, 0].plot(1, 0.15, marker='*', markersize=9, c=color_list[0])
# axes[2, 0].plot(1.2, 0.15, marker='*', markersize=9, c=color_list[1])
axes[2, 0].plot(1, 0.05, marker='v', markersize=7.5, c=color_list[1])
axes[2, 0].plot(1.2, 0.05, marker='v', markersize=7.5, c=color_list[0])
axes[2, 0].grid(False)
axes[2, 0].set_ylim([-0.05, 1.05])
axes[2, 0].set_yticks([0, 0.5, 1])
axes[2, 0].set_title('(g) Time-dependent C-index', weight='bold')
axes[2, 0].set_xlabel('Year')
axes[2, 0].set_ylabel('Survival Probability')


# subfigure 8, IBS
axes[2, 1].axvline(e_1, ls='--', c=color_list[0], alpha=0.5)
axes[2, 1].plot(dist_space, 1 - cdf_1, label='Patient A', c=color_list[0])
axes[2, 1].fill_between(dist_space, heaviside(dist_space, e_1), 1 - cdf_1, alpha=0.2, color='grey')
axes[2, 1].plot(e_1, -0.05, marker='*', markersize=12, c=color_list[0], clip_on=False, zorder=10)
axes[2, 1].text(1., 0.83, r'$\alpha$', fontsize=9, horizontalalignment='center')
axes[2, 1].text(2., 0.3, r'$\beta$', fontsize=9, horizontalalignment='center')
axes[2, 1].grid(False)
axes[2, 1].set_ylim([-0.05, 1.05])
axes[2, 1].set_yticks([0, 0.5, 1])
axes[2, 1].set_title('(h) Integrated Brier score', weight='bold')
axes[2, 1].set_xlabel('Year')
axes[2, 1].set_ylabel('Survival Probability')


# subfigure 9, d-calibration
axes[2, 2].axhline(0.5, ls='dashdot', c='grey')
axes[2, 2].plot(dist_space, 1 - cdf_1, label='Patient A', c=color_list[0])
axes[2, 2].plot(dist_space, 1 - cdf_2, label='Patient B', c=color_list[1])
axes[2, 2].plot(dist_space, 1 - cdf_3, label='Patient C', c=color_list[2])
axes[2, 2].plot(dist_space, 1 - cdf_4, label='Patient D', c=color_list[3])
axes[2, 2].plot(e_1, 1 - cdf_1[death_idx_1], marker='v', markersize=10, c=color_list[0])
axes[2, 2].plot(e_2, 1 - cdf_2[death_idx_2], marker='v', markersize=10, c=color_list[1])
axes[2, 2].plot(e_3, 1 - cdf_3[death_idx_3], marker='v', markersize=10, c=color_list[2])
axes[2, 2].plot(e_4, 1 - cdf_4[death_idx_4], marker='v', markersize=10, c=color_list[3])
axes[2, 2].plot(e_1, -0.05, marker='*', markersize=12, c=color_list[0], clip_on=False, zorder=10)
axes[2, 2].plot(e_2, -0.05, marker='*', markersize=12, c=color_list[1], clip_on=False, zorder=10)
axes[2, 2].plot(e_3, -0.05, marker='*', markersize=12, c=color_list[2], clip_on=False, zorder=10)
axes[2, 2].plot(e_4, -0.05, marker='*', markersize=12, c=color_list[3], clip_on=False, zorder=10)
axes[2, 2].text(2.39, 0.8, '2 events in \n [0.5, 1]', fontsize=9, horizontalalignment='center')
axes[2, 2].text(0.6, 0.15, '2 events in \n [0, 0.5)', fontsize=9, horizontalalignment='center')

axes[2, 2].grid(False)
# axes[2, 2].spines.set_color('black')
axes[2, 2].set_ylim([-0.05, 1.05])
axes[2, 2].set_yticks([0, 0.5, 1])
axes[2, 2].set_title('(i) D-calibration', weight='bold')
axes[2, 2].set_xlabel('Year')
axes[2, 2].set_ylabel('Survival Probability')

lines, labels = axes[2, 2].get_legend_handles_labels()
black_line = mlines.Line2D([], [], color='black', linestyle='-', label=r'Predicted $\widehat{S}(t\mid \bf{x}_i)$')
black_star = mlines.Line2D([], [], color='black', marker='*', linestyle='None',
                          markersize=12, label=r'True $t_i$')
# black_trangle = mlines.Line2D([], [], color='black', marker='v', linestyle='None',
#                           markersize=10, label=r'Prediction')
color_A = mlines.Line2D([], [], color=color_list[0], marker='s', linestyle='None',
                            markersize=12, label='A', markerfacecolor=color_list[0])
color_B = mlines.Line2D([], [], color=color_list[1], marker='s', linestyle='None',
                            markersize=12, label='B', markerfacecolor=color_list[1])
color_C = mlines.Line2D([], [], color=color_list[2], marker='s', linestyle='None',
                            markersize=12, label='C', markerfacecolor=color_list[2])
color_D = mlines.Line2D([], [], color=color_list[3], marker='s', linestyle='None',
                            markersize=12, label='D', markerfacecolor=color_list[3])
lines = []
lines.append(black_star)
lines.append(black_line)
# lines.append(black_trangle)
lines.append(color_A)
lines.append(color_B)
lines.append(color_C)
lines.append(color_D)

labels = []
labels.append(r'True time $t_i$')
labels.append(r'Prediction $\hat{S}(t\mid x_i)$')
# labels.append('Prediction')
labels.append('A')
labels.append('B')
labels.append('C')
labels.append('D')
lgd = fig.legend(lines, labels, bbox_to_anchor=(0.88, 0.02), prop={'size': 9.5}, ncol=7)

# plt.axhline(0.5, ls='--', c='grey')
# plt.legend()
plt.tight_layout()

# plt.show()
# plt.savefig('all_metrics.pdf', dpi=400, bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig('all_metrics.png', dpi=400, bbox_extra_artists=(lgd,), bbox_inches='tight',
            transparent=False)
