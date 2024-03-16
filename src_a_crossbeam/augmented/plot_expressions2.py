# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Plots the number of programs synthesized by the elapsed time.

python3 plot_expressions.py --output_file=string_manipulation_exps_plot.png
"""

import glob
import json
import os

from absl import app
from absl import flags
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")
# import seaborn as sns  # pylint: disable=g-import-not-at-top

FLAGS = flags.FLAGS

flags.DEFINE_string(
    "output_file",
    "string_manipulation_exps_plot.png",
    "file where we will save the output plot.",
)

MAX_PLOT_EXPS = 50 * 1000
MAX_PLOT_TIMES = 1 * 70

# Number of tasks in the benchmark sets.
NUM_NEW_TASKS = 38
NUM_SYGUS_TASKS = 89

# Title for each sub-plot.
NEW_TASKS_TITLE = "Successes by expression considered (38B)"
SYGUS_TITLE = "Successes by expression considered (SyGus)"

NEW_TASKS_TITLE2 = "Successes by time considered (38B)"
SYGUS_TITLE2 = "Successes by time considered (SyGus)"

# Directory to find CrossBeam results.
CROSSBEAM_DIR = "bustle_results_latest"

# Names of datasets in results files.
NEW_TASKS_DATASET_NAME = "new"
SYGUS_DATASET_NAME = "sygus"

# Key -> (label, color, linestyle, linewidth).
# CrossBeam file formats -> (label, color, linestyle, linewidth, border_width)
CROSSBEAM_FORMATS = {
    "run_*.1.vw-bustle_sig-vsize.{}.json": (
        "CrossBeam 1",
        "#028a0f",
        "-",
        2,
        1,
    ),  # green
    "run_*.2.vw-bustle_sig-vsize.{}.json": (
        "CrossBeam 2",
        "#836fff",
        "-",
        2,
        1,
    ),  # green
    "run_*.4.vw-bustle_sig-vsize.{}.json": (
        "CrossBeam 4",
        "#ff4500",
        "-",
        2,
        1,
    ),  # green
    "run_*.8.vw-bustle_sig-vsize.{}.json": (
        "CrossBeam 8",
        "#338AFF",
        "-",
        2,
        1,
    ),  # green
    # "run_*.10.vw-bustle_sig-vsize.{}.json": ("CrossBeam 10", "#FC33FF", "-", 2, 1),  # green
}

# Space out nearby numbers on the right side of plots. Must change for new data.
EXPS_NUMBER_LABEL_TWEAKS = {
    16: 0.15,
    15: -0.15,
    8: 0.15,
    7: -0.15,
}


def get_number_label_delta(num_benchmarks):
    """Amount to move number labels downward to center them on the line."""
    return -1 * num_benchmarks / 110


def solve_text_y_position(solves, num_benchmarks):
    """The Y position to plot the number of solves as text."""
    return (
        solves
        + EXPS_NUMBER_LABEL_TWEAKS.get(solves, 0)
        + get_number_label_delta(num_benchmarks)
    )


def plot_expressions(
    title, num_benchmarks, crossbeam_dir, dataset_name, add_legend=True
):
    """Plots benchmarks solved per expression considered."""
    xs = np.arange(0, MAX_PLOT_EXPS, 100)
    legend_handles = []

    # CrossBeam lines.
    for file_format, (
        label,
        color,
        linestyle,
        linewidth,
        border_width,
    ) in CROSSBEAM_FORMATS.items():
        all_runs = []
        for filename in sorted(
            glob.glob(os.path.join(crossbeam_dir, file_format.format(dataset_name)))
        ):
            print("Reading CrossBeam results file: {}".format(filename))
            with open(filename) as f:
                this_data = json.load(f)
            solved_explored_data = []
            solved_time_data = []
            results = this_data["results"]
            for i in range(len(results)):
                if results[i]["success"]:
                    attempt = results[i]["attempt"]
                    attempts_data = results[i - attempt + 1 : i + 1]
                    solved_explored_data.append(
                        sum(r["num_values_explored"] for r in attempts_data)
                    )
                    solved_time_data.append(r["elapsed_time"] for r in attempts_data)
            ys = [np.sum(solved_explored_data <= x) for x in xs]
            all_runs.append(ys)
        all_runs = np.array(all_runs)
        all_runs_max = np.max(all_runs, axis=0)
        all_runs_min = np.min(all_runs, axis=0)
        all_runs_mean = np.mean(all_runs, axis=0)
        solves = max(all_runs_mean)
        solves = round(solves, 1)
        if label == "CrossBeam":
            crossbeam_ys = all_runs_mean

        (line,) = plt.plot(
            xs,
            all_runs_mean,
            label=label,
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
        )
        if len(all_runs) > 1:
            fill = plt.fill_between(
                xs, all_runs_min, all_runs_max, facecolor=color, alpha=0.1
            )
            plt.plot(
                xs,
                all_runs_max,
                label=None,
                color=color,
                alpha=0.3,
                linestyle="-",
                linewidth=border_width,
            )
            plt.plot(
                xs,
                all_runs_min,
                label=None,
                color=color,
                alpha=0.3,
                linestyle="-",
                linewidth=border_width,
            )
            legend_handles.append((line, fill))
        else:
            assert solves == int(solves)
            solves = int(solves)
            legend_handles.append(line)

        plt.text(
            MAX_PLOT_EXPS * 1.005,
            solve_text_y_position(solves, num_benchmarks),
            solves,
            fontsize=9,
        )

    plt.xlim(0, MAX_PLOT_EXPS)
    plt.ylim(0, num_benchmarks)
    plt.title(title, fontsize=14)
    plt.xlabel("Number of Programs Evaluated", fontsize=12)
    plt.ylabel("Programs synthesized", fontsize=12)

    if add_legend:
        _, labels = plt.gca().get_legend_handles_labels()
        handles = legend_handles
        # Swap RobustFill and Baseline. We need to draw Baseline first so its solid
        # line doesn't cover DeepCoder, but let's have Baseline last in the legend.
        # Currently RobustFill is at position -1, Baseline at position -3.
        # handles[-1], handles[-3] = handles[-3], handles[-1]
        # labels[-1], labels[-3] = labels[-3], labels[-1]
        legend = plt.legend(handles, labels, loc="lower left", bbox_to_anchor=(1.04, 0))
        return legend
    else:
        return None

def plot_times(
    title, num_benchmarks, crossbeam_dir, dataset_name, add_legend=True
):
    """Plots benchmarks solved per expression considered."""
    xs = np.arange(0, MAX_PLOT_TIMES, 10)
    legend_handles = []

    # CrossBeam lines.
    for file_format, (
        label,
        color,
        linestyle,
        linewidth,
        border_width,
    ) in CROSSBEAM_FORMATS.items():
        all_runs = []
        for filename in sorted(
            glob.glob(os.path.join(crossbeam_dir, file_format.format(dataset_name)))
        ):
            print("Reading CrossBeam results file: {}".format(filename))
            with open(filename) as f:
                this_data = json.load(f)
            solved_explored_data = []
            solved_time_data = []
            results = this_data["results"]
            for i in range(len(results)):
                if results[i]["success"]:
                    attempt = results[i]["attempt"]
                    attempts_data = results[i - attempt + 1 : i + 1]
                    solved_explored_data.append(
                        sum(r["num_values_explored"] for r in attempts_data)
                    )
                    solved_time_data.append(sum(r["elapsed_time"] for r in attempts_data))
            ys = [np.sum(solved_time_data <= x) for x in xs]
            print(f"largest time: {max(ys)}")
            all_runs.append(ys)
        all_runs = np.array(all_runs)
        all_runs_max = np.max(all_runs, axis=0)
        all_runs_min = np.min(all_runs, axis=0)
        all_runs_mean = np.mean(all_runs, axis=0)
        solves = max(all_runs_mean)
        solves = round(solves, 1)
        if label == "CrossBeam":
            crossbeam_ys = all_runs_mean

        (line,) = plt.plot(
            xs,
            all_runs_mean,
            label=label,
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
        )
        if len(all_runs) > 1:
            fill = plt.fill_between(
                xs, all_runs_min, all_runs_max, facecolor=color, alpha=0.1
            )
            plt.plot(
                xs,
                all_runs_max,
                label=None,
                color=color,
                alpha=0.3,
                linestyle="-",
                linewidth=border_width,
            )
            plt.plot(
                xs,
                all_runs_min,
                label=None,
                color=color,
                alpha=0.3,
                linestyle="-",
                linewidth=border_width,
            )
            legend_handles.append((line, fill))
        else:
            assert solves == int(solves)
            solves = int(solves)
            legend_handles.append(line)

        plt.text(
            MAX_PLOT_TIMES * 1.005,
            solve_text_y_position(solves, num_benchmarks),
            solves,
            fontsize=9,
        )

    plt.xlim(0, MAX_PLOT_TIMES)
    plt.ylim(0, num_benchmarks)
    plt.title(title, fontsize=14)
    plt.xlabel("Time in seconds", fontsize=12)
    plt.ylabel("Programs synthesized", fontsize=12)

    if add_legend:
        _, labels = plt.gca().get_legend_handles_labels()
        handles = legend_handles
        # Swap RobustFill and Baseline. We need to draw Baseline first so its solid
        # line doesn't cover DeepCoder, but let's have Baseline last in the legend.
        # Currently RobustFill is at position -1, Baseline at position -3.
        # handles[-1], handles[-3] = handles[-3], handles[-1]
        # labels[-1], labels[-3] = labels[-3], labels[-1]
        legend = plt.legend(handles, labels, loc="lower left", bbox_to_anchor=(1.04, 0))
        return legend
    else:
        return None

def plot_histograms(
    title,
    num_benchmarks,
    crossbeam_dir,
    dataset_name,
):
    for file_format, (
        label,
        color,
        linestyle,
        linewidth,
        border_width,
    ) in CROSSBEAM_FORMATS.items():
        for filename in sorted(
            glob.glob(os.path.join(crossbeam_dir, file_format.format(dataset_name)))
        ):
            print("Reading CrossBeam results file: {}".format(filename))
            with open(filename) as f:
                this_data = json.load(f)
            solved_time_data = []
            results = this_data["results"]
            for i in range(len(results)):
                if results[i]["success"]:
                    attempt = results[i]["attempt"]
                    attempts_data = results[i - attempt + 1 : i + 1]
                    solved_time_data.append(sum(r["elapsed_time"] for r in attempts_data))

        fig, ax = plt.subplots()
        name = file_format + title
        ax.set_title(title)
        # xs = np.array(solved_time_data)
        ax.hist(solved_time_data)
        plt.savefig(
            os.path.expanduser(name + ".png"),
            bbox_inches="tight",
        )


def main(_):
    # sns.set()

    default_width = 6.4
    default_height = 4.8
    plt.figure(figsize=(default_width * 2, default_height))

    plt.subplot(121)
    plot_expressions(
        title=NEW_TASKS_TITLE,
        num_benchmarks=NUM_NEW_TASKS,
        crossbeam_dir=CROSSBEAM_DIR,
        dataset_name=NEW_TASKS_DATASET_NAME,
        add_legend=False,
    )
    plt.grid()

    plt.subplot(122)
    legend = plot_expressions(
        title=SYGUS_TITLE,
        num_benchmarks=NUM_SYGUS_TASKS,
        crossbeam_dir=CROSSBEAM_DIR,
        dataset_name=SYGUS_DATASET_NAME,
        add_legend=True,
    )

    plt.grid()
    plt.savefig(
        os.path.expanduser("expressions.png"),
        bbox_inches="tight",
        bbox_extra_artists=[legend],
    )

    plt.figure(figsize=(default_width * 2, default_height))

    plt.subplot(121)
    plot_times(
        title=NEW_TASKS_TITLE2,
        num_benchmarks=NUM_NEW_TASKS,
        crossbeam_dir=CROSSBEAM_DIR,
        dataset_name=NEW_TASKS_DATASET_NAME,
        add_legend=False,
    )
    plt.grid()

    plt.subplot(122)
    legend = plot_times(
        title=SYGUS_TITLE2,
        num_benchmarks=NUM_SYGUS_TASKS,
        crossbeam_dir=CROSSBEAM_DIR,
        dataset_name=SYGUS_DATASET_NAME,
        add_legend=True,
    )
    plt.grid()

    plt.savefig(
        os.path.expanduser("time.png"),
        bbox_inches="tight",
        bbox_extra_artists=[legend],
    )
    plt.clf()
    # plot_histograms(
    #     title="New",
    #     num_benchmarks=NUM_NEW_TASKS,
    #     crossbeam_dir=CROSSBEAM_DIR,
    #     dataset_name=NEW_TASKS_DATASET_NAME,
    # )

    # plot_histograms(
    #     title="SyGus",
    #     num_benchmarks=NUM_SYGUS_TASKS,
    #     crossbeam_dir=CROSSBEAM_DIR,
    #     dataset_name=SYGUS_DATASET_NAME,
    # )



if __name__ == "__main__":
    app.run(main)
