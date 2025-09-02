import os

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from typing import List, Union
import imageio.v2 as imageio #requires imageio and imageio-ffmpeg
import shutil
import time


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

def plot_plane(pos: np.ndarray, vel: np.ndarray, tag: str | None = None,
               exp_dir: str | None = None, dpi = 300):
    axes_names = ["x", "y", "z"]
    var_index = np.array([0, 1, 2])
    uniques_list = [np.unique(pos[:, i]) for i in range(3)]
    constant_value_index = [i for i, arr in enumerate(uniques_list) if len(arr) == 1][0]
    var_index = var_index[var_index != constant_value_index]
    var_0 = uniques_list[var_index[0]]
    var_0_range = np.array([np.min(var_0), np.max(var_0)])
    var_1 = uniques_list[var_index[1]]
    var_1_range = np.array([np.min(var_1), np.max(var_1)])
    nx = len(uniques_list[var_index[0]])
    ny = len(uniques_list[var_index[1]])
    base_len = 8
    sub_asp = np.array([1, (var_1_range[1] - var_1_range[0]) / (var_0_range[1] - var_0_range[0])])
    if nx / ny <= 1.5:
        fig_size = np.array([sub_asp[0] / 0.7, 3 * sub_asp[1] / 0.75])
    elif nx / ny > 1.5 and nx / ny <= 2.5:
        fig_size = np.array([sub_asp[0] / 0.7, 3 * sub_asp[1] / 0.55])
    else:
        fig_size = np.array([sub_asp[0] / 0.7, 3 * sub_asp[1]  / 0.45])
    fig_size *= base_len / np.min(fig_size)

    fig, axes = plt.subplots(3, 1, figsize=fig_size, sharex=True)

    for i, ax in enumerate(axes):
        field = vel[:, i].reshape(nx, ny)
        im = ax.imshow(
            field.T,
            origin="lower",
            extent=[
                pos[:, var_index[0]].min(),
                pos[:, var_index[0]].max(),
                pos[:, var_index[1]].min(),
                pos[:, var_index[1]].max(),
                    ],
            cmap="viridis",
            vmin=np.min(vel),
            vmax=np.max(vel),
            aspect="equal")

    for i, comp in zip(range(3),["u", "v", "w"]):
        axes[i].set_title(f"Component: {comp}", fontsize=20)
        axes[i].tick_params(axis="both", which="major", labelsize=16)
    axes[-1].set_xlabel(f'Direction {axes_names[var_index[0]]} [m]', fontsize=20)

    y_label = fig.supylabel(f"Direction {axes_names[var_index[1]]} [m]", fontsize=20)
    y_label.set_x(0.01)
    cax = fig.add_axes([0.51, 0.95, 0.48, 0.02])
    col_bar = fig.colorbar(im, cax=cax, orientation="horizontal")
    col_bar.set_label("Velocity [m/s]", fontsize=20)
    col_bar.ax.tick_params(labelsize=16)
    fig.tight_layout()
    if nx / ny <= 2.5:
        fig.subplots_adjust(top=0.9, left=0.1)
    elif nx / ny > 2.5 and nx / ny <= 4.5:
        fig.subplots_adjust(top=0.825, left=0.1)
    elif nx / ny > 4.5 and nx / ny <= 7.5:
        fig.subplots_adjust(top=0.825, left=0.075)
    else:
        fig.subplots_adjust(top=0.825, left=0.05)


    if tag is not None:
        fig.suptitle(f'Showing Plane:\n{tag}', fontsize=30, ha="left", x=0.05)
        if exp_dir is not None:
            os.makedirs(exp_dir, exist_ok=True)
            fig.savefig(os.path.join(exp_dir, f"{tag}.png"), dpi=dpi)
        else:
            plt.show()
    else:
        if exp_dir is not None:
            os.makedirs(exp_dir, exist_ok=True)
            fig.savefig(os.path.join(exp_dir, f"flomp_signal_plot.png"), dpi=dpi)
        else:
            plt.show()
    plt.close("all")

def animate_temporal_plane(posList: Union[np.ndarray, list], velList: Union[np.ndarray, list],tagList: str | None = None,
                            exp_dir: str | None = None, dpi = 300):

    n_frames = len(posList)
    temp_dir = "./flomp_temp_animation_generation"
    os.makedirs(temp_dir, exist_ok=True)
    for i, (pos_el, vel_el) in enumerate(zip(posList,velList)):
        print(f" Creating animation frame {i+1}/{n_frames}")
        plot_plane(pos_el, vel_el, f"frame{i:04d}", temp_dir, dpi)
    if exp_dir is None: exp_dir = "."
    with imageio.get_writer(f"{exp_dir}/PlaneTempAnimation.mp4", fps=10) as writer:
        for i in range(n_frames):
            img = imageio.imread(f"{temp_dir}/frame{i:04d}.png")
            writer.append_data(img)