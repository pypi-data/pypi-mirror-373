import os

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from typing import List



'''-----------------------------------------------------------------------------------------
    Signal u,v,w plotting
-----------------------------------------------------------------------------------------'''

def add_signal_plot(axs: Axes, times: np.ndarray, signal: np.ndarray, signal_name: str | None = None):

    for i, (ax, comp) in enumerate(zip(axs, ["u", "v", "w"])):
        if i == 0:
            ax.plot(times, signal[i], label=signal_name)
        else:
            ax.plot(times, signal[i])

def plot_signals(times_list: List, signals_list: List, names_list: List, case_name: str | None = None,
                 exp_dir: str | None = None, dpi = 300):

    fig, axes = plt.subplots(3, 1, figsize=(20, 10), sharex=True)

    for times, signal, names in zip(times_list, signals_list, names_list):
        add_signal_plot(axes, times, signal, names)

    for i, comp in zip(range(3),["u", "v", "w"]):
        axes[i].set_ylabel(f'{comp} [m/s]', fontsize=20)
        axes[i].tick_params(axis="both", which="major", labelsize=16)
    axes[-1].set_xlabel('Time [s]', fontsize=20)

    fig.legend(fontsize=20, ncol=2)
    fig.tight_layout()
    fig.subplots_adjust(top=0.88)

    if len(times_list) > 1:
        if case_name is not None:
            fig.suptitle(f'Signals for case: {case_name}', fontsize=30, ha="left", x = 0.05)
            if exp_dir is not None:
                os.makedirs(exp_dir, exist_ok=True)
                fig.savefig(os.path.join(exp_dir, f"{case_name}.png"), dpi=dpi)
            else:
                plt.show()
        else:
            if exp_dir is not None:
                os.makedirs(exp_dir, exist_ok=True)
                fig.savefig(os.path.join(exp_dir, f"flomp_signal_plot.png"), dpi=dpi)
            else:
                plt.show()
    elif len(times_list) == 1:
        if names_list[0] is not None:
            fig.suptitle(f'Single Signal: {names_list[0]}', fontsize=30, ha="left", x=0.05)
            if exp_dir is not None:
                os.makedirs(exp_dir, exist_ok=True)
                fig.savefig(os.path.join(exp_dir, f"{names_list[0]}.png"), dpi=dpi)
            else:
                plt.show()
        else:
            if exp_dir is not None:
                os.makedirs(exp_dir, exist_ok=True)
                fig.savefig(os.path.join(exp_dir, f"flomp_signal_plot.png"), dpi=dpi)
            else:
                plt.show()

    plt.close("all")

'''-----------------------------------------------------------------------------------------
    Sigma and Ti plotting
-----------------------------------------------------------------------------------------'''

'''-----------------------------------------------------------------------------------------
    PSD plotting
-----------------------------------------------------------------------------------------'''

'''-----------------------------------------------------------------------------------------
    Plane plotting
-----------------------------------------------------------------------------------------'''