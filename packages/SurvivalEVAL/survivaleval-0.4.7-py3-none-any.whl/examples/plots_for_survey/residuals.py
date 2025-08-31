import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
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

eval = LifelinesEvaluator(survs_cox, df_test['time'].values, df_test['event'].values)

cox_residuals = eval.residuals(method="CoxSnell", draw_figure=False)
cox2_residuals = eval.residuals(method="Modified CoxSnell-v2", draw_figure=False)
martingale_rs = eval.residuals(method="Martingale", draw_figure=False)
deviance_res = eval.residuals(method="Deviance", draw_figure=False)

cum_haz_empirical = NelsonAalen(cox_residuals, df_test['event'].values)
max_res = np.max(cum_haz_empirical.cumulative_hazard)

fig, ax = plt.subplots(nrows=1, ncols=1, tight_layout=True, dpi=400, figsize=(3.2, 3),)
ax.plot(cum_haz_empirical.survival_times, cum_haz_empirical.cumulative_hazard, color='skyblue')
ax.plot([0, max_res], [0, max_res], label='Ideal', linestyle='dashed', color='grey', linewidth=1)
ax.set_xlim(- max_res * 0.05, max_res * 1.05)
ax.set_ylim(- max_res * 0.05, max_res * 1.05)
ax.legend()
ax.set_xlabel('Cox-Snell Residuals')
ax.set_ylabel('Cumlative hazard of \nCox-Snell residuals')
plt.savefig('cox_snell_residual.png', dpi=400)

idx = np.arange(len(cox_residuals))
event_indicators = df_test['event'].values.astype(bool)


def scatter_plus_hist(
        fig, gs_cell, x_idx, y_vals, events, *,
                      y_label="", title="",
                      bins='auto', alpha=0.5):
    """
    Draw a scatterplot of residuals in the left‑hand panel and, in
    the right‑hand panel, a horizontal histogram of the same y values.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The parent figure to which the axes belong.
    gs_cell : matplotlib.gridspec.SubplotSpec
        A single slot (cell) of a top‑level GridSpec—e.g., outer[i].
    x_idx : 1‑D array‑like
        X‑axis positions (e.g., index or time).
    y_vals : 1‑D array‑like
        Y‑axis data (residuals).
    events : 1‑D boolean array‑like
        True for events, False for censored.
    y_label : str, optional
        Label for the scatter’s y‑axis.
    title : str, optional
        Title for the scatter panel.
    color : str or tuple, optional
        Color for event markers and histogram bars.
    bins : int, str, or sequence, optional
        Passed to ``plt.hist``.
    alpha : float, optional
        Transparency for scatter markers.

    Returns
    -------
    ax_scatter, ax_hist : tuple of matplotlib.axes.Axes
        The two axes objects that were created.
    """
    # Create a 1×2 inner GridSpec within this outer cell
    inner = gs_cell.subgridspec(1, 2, width_ratios=[2, 1], wspace=0.00005)

    # Axes: scatter on the left, histogram on the right
    ax_scatter = fig.add_subplot(inner[0, 0])
    ax_hist    = fig.add_subplot(inner[0, 1], sharey=ax_scatter)

    # Scatter plot
    ax_scatter.scatter(x_idx[events], y_vals[events],  alpha=alpha, facecolors='#D5E8D4', edgecolors='#82B366', linewidths=1, label='Event')
    ax_scatter.scatter(x_idx[~events], y_vals[~events], alpha=alpha, facecolors='#FFF2CC', edgecolors='#D6B656', linewidths=1, label='Censored')
    ax_scatter.set_xlabel('Index')
    ax_scatter.set_ylabel(y_label)
    if title:
        ax_scatter.set_title(title, pad=4, fontsize=9)

    # Histogram (horizontal)
    ax_hist.hist(y_vals, bins=bins, orientation='horizontal', linewidth=1, edgecolor='black', color='#CDE7F0')
    ax_hist.set_xlabel('Count')
    ax_hist.tick_params(axis='y', labelleft=False)  # hide duplicate ticks

    return ax_scatter, ax_hist


fig = plt.figure(figsize=(8, 3), dpi=400, constrained_layout=True)
outer = fig.add_gridspec(1, 3, wspace=0.25)

scatter_plus_hist(fig, outer[0], idx, cox2_residuals, event_indicators,
                  y_label="(a) Modified Cox‑Snell residuals")
scatter_plus_hist(fig, outer[1], idx, martingale_rs, event_indicators,
                  y_label="(b) Martingale residuals")
scatter_plus_hist(fig, outer[2], idx, deviance_res, event_indicators,
                  y_label="(c) Deviance residuals")

# plt.tight_layout()
plt.savefig("combined_residuals.png", dpi=400)
