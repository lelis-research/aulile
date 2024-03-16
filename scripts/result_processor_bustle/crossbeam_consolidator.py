import json
import os
from datetime import timedelta
import logging

import numpy as np


def consolidate_crossbeam_log():
    sygus_benchmarks_json_file_name = "sygus_benchmarks.json"
    sygus_benchmarks_json_file = open(sygus_benchmarks_json_file_name)
    sygus_benchmarks_json = json.load(sygus_benchmarks_json_file)
    sygus_benchmarks_names = []
    for benchmark_json in sygus_benchmarks_json:
        sygus_benchmarks_names.append(benchmark_json["name"])

    # crossbeam results of all runs
    crossbeam_results_all_runs = []
    for run in range(1, 6):
        run_results_json_file_name = "./2102/run_" + str(run) + ".vw-bustle_sig-vsize.sygus.json"
        run_results_json_file = open(run_results_json_file_name)
        run_results_json = json.load(run_results_json_file)
        crossbeam_results_all_runs.append(run_results_json["results"])

    # sygus consolidated results
    sygus_consolidated_results = []
    for benchmark_index, benchmark in enumerate(sygus_benchmarks_names):
        benchmark_statistics = {"Benchmark": benchmark}
        number_of_evaluations = []
        times_taken = []
        program_string = None
        for run in range(1, 6):
            crossbeam_run_result = crossbeam_results_all_runs[run - 1][benchmark_index]
            if crossbeam_run_result["success"] is True:
                number_of_evaluations.append(crossbeam_run_result["num_values_explored"])
                times_taken.append(crossbeam_run_result["elapsed_time"])
                program_string = crossbeam_run_result["solution"]
        if len(number_of_evaluations) > 0:
            benchmark_statistics["Result"] = "Success"
            benchmark_statistics["Number of evaluations"] = np.mean(number_of_evaluations)
            benchmark_statistics["Program"] = program_string
            benchmark_statistics["Time taken"] = np.mean(times_taken)
        else:
            benchmark_statistics["Result"] = "Fail"
            benchmark_statistics["Number of evaluations"] = 1000001
            benchmark_statistics["Program"] = None
            benchmark_statistics["Time taken"] = 10000000

        sygus_consolidated_results.append(benchmark_statistics)

    # crossbeam consolidated log
    log_filename = "2102/crossbeam.log"

    for TaskId, sygus_result in enumerate(sygus_consolidated_results):
        logging.basicConfig(filename=log_filename,
                            filemode='a',
                            format="[Task: " + str(TaskId) + "] " + '%(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

        if sygus_result["Result"] == "Success":
            logging.info("Benchmark: " + sygus_result["Benchmark"])
            logging.info("Result: Success")
            logging.info("Program: " + sygus_result["Program"])
            logging.info("Number of evaluations: " + str(sygus_result["Number of evaluations"]))
            logging.info("Time taken: " + str(timedelta(seconds=sygus_result["Time taken"])))
            # logging.info("Time taken: " + str(sygus_result["Time taken"]))


def get_evaluation_stats_sygus(evaluation_limit=1000000):
    evaluation_stats = []
    crossbeam_results_all_runs = []
    all_evaluation_counts = set()
    for run in range(1, 6):
        successful_results = []
        for task_index in range(1, 90):
            run_results_json_file_name = "./2403/run_" + str(run) + ".vw-bustle_sig-vsize.sygus." + str(
                task_index) + ".json"
            if not os.path.exists(run_results_json_file_name):
                continue
            run_results_json_file = open(run_results_json_file_name)
            run_results_json = json.load(run_results_json_file)
            for run_result in run_results_json["results"]:
                if run_result["success"] is True and run_result["num_values_explored"] <= evaluation_limit:
                    successful_results.append(run_result)
            for run_result in successful_results:
                all_evaluation_counts.add(run_result["num_values_explored"])
        crossbeam_results_all_runs.append(successful_results)

    for evaluation_count in all_evaluation_counts:
        evaluation_stat = {}
        runs_evaluation_counts = []
        for run_index in range(0, 5):
            number_of_problems_solved = 0
            for run_result in crossbeam_results_all_runs[run_index]:
                if run_result["num_values_explored"] <= evaluation_count:
                    number_of_problems_solved += 1
            runs_evaluation_counts.append(number_of_problems_solved)
        evaluation_stat["min"] = min(runs_evaluation_counts)
        evaluation_stat["max"] = max(runs_evaluation_counts)
        evaluation_stat["avg"] = np.mean(runs_evaluation_counts)
        evaluation_stat["count"] = evaluation_count
        evaluation_stats.append(evaluation_stat)

    evaluation_stats = sorted(evaluation_stats, key=lambda stat: stat["count"])
    return evaluation_stats


def get_evaluation_stats_38b(evaluation_limit=1000000):
    evaluation_stats = []
    crossbeam_results_all_runs = []
    all_evaluation_counts = set()
    for run in range(1, 6):
        successful_results = []
        for task_index in range(1, 39):
            run_results_json_file_name = "./2403/run_" + str(run) + ".vw-bustle_sig-vsize.new." + str(
                task_index) + ".json"
            if not os.path.exists(run_results_json_file_name):
                continue
            run_results_json_file = open(run_results_json_file_name)
            run_results_json = json.load(run_results_json_file)
            for run_result in run_results_json["results"]:
                if run_result["success"] is True and run_result["num_values_explored"] <= evaluation_limit:
                    successful_results.append(run_result)
            for run_result in successful_results:
                all_evaluation_counts.add(run_result["num_values_explored"])
        crossbeam_results_all_runs.append(successful_results)

    for evaluation_count in all_evaluation_counts:
        evaluation_stat = {}
        runs_evaluation_counts = []
        for run_index in range(0, 5):
            number_of_problems_solved = 0
            for run_result in crossbeam_results_all_runs[run_index]:
                if run_result["num_values_explored"] <= evaluation_count:
                    number_of_problems_solved += 1
            runs_evaluation_counts.append(number_of_problems_solved)
        evaluation_stat["min"] = min(runs_evaluation_counts)
        evaluation_stat["max"] = max(runs_evaluation_counts)
        evaluation_stat["avg"] = np.mean(runs_evaluation_counts)
        evaluation_stat["count"] = evaluation_count
        evaluation_stats.append(evaluation_stat)

    evaluation_stats = sorted(evaluation_stats, key=lambda stat: stat["count"])
    return evaluation_stats


def check_38b_results_file_status():
    filenames = os.listdir("./2403/")
    filenames = [filename for filename in filenames if "new" in filename]
    tasks = set(list(range(1, 39)))
    failed_tasks = []
    for run in range(1, 6):
        for task in tasks.copy():
            run_task_filename = "run_" + str(run) + ".vw-bustle_sig-vsize.new." + str(task) + ".json"
            if run_task_filename not in filenames:
                print("Task: ", task, " run: ", run)
                tasks.remove(task)
                failed_tasks.append(task)

    print("number of failed tasks: ", len(failed_tasks))
    print("failed tasks: ", failed_tasks)


def check_sygus_results_file_status():
    filenames = os.listdir("./2403/")
    filenames = [filename for filename in filenames if "sygus" in filename]
    tasks = set(list(range(1, 90)))
    failed_tasks = []
    for run in range(1, 6):
        for task in tasks.copy():
            run_task_filename = "run_" + str(run) + ".vw-bustle_sig-vsize.sygus." + str(task) + ".json"
            if run_task_filename not in filenames:
                print("Task: ", task, " run: ", run)
                tasks.remove(task)
                failed_tasks.append(task)

    print("number of failed tasks: ", len(failed_tasks))
    print("failed tasks: ", failed_tasks)


def get_time_stats_sygus(time_limit=86400):
    time_stats = []
    crossbeam_results_all_runs = []
    all_time_periods = set()
    for run in range(1, 6):
        successful_results = []
        for task_index in range(1, 90):
            run_results_json_file_name = "./2403/run_" + str(run) + ".vw-bustle_sig-vsize.sygus."+str(task_index)+".json"
            if not os.path.exists(run_results_json_file_name):
                continue
            run_results_json_file = open(run_results_json_file_name)
            run_results_json = json.load(run_results_json_file)
            for run_result in run_results_json["results"]:
                if run_result["success"] is True and run_result["elapsed_time"] <= time_limit:
                    successful_results.append(run_result)
            for run_result in successful_results:
                all_time_periods.add(run_result["elapsed_time"])
        crossbeam_results_all_runs.append(successful_results)

    for time_period in all_time_periods:
        time_stat = {}
        runs_time_periods = []
        for run_index in range(0, 5):
            number_of_problems_solved = 0
            for run_result in crossbeam_results_all_runs[run_index]:
                if run_result["elapsed_time"] <= time_period:
                    number_of_problems_solved += 1
            runs_time_periods.append(number_of_problems_solved)
        time_stat["min"] = min(runs_time_periods)
        time_stat["max"] = max(runs_time_periods)
        time_stat["avg"] = np.mean(runs_time_periods)
        time_stat["time_period"] = time_period
        time_stats.append(time_stat)

    time_stats = sorted(time_stats, key=lambda stat: stat["time_period"])
    return time_stats


def get_time_stats_38b(time_limit=86400):
    time_stats = []
    crossbeam_results_all_runs = []
    all_time_periods = set()
    for run in range(1, 6):
        successful_results = []
        for task_index in range(1, 39):
            run_results_json_file_name = "./2403/run_" + str(run) + ".vw-bustle_sig-vsize.new."+str(task_index)+".json"
            if not os.path.exists(run_results_json_file_name):
                continue
            run_results_json_file = open(run_results_json_file_name)
            run_results_json = json.load(run_results_json_file)
            for run_result in run_results_json["results"]:
                if run_result["success"] is True and run_result["elapsed_time"] <= time_limit:
                    successful_results.append(run_result)
            for run_result in successful_results:
                all_time_periods.add(run_result["elapsed_time"])
        crossbeam_results_all_runs.append(successful_results)

    for time_period in all_time_periods:
        time_stat = {}
        runs_time_periods = []
        for run_index in range(0, 5):
            number_of_problems_solved = 0
            for run_result in crossbeam_results_all_runs[run_index]:
                if run_result["elapsed_time"] <= time_period:
                    number_of_problems_solved += 1
            runs_time_periods.append(number_of_problems_solved)
        time_stat["min"] = min(runs_time_periods)
        time_stat["max"] = max(runs_time_periods)
        time_stat["avg"] = np.mean(runs_time_periods)
        time_stat["time_period"] = time_period
        time_stats.append(time_stat)

    time_stats = sorted(time_stats, key=lambda stat: stat["time_period"])
    return time_stats


# check_38b_results_file_status()
# check_sygus_results_file_status()
# print(get_time_stats_sygus())
# print(get_time_stats_38b())
print(get_evaluation_stats_sygus())
