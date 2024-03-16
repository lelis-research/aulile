import os
import subprocess
import sys

import matplotlib.pylab as plt
import pandas as pd

import crossbeam_consolidator

evaluation_limit = 350000000
time_limit = 86400
max_evaluations = evaluation_limit
max_time = time_limit


def get_time_in_seconds(timestr):
    time_splits = timestr.split(":")
    seconds = int(time_splits[0]) * 60 * 60 + int(time_splits[1]) * 60 + int(time_splits[2].split(".")[0])
    return seconds


def get_processed_results(statistics, statkeys):
    global max_evaluations
    global max_time
    evaluations_map = {}
    times_map = {}
    success_counts = {}
    max_eval_logkey = None
    max_time_logkey = None
    min_evaluations = sys.maxsize
    min_eval_logkey = None
    min_time = sys.maxsize
    min_time_logkey = None
    processed_results = {}

    for statkey in statkeys:
        processed_results[statkey] = {}
        evaluations = []
        times = []
        for benchmark_stat in statistics:
            if benchmark_stat[statkey + "_result"] == "Success" and float(
                    benchmark_stat[statkey + "_evaluations"]) <= evaluation_limit and float(
                benchmark_stat[statkey + "_time"]) <= time_limit:
                evaluations.append(float(benchmark_stat[statkey + "_evaluations"]))
                times.append(float(benchmark_stat[statkey + "_time"]))

        evaluations.sort()
        times.sort()
        sum_of_evaluations = 0
        sum_of_times = 0
        evaluation_results = {}
        time_results = {}

        for index, evaluation in enumerate(evaluations):
            sum_of_evaluations = int(evaluation)
            evaluation_results[sum_of_evaluations] = index + 1

        for index, time in enumerate(times):
            sum_of_times = time
            time_results[sum_of_times] = index + 1

        if sum_of_evaluations > max_evaluations:
            max_evaluations = sum_of_evaluations
            max_eval_logkey = statkey

        if sum_of_times > max_time:
            max_time = sum_of_times
            max_time_logkey = statkey

        if sum_of_evaluations < min_evaluations:
            min_evaluations = sum_of_evaluations
            min_eval_logkey = statkey

        if sum_of_times < min_time:
            min_time = sum_of_times
            min_time_logkey = statkey

        evaluations_map[statkey] = evaluation_results
        times_map[statkey] = time_results
        success_counts[statkey] = len(evaluations)

    processed_results["evaluations_map"] = evaluations_map
    processed_results["times_map"] = times_map
    processed_results["success_counts"] = success_counts
    processed_results["min_time_logkey"] = min_time_logkey
    processed_results["max_time_logkey"] = max_time_logkey
    processed_results["min_eval_logkey"] = min_eval_logkey
    processed_results["max_eval_logkey"] = max_eval_logkey

    for statkey, value in evaluations_map.items():
        expressions = list(value.keys())
        tasks = list(value.values())
        min_plot_expressions = []
        min_plot_tasks = []
        max_plot_expressions = expressions.copy()
        max_plot_tasks = tasks.copy()
        for index, expression in enumerate(expressions):
            if expression <= min_evaluations:
                min_plot_expressions.append(expression)
                min_plot_tasks.append(tasks[index])
        if min_plot_expressions[-1] != min_evaluations:
            min_plot_expressions.append(min_evaluations)
            min_plot_tasks.append(min_plot_tasks[-1])
        if max_plot_expressions[-1] != max_evaluations:
            max_plot_expressions.append(max_evaluations)
            max_plot_tasks.append(max_plot_tasks[-1])

        processed_results[statkey]["min_evals"] = min_plot_expressions
        processed_results[statkey]["min_eval_tasks"] = min_plot_tasks
        processed_results[statkey]["max_evals"] = max_plot_expressions
        processed_results[statkey]["max_eval_tasks"] = max_plot_tasks
        print("statkey: ", statkey)
        print("max expression: ", max_plot_expressions[-2])

    for statkey, value in times_map.items():
        times = list(value.keys())
        tasks = list(value.values())
        min_plot_times = []
        min_plot_tasks = []
        max_plot_times = times.copy()
        max_plot_tasks = tasks.copy()
        for index, time in enumerate(times):
            if time <= min_time:
                min_plot_times.append(time)
                min_plot_tasks.append(tasks[index])
        if min_plot_times[-1] != min_time:
            min_plot_times.append(min_time)
            min_plot_tasks.append(min_plot_tasks[-1])
        if max_plot_times[-1] != max_time:
            max_plot_times.append(max_time)
            max_plot_tasks.append(max_plot_tasks[-1])

        processed_results[statkey]["min_times"] = min_plot_times
        processed_results[statkey]["min_time_tasks"] = min_plot_tasks
        processed_results[statkey]["max_times"] = max_plot_times
        processed_results[statkey]["max_time_tasks"] = max_plot_tasks

    return processed_results


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(" ")
        print("Please provide the log directory and number of tasks as the arguments !!")
        print(" ")
        sys.exit()
    source_directory = sys.argv[1]
    number_of_tasks = sys.argv[2]

    crossbeam_eval_stats = crossbeam_consolidator.get_evaluation_stats_sygus(evaluation_limit)
    eval_counts = [eval_stat["count"] for eval_stat in crossbeam_eval_stats]
    eval_avg = [eval_stat["avg"] for eval_stat in crossbeam_eval_stats]
    eval_min = [eval_stat["min"] for eval_stat in crossbeam_eval_stats]
    eval_max = [eval_stat["max"] for eval_stat in crossbeam_eval_stats]

    crossbeam_time_stats = crossbeam_consolidator.get_time_stats_sygus(time_limit)
    time_periods = [time_stat["time_period"] for time_stat in crossbeam_time_stats]
    time_avg = [time_stat["avg"] for time_stat in crossbeam_time_stats]
    time_min = [time_stat["min"] for time_stat in crossbeam_time_stats]
    time_max = [time_stat["max"] for time_stat in crossbeam_time_stats]

    benchmarks_file = "bustle_benchmarks"
    # benchmarks_file = "top_down_benchmarks"
    # benchmarks_file = "random_top_down_benchmarks"
    # benchmarks_file = "38_benchmarks"

    os.makedirs("./result_images/", exist_ok=True)

    all_logs = ["BUS_Augmented_Sygus.log", "BUSTLE_Sygus.log",
                "BUSTLE_Augmented_Sygus.log",
                "BUS_Sygus.log",
                "BUS_Augmented_Combination_Sygus.log",
                "BUSTLE_Augmented_Combination_Sygus.log",
                "BUS_Augmented_Chopping_Sygus.log",
                "BUSTLE_Augmented_Chopping_Sygus.log"
                # , "crossbeam.log"
                ]

    logs = all_logs

    all_logkeys = ["AGS", "BUSTLE", "AGS+BUSTLE", "BUS",
                   "BUS+COMB", "BUSTLE+COMB", "BUS+CHOP", "BUSTLE+CHOP"
                   # , "crossbeam"
                   ]

    logkeys = all_logkeys

    script_name = "./processor_script.sh"

    for key, logfile in enumerate(logs):
        logkey = logkeys[key]
        script_result = subprocess.check_call(
            [script_name, "./" + source_directory + "/" + logfile, logkey, number_of_tasks])
        print(script_result)

    benchmark_results = {}
    unsolved_tasks = set()

    with open(benchmarks_file) as f:
        all_benchmarks = f.read().splitlines()

    print("total no of benchmarks: ", len(all_benchmarks))
    for benchmark in all_benchmarks:
        stats = {"benchmark": benchmark}
        unsolved_tasks.add(benchmark)
        for logkey in logkeys:
            stats[logkey + "_result"] = "Fail"
            stats[logkey + "_program"] = "None"
            stats[logkey + "_time"] = 86400000
            stats[logkey + "_evaluations"] = 1000000000
        benchmark_results[benchmark] = stats

    for logkey in logkeys:
        print(logkey)
        with open(logkey + "_benchmarks.txt") as f:
            benchmarks = f.read().splitlines()

        with open(logkey + "_results.txt") as f:
            results = f.read().splitlines()

        with open(logkey + "_programs.txt") as f:
            programs = f.read().splitlines()

        with open(logkey + "_evaluations.txt") as f:
            evaluations = f.read().splitlines()

        with open(logkey + "_times.txt") as f:
            times = f.read().splitlines()

        for index, benchmark in enumerate(benchmarks):
            if benchmark in unsolved_tasks:
                unsolved_tasks.remove(benchmark)
            stats = benchmark_results.get(benchmark)
            stats[logkey + "_result"] = results[index]
            stats[logkey + "_program"] = programs[index]
            stats[logkey + "_time"] = get_time_in_seconds(str(times[index]))
            stats[logkey + "_evaluations"] = evaluations[index]

    with open("../config/unsolved_tasks", "w") as fwriter:
        for unsolved_task in unsolved_tasks:
            fwriter.write(unsolved_task)
            fwriter.write("\n")

    statistics = []

    for key, value in benchmark_results.items():
        statistics.append(value)

    dataFrame = pd.DataFrame(statistics)
    dataFrame.to_csv("statistics.csv", index=False)

    statistics = dataFrame.to_dict('records')

    statkeys = ["AGS", "BUSTLE", "AGS+BUSTLE", "BUS",
                "BUS+COMB", "BUSTLE+COMB", "BUS+CHOP", "BUSTLE+CHOP"
                # , "crossbeam"
                ]
    line_styles = ["-", "--", ":", "-.", "solid", "dotted", "-", "--"]

    processed_results = get_processed_results(statistics, statkeys)

    # Plotting max evaluations
    for index, statkey in enumerate(statkeys):
        plot_expressions = processed_results[statkey]["max_evals"]
        plot_tasks = processed_results[statkey]["max_eval_tasks"]
        plt.step(plot_expressions, plot_tasks, ls=line_styles[index], label=statkey + " (" + str(plot_tasks[-1]) + ")",
                 where='pre')
        # plt.text(plot_expressions[-1], plot_tasks[-1], plot_tasks[-1])

    # crossbeam average plot
    if eval_counts[-1] < max_evaluations:
        eval_counts.append(max_evaluations)
        eval_avg.append(eval_avg[-1])
        eval_min.append(eval_min[-1])
        eval_max.append(eval_max[-1])

    plt.step(eval_counts, eval_avg, ls="solid", label="crossbeam_avg (" + str(eval_avg[-1]) + ")", where='pre')
    # plt.step(eval_counts, eval_min, ls="dotted", label="crossbeam_min (" + str(eval_min[-1]) + ")", where='pre')
    # plt.step(eval_counts, eval_max, ls="--", label="crossbeam_max (" + str(eval_max[-1]) + ")", where='pre')

    plt.xlabel("Number of Programs Evaluated")
    # plt.ylim(50)
    plt.ylabel("Programs synthesized")
    plt.legend()
    plt.title("Successes by expressions considered (Sygus)")
    plt.grid("on", linestyle=':')
    plt.savefig("./result_images/max_expr.png", bbox_inches='tight')
    plt.show()
    plt.close()

    # Plotting max time periods
    for index, statkey in enumerate(statkeys):
        plot_times = processed_results[statkey]["max_times"]
        plot_tasks = processed_results[statkey]["max_time_tasks"]
        plt.step(plot_times, plot_tasks, ls=line_styles[index], label=statkey + " (" + str(plot_tasks[-1]) + ")",
                 where='pre')
        # plt.text(plot_expressions[-1], plot_tasks[-1], plot_tasks[-1])

    # crossbeam average plot
    if time_periods[-1] < max_time:
        time_periods.append(max_time)
        time_avg.append(time_avg[-1])
        time_min.append(time_min[-1])
        time_max.append(time_max[-1])

    plt.step(time_periods, time_avg, ls="solid", label="crossbeam_avg (" + str(time_avg[-1]) + ")", where='pre')
    # plt.step(eval_counts, eval_min, ls="dotted", label="crossbeam_min (" + str(eval_min[-1]) + ")", where='pre')
    # plt.step(eval_counts, eval_max, ls="--", label="crossbeam_max (" + str(eval_max[-1]) + ")", where='pre')

    plt.xlabel("Time in seconds")
    # plt.ylim(50)
    plt.ylabel("Programs synthesized")
    plt.legend()
    plt.title("Successes by expressions considered (Sygus)")
    plt.grid("on", linestyle=':')
    plt.savefig("./result_images/max_time.png", bbox_inches='tight')
    plt.show()
    plt.close()

    # clean up job
    os.system("rm -rf *.txt")
