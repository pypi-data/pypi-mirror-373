# plot a pdf, cdf, and survival function for a weibull distribution (in three subplots)
from scipy.stats import norm, weibull_min
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# set seed
np.random.seed(111)

# create a range of x values
x = np.linspace(0, 6, 100)

# create a weibull distribution with shape 1.5 and scale 2
dist = weibull_min(1.5, scale=1.3)

# create a figure and a set of subplots
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(9, 3))

# plot the probability density function
# ax[0].spines['left'].set_position('center')
ax[0].spines['right'].set_color('none')
ax[0].spines['top'].set_color('none')
ax[0].plot(x, dist.pdf(x), zorder = 10)
ax[0].set_ylabel('Probability Density Function')
ax[0].set_xlabel('time')
ax[0].set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1], minor=False)
ax[0].set_xlim(0.0, 6.0)
ax[0].set_ylim(0.0, 1.0)
ax[0].grid(axis='y')

# # plot the cumulative distribution function
# # ax[1].spines['left'].set_position('center')
# ax[1].spines['right'].set_color('none')
# ax[1].spines['top'].set_color('none')
# ax[1].plot(x, dist.cdf(x), zorder = 10)
# ax[1].set_title('Cumulative Density Function')
# ax[1].set_yticks([0, 0.25, 0.5, 0.75, 1], minor=False)
# ax[1].set_ylim(0.0, 1.0)
# ax[1].set_xlabel('time')
# ax[1].grid(axis='y')

# plot the survival function
# ax[2].spines['left'].set_position('center')
ax[1].spines['right'].set_color('none')
ax[1].spines['top'].set_color('none')
ax[1].plot(x, dist.sf(x),  zorder = 10)
ax[1].set_ylabel('Survival Function')
ax[1].set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1], minor=False)
ax[1].set_xlabel('time')
ax[1].set_xlim(0.0, 6.0)
ax[1].set_ylim(0.0, 1.0)
ax[1].grid(axis='y')


# plot the cumulative hazard function
ax[2].spines['right'].set_color('none')
ax[2].spines['top'].set_color('none')
ax[2].plot(x, -dist.logsf(x),  zorder = 10)
ax[2].set_ylabel('Cumulative Hazard Function')
# ax[1].set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1], minor=False)
ax[2].set_xlabel('time')
ax[2].set_xlim(0.0, 6.0)
ax[2].set_ylim(0.0, 10.0)
ax[2].grid(axis='y')

colors = sns.color_palette('colorblind', 8)

# draw 100 samples from the weibull distribution
samples_40 = dist.rvs(100)

dot_size = 8
ax[0].scatter(samples_40, dist.pdf(samples_40), color=colors[7], marker='o', s=dot_size, zorder=8)
# ax[1].scatter(samples_40, dist.cdf(samples_40), color=colors[7], marker='o', s=dot_size)
ax[1].scatter(samples_40, dist.sf(samples_40), color=colors[7], marker='o', s=dot_size, zorder=8)
ax[2].scatter(samples_40, -dist.logsf(samples_40), color=colors[7], marker='o', s=dot_size, zorder=8)

# plot the sideway histogram for the
ax0 = ax[0].twiny()
# ax0.get_xaxis().set_visible(False)
# ax0.set_xticks([])

ax1 = ax[1].twiny()
ax1.hist(dist.sf(samples_40), bins=[0, 0.2, 0.4, 0.6, 0.8, 1], density=False, alpha=0.3, color='gray', orientation='horizontal', zorder=5)
ax1.yaxis.set_ticks_position('left')
# ax1.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1], minor=False)
ax1.set_ylim(0.0, 1.0)
# ax1.set_xlim(0, 1)
ax1.xaxis.set_ticks_position('top')
ax1.set_xlabel('count')

ax2 = ax[2].twiny()
ax2.hist(-dist.logsf(samples_40), bins=[0, 2, 4, 6, 8, 10], density=False, alpha=0.3, color='gray', orientation='horizontal', zorder=5)
ax2.yaxis.set_ticks_position('left')
ax2.set_ylim(0.0, 10.0)
ax2.xaxis.set_ticks_position('top')
ax2.set_xlabel('count')
# ax2.set_xlim(0, 1)


plt.tight_layout()
plt.savefig('weibull_distribution_40.png', dpi=400)

surv_probs = dist.sf(samples_40)
print("Above 75%:", len(surv_probs[surv_probs > 0.75]))
print("50%-75%:", len(surv_probs[(surv_probs > 0.5) & (surv_probs <= 0.75)]))
print("25%-50%:", len(surv_probs[(surv_probs > 0.25) & (surv_probs <= 0.5)]))
print("Below 25%:", len(surv_probs[surv_probs <= 0.25]))


