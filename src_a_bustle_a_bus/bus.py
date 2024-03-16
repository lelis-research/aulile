import logging
import os
import sys
from datetime import datetime

import numpy as np

from bustle_properties import *
from bustle_string_dsl import *
from sygus_parser import StrParser
from bm_38_parser import StrParser38
from utils import *

import argparse

def populate_property_value(property_signature, property_encoding):
    for encoding in property_encoding:
        property_signature.append(encoding)


class ProgramList:

    def __init__(self, string_variables_list, integer_variables_list, input_output):
        self.plist = {}
        self.number_programs = 0
        self.parent_input_output = input_output
        self.string_variables = string_variables_list
        self.integer_variables = integer_variables_list
        self.parent_ps = []
        self.batch_jobs = []

    def insert(self, program):
        self.batch_jobs.append(program)

    def process_batch_jobs(self):

        batch_size = 100000
        total_jobs = len(self.batch_jobs)

        for job_index in range(0, total_jobs, batch_size):

            current_batch = self.batch_jobs[job_index:job_index + batch_size]
            current_batch_ps = []

            for program in current_batch:

                test_row = self.parent_ps.copy()
                child_input_outputs = []

                for index, parent_input in enumerate(self.parent_input_output):
                    child_input_output = parent_input.copy()
                    child_output = program.interpret(child_input_output)
                    child_input_output['cout'] = child_output
                    child_input_output['out'] = self.parent_input_output[index]['out']
                    child_input_outputs.append(child_input_output)

                outputs = [output['cout'] for output in child_input_outputs]

            for program_index, program in enumerate(current_batch):

                # program_size = program.size

                # Reweighing the size of the program as per BUSTLE algorithm using the neural model

                # program.size = program_size

                if program.size not in self.plist:
                    self.plist[program.size] = {}

                if program.getReturnType() not in self.plist[program.size]:
                    self.plist[program.size][program.getReturnType()] = []

                self.plist[program.size][program.getReturnType()].append(program)
                self.number_programs += 1

        self.batch_jobs.clear()

    def init_insert(self, program):

        if program.size not in self.plist:
            self.plist[program.size] = {}

        if program.getReturnType() not in self.plist[program.size]:
            self.plist[program.size][program.getReturnType()] = []

        self.plist[program.size][program.getReturnType()].append(program)
        self.number_programs += 1

    def init_plist(self, string_literals_list, integer_literals_list,
                   string_variables_list, integer_variables_list):
        for string_literal in string_literals_list:
            init_program = StrLiteral(string_literal)
            self.init_insert(init_program)

        for integer_literal in integer_literals_list:
            init_program = IntLiteral(integer_literal)
            self.init_insert(init_program)

        for str_var in string_variables_list:
            init_program = StrVar(str_var)
            self.init_insert(init_program)

        for int_var in integer_variables_list:
            init_program = IntVar(int_var)
            self.init_insert(init_program)

        # self.process_batch_jobs()

    def get_programs_all(self, size):

        if size in self.plist:
            programs = []
            for value in self.plist[size].values():
                programs.extend(value)
            return programs

        return []

    def get_programs(self, size, return_type):

        if size in self.plist:
            if return_type in self.plist[size]:
                return self.plist[size][return_type]

        return []

    def get_number_programs(self):
        return self.number_programs


class BottomUpSearch:

    def __init__(self, string_variables_list, integer_variables_list, input_output,started_number_evaluations, started_unique_evaluations):
        self._variables = string_variables_list + integer_variables_list
        self._input_output = input_output
        self.plist = ProgramList(string_variables_list, integer_variables_list, input_output)
        self._outputs = set()
        self.closed_list = set()
        self.number_evaluations = started_number_evaluations
        self.unique_evaluations = started_unique_evaluations


    def is_correct(self, p):
        is_program_correct = True

        for inout in self._input_output:
            env = self.init_env(inout)
            out = p.interpret(env)
            if out != inout['out']:
                is_program_correct = False

        return is_program_correct

    def init_env(self, inout):
        env = {}
        for v in self._variables:
            env[v] = inout[v]
        return env

    def has_equivalent(self, program):
        p_out = []
        for inout in self._input_output:
            env = self.init_env(inout)
            out = program.interpret(env)
            if out is not None:
                p_out.append(out)
            else:
                return False, True

        tuple_out = tuple(p_out)

        if tuple_out not in self._outputs:
            self._outputs.add(tuple_out)
            return True, False
        return True, True

    def grow(self, operations, size):
        new_programs = []
        for operation in operations:
            for new_program in operation.grow(self.plist, size):
                # print(p.toString)
                is_valid, has_equivalent = self.has_equivalent(new_program)
                if is_valid:
                    self.number_evaluations += 1
                if new_program.toString() not in self.closed_list and not has_equivalent:
                    self.closed_list.add(new_program)
                    new_programs.append(new_program)
                    yield new_program

        for new_program in new_programs:
            self.plist.insert(new_program)

        self.plist.process_batch_jobs()

    def search(self, bound, operations, string_literals_list, integer_literals_list,
               string_variables_list,
               integer_variables_list):

        self.plist.init_plist(string_literals_list, integer_literals_list, string_variables_list,
                              integer_variables_list)

        logging.info('Number of programs: ' + str(self.plist.get_number_programs()))

        current_size = 0

        while current_size <= bound:

            number_evaluations_bound = 0

            for new_program in self.grow(operations, current_size):
                self.unique_evaluations += 1
                number_evaluations_bound += 1
                is_p_correct = self.is_correct(new_program)
                if is_p_correct:
                    return new_program, self.number_evaluations, self.unique_evaluations

            logging.info('Size: ' + str(current_size) + ' Evaluations: ' + str(number_evaluations_bound))
            current_size += 1

        return None, self.number_evaluations, self.unique_evaluations

    def synthesize(self, bound, operations, string_literals_list, integer_literals_list,
                   string_variables_list,
                   integer_variables_list):

        BustlePCFG.initialize(operations, string_literals_list, integer_literals_list,
                              string_variables_list)

        program_solution, evaluations, unique_evaluations = self.search(bound, operations, string_literals_list,
                                                                        integer_literals_list,
                                                                        string_variables_list, integer_variables_list)

        return program_solution, evaluations, unique_evaluations


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t",
        "--task_id",
        dest="TaskId",
        default=57,
        type=int,
        help="Define the task id from bustle_benchmarks.txt to solve.",
    )

    parser.add_argument(
        "-l",
        "--log",
        dest="log_filename",
        default="BUS_sygus.log",
        type=str,
        help="Log filename - if not specified, defaults to BUS_sygus.log",
    )

    parser.add_argument(
        "-b",
        "--benchmark",
        dest="benchmark_filename",
        default="bustle_benchmarks.txt",
        type=str,
        help="Benchmarks filename - if not specified, defaults to bustle_benchmarks.txt",
    )
    
    parser.add_argument(
        "-bn",
        "--benchmark_name",
        dest="benchmark_name",
        default="sygus",
        type=str,
        help="Benchmarks name - if not specified, defaults to sygus. Possible values: sygus, and 38",
    )


    parameters = parser.parse_args()
    TaskId = parameters.TaskId - 1
    log_filename = logs_directory + parameters.log_filename
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    
    benchmark_filename = parameters.benchmark_filename
    benchmark_name = parameters.benchmark_name
    
    logging.basicConfig(filename=log_filename,
                        filemode='a',
                        format="[Task: " + str(TaskId) + "] " + '%(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    with open(config_directory + benchmark_filename) as f:
        benchmarks = f.read().splitlines()

    logging.info('TaskId: ' + str(TaskId))
    benchmark = None
    
    filename = benchmarks[TaskId]
    
    benchmark = filename

    specification_parser = StrParser(benchmark) if benchmark_name == "sygus" else StrParser38(benchmark)
    specifications = specification_parser.parse()

    logging.info("\n")

    dsl_functions = [IntPlus, StrConcat, IntFirstIndexOf, IntIndexOf, StrLeftSubstr,
                        IntLength, StrSubstr, IntMinus, StrReplaceAdd, StrRightSubstr,
                        StrTrim, StrLower, StrUpper, StrProper, StrRepeat, StrReplace,
                        StrReplaceOccurence, StrIntToStr, StrIte, BoolEqual, BoolGreaterThan,
                        BoolGreaterThanEqual]

    string_variables = specifications[0]
    string_literals = specifications[1]
    integer_variables = specifications[2]
    integer_literals = specifications[3]

    input_output_examples = specifications[4]

    synthesizer = BottomUpSearch(string_variables, integer_variables, input_output_examples,started_number_evaluations = 0, started_unique_evaluations = 0)
    logging.info(str(datetime.now()))
    begin_time = datetime.now()
    solution, num, unique_eval = synthesizer.synthesize(40, dsl_functions,
                                                        string_literals,
                                                        integer_literals,
                                                        string_variables,
                                                        integer_variables)

    if solution is not None:
        logging.info("Benchmark: " + str(benchmark))
        logging.info("Result: Success")
        logging.info("Program: " + solution.toString())
        logging.info("Number of evaluations: " + str(num))
        logging.info("Number of unique evaluations: " + str(unique_eval))
        logging.info(str(datetime.now()))
        logging.info("Time taken: " + str(datetime.now() - begin_time))
        # create a file named taskid_model_augmented/not_augmented.txt inside results folder
        with open(
            "../results/"
            + benchmark_name
            + "_"
            + 'BUS_'
            + str(TaskId + 1)
            + "_"
            + str(0)
            + ".txt",
            "w",
        ) as f:
            f.write("Program: " + solution.toString() + "\n")
            f.write("Number of evaluations: " + str(num) + "\n")
            f.close()
    else:
        logging.info("Benchmark: " + str(benchmark))
        logging.info("Result: Fail")
        logging.info("Program: None")
        logging.info("Number of evaluations: " + str(num))
        logging.info("Number of unique evaluations: " + str(unique_eval))
        logging.info(str(datetime.now()))
        logging.info("Time taken: " + str(datetime.now() - begin_time))

    logging.info("\n\n")
