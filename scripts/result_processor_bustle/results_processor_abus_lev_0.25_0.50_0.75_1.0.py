import subprocess
import sys

import matplotlib.pylab as plt
import pandas as pd
import numpy as np

def get_time_in_seconds(timestr):
    time_splits = timestr.split(":")
    seconds = int(time_splits[0]) * 60 * 60 + int(time_splits[1]) * 60 + int(time_splits[2].split(".")[0])
    return seconds


if __name__ == "__main__":

    source_directory = sys.argv[1]
    
    benchmark_file_name = "sygus"
    logs = ["A-BUS_Lev_1.0.log", "A-BUS_Lev_0.25.log", "A-BUS_Lev_0.50.log", "A-BUS_Lev_0.75.log"]
    logkeys = ["A-BUS_Lev_1.0", "A-BUS_Lev_0.25", "A-BUS_Lev_0.50", "A-BUS_Lev_0.75"]
    script_name = "./processor_script.sh"

    for key, logfile in enumerate(logs):
        logkey = logkeys[key]
        script_result = subprocess.check_call([script_name, "./" + source_directory + "/" + logfile, logkey])
        print(script_result)

    benchmark_results = {}

    with open("bustle_benchmarks") as f:
        all_benchmarks = f.read().splitlines()

    for benchmark in all_benchmarks:
        stats = {"benchmark": benchmark}
        for logkey in logkeys:
            stats[logkey + "_result"] = "Fail"
            stats[logkey + "_program"] = "None"
            stats[logkey + "_time"] = 3600
            stats[logkey + "_evaluations"] = 100000000
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

            stats = benchmark_results.get(benchmark)
            if stats is None:
                stats = {"benchmark": benchmark}
                benchmark_results[benchmark] = stats
            stats[logkey + "_result"] = results[index]
            stats[logkey + "_program"] = programs[index]
            stats[logkey + "_time"] = get_time_in_seconds(str(times[index]))
            stats[logkey + "_evaluations"] = evaluations[index]

    statistics = []

    for key, value in benchmark_results.items():
        statistics.append(value)

    dataFrame = pd.DataFrame(statistics)
    # dataFrame.to_csv("statistics.csv", index=False)

    statistics = dataFrame.to_dict('records')

    evaluations_map = {}
    times_map = {}
    success_counts = {}
    
    evaluations_values_map = {}
    times_values_map = {}
    
    max_evaluations = 0
    max_time = 0
    
    min_evaluations = sys.maxsize
    min_time = sys.maxsize

    for logkey in logkeys:

        evaluations = []
        times = []
        for benchmark_stat in statistics:
            if benchmark_stat[logkey + "_result"] == "Success":
                evaluations.append(int(benchmark_stat[logkey + "_evaluations"]))
                times.append(int(benchmark_stat[logkey + "_time"]))

        evaluations.sort()
        times.sort()

        sum_of_evaluations = 0
        sum_of_times = 0
        
        evaluation_results = {}
        time_results = {}

        for index, evaluation in enumerate(evaluations):
            sum_of_evaluations += int(evaluation)
            evaluation_results[sum_of_evaluations] = index + 1

        for index, time in enumerate(times):
            sum_of_times += time
            time_results[sum_of_times] = index + 1

        if sum_of_evaluations > max_evaluations:
            max_evaluations = sum_of_evaluations

        if sum_of_times > max_time:
            max_time = sum_of_times

        if sum_of_evaluations < min_evaluations:
            min_evaluations = sum_of_evaluations

        if sum_of_times < min_time:
            min_time = sum_of_times

        evaluations_map[logkey] = evaluation_results
        times_map[logkey] = time_results
        success_counts[logkey] = len(evaluations)
        evaluations_values_map[logkey] = evaluations
        times_values_map[logkey] = times
    
    
    x_list = np.arange(0, max_evaluations + 5e3, 5e3)
    x_list_time = np.arange(0, max_time + 1, 1)
    
    eval_combined_dataframe = {}
    eval_combined_dataframe["evaluations"] = x_list
    time_combined_dataframe = {}
    time_combined_dataframe["times"] = x_list_time
    
    for logkey in logkeys:
        expressions = np.array(list(evaluations_values_map[logkey]))
        times_result = np.array(list(times_values_map[logkey]))
        eval_combined_dataframe[logkey] = []
        time_combined_dataframe[logkey] = []
        for evals in x_list:
            eval_combined_dataframe[logkey].append(np.count_nonzero(expressions <= evals))
        for times_ in x_list_time:
            time_combined_dataframe[logkey].append(np.count_nonzero(times_result <= times_))
    
    eval_combined_dataframe = pd.DataFrame(eval_combined_dataframe)
    time_combined_dataframe = pd.DataFrame(time_combined_dataframe)
    
    print(eval_combined_dataframe.head())
    print(time_combined_dataframe.head())
    
    file_name = ""
    for logkey in logkeys:
        file_name += logkey + "_"
    
    # save the dataframes
    eval_combined_dataframe.to_csv(benchmark_file_name + "_" + file_name + "evaluations_statistics.csv", index=False)
    time_combined_dataframe.to_csv(benchmark_file_name + "_" + file_name + "times_statistics.csv", index=False)
    
    
    # Normalizes all the results to the maximum availble result
    # for key,value in evaluations_map.items():
    # value[max_evaluations] = success_counts[key]

    # for key,value in times_map.items():
    # value[max_time] = success_counts[key]
    
    for key, value in evaluations_map.items():
        expressions = list(value.keys())
        tasks = list(value.values())
        plot_expressions = []
        plot_tasks = []
        for index, expression in enumerate(expressions):
            if expression <= min_evaluations:
                plot_expressions.append(expression)
                plot_tasks.append(tasks[index])
        if plot_expressions[-1] != min_evaluations:
            plot_expressions.append(min_evaluations)
            plot_tasks.append(plot_tasks[-1])
        print("key: ", key)
        print("expressions: ", plot_expressions)
        print("tasks: ", plot_tasks)
        plt.step(plot_expressions, plot_tasks, label=key, where='pre')
        plt.text(plot_expressions[-1], plot_tasks[-1], plot_tasks[-1])
    
    # for key,value in evaluations_map.items():
    # expressions = list(value.keys())
    # tasks = list(value.values())
    # plt.step(expressions,tasks,label=key,where='pre')
    
    plt.xlabel("Number of candidate expressions considered")
    plt.ylabel("Programs synthesized")
    plt.legend()
    # plt.yticks(np.arange(0,85,1))
    plt.title("Successes by expressions considered")
    # plt.savefig("./result_images/ran_expr.png", bbox_inches='tight')
    plt.show()
    plt.close()

    for key, value in times_map.items():
        times = list(value.keys())
        tasks = list(value.values())
        plot_times = []
        plot_tasks = []
        for index, time in enumerate(times):
            if time <= min_time:
                plot_times.append(time)
                plot_tasks.append(tasks[index])
        if plot_times[-1] != min_time:
            plot_times.append(min_time)
            plot_tasks.append(plot_tasks[-1])
        print("key: ", key)
        print("times: ", plot_times)
        print("tasks: ", plot_tasks)
        plt.step(plot_times, plot_tasks, label=key, where='pre')
        plt.text(plot_times[-1], plot_tasks[-1], plot_tasks[-1])
    
    # for key,value in times_map.items():
    # times = list(value.keys())
    # tasks = list(value.values())
    # plt.step(times,tasks,label=key,where='pre')
    
    plt.xlabel("Elapsed Time(s)")
    plt.ylabel("Programs synthesized")
    # plt.yticks(np.arange(0,85,1))
    plt.legend()
    plt.title("Successes by Time Elapsed")
    # plt.savefig("./result_images/ran_time.png", bbox_inches='tight')
    plt.show()
    plt.close()
    