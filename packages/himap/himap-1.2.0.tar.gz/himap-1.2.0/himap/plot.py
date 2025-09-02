# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Group iSP and contributors

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os


def plot_multiple_observ(obs, states, num2plot):
    """
    Plot multiple degradation histories from MC sampling.

    Parameters
    ----------
    obs : dict
        Dictionary containing all observations.
    states : dict
        Dictionary containing all statesm of the corresponding observations.
    num2plot : int
        Number of histories to plot.

    Returns
    -------
    None

    Notes
    -----
    The figure is saved at '/path/to/current/directory/results/figures/mc_traj.png'.
    """
    fig_path = os.path.join(os.getcwd(), 'results', 'figures', 'mc_traj.png')
    title = f'Degradation histories with MC sampling\n {num2plot} random samples out of {len(obs)} total samples'
    fig, axs = plt.subplots(num2plot, figsize=(19, 10))
    keys = list(obs.keys())
    for i in range(num2plot):
        k = np.random.randint(len(obs))
        states4plot = states[keys[k]]
        obs4plot = obs[keys[k]]

        ax1 = axs[i]

        color = 'tab:red'
        ax1.set_xlabel('time')
        ax1.set_ylabel('observations', color=color)
        ax1.plot(obs4plot, color=color, label="observations")
        ax1.tick_params(axis='y', labelcolor=color)

        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

        color = 'tab:blue'
        ax2.set_ylabel('states', color=color)  # we already handled the x-label with ax1
        ax2.plot(states4plot, color=color, linewidth=2, alpha=.8, label='HI')
        ax2.tick_params(axis='y', labelcolor=color, )
        ax2.set_yticks([tick for tick in ax2.get_yticks() if tick % 1 == 0])
        ax2.set_ylim(top=max(states4plot) + 1)
        plt.xlim(left=0)
        plt.ylim(bottom=0)

    fig.suptitle(title)
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f'MC trajectories figure saved at {fig_path}')


def plot_ruls(rul_mean, rul_upper, rul_lower, fig_path):
    """
    Plot RUL predictiction with confidence intervals vs true RUL.

    Parameters
    ----------
    rul_mean : list
        Mean RUL predictions.
    rul_upper : list
        Upper bound of the confidence interval.
    rul_lower : list
        Lower bound of the confidence interval.
    fig_path : str
        Path to save the figure.

    Returns
    -------
    None

    Notes
    -----
    The figure is saved at '/path/to/current/directory/results/figures/'.
    """
    fig, ax = plt.subplots(figsize=(19, 10))
    ax.plot(range(len(rul_mean), 0, -1), label='True RUL', color='black', linewidth=2)
    ax.plot(rul_mean, '--', label='Mean Predicted RUL', color='tab:red', linewidth=2)
    ax.plot(rul_upper, '-.', label='Upper Bound (95% CI)', color='tab:blue', linewidth=1)
    ax.plot(rul_lower, '-.', label='Lower Bound (95% CI)', color='tab:blue', linewidth=1)
    ax.fill_between(range(len(rul_mean)), rul_lower, rul_upper, alpha=0.1, color='tab:blue')
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    fig.suptitle('RUL')
    ax.legend(loc='best')
    plt.xlabel('Time [s]')
    plt.ylabel('RUL')
    plt.savefig(fig_path, dpi=300)
    plt.close()
