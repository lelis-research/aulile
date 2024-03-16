import logging
import os
import sys
from datetime import datetime

import numpy as np
import tensorflow.keras.models as keras_model

from bustle_properties import *
from bustle_string_dsl import *
from sygus_parser import StrParser
from bm_38_parser import StrParser38
from utils import *

from Levenshtein import distance

import argparse

outputsPartialProgs = set()
added_partialprogs = []


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
        self.property_encodings = {
            AllTrue: EncodedAllTrue,
            AllFalse: EncodedAllFalse,
            Mixed: EncodedMixed,
            Padding: EncodedPadding
        }

        max_string_variables = 3

        # input strings with string only properties
        for string_variable in string_variables_list:
            input_strings = [parent_input.get(string_variable) for parent_input in self.parent_input_output]
            for StringProperty in StringProperties:
                property_value = StringProperty(input_strings)
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        for padding_index in range(0, max_string_variables - len(string_variables_list)):
            for _ in StringProperties:
                property_value = Padding
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        # output string with string only properties
        output_strings = [parent_output['out'] for parent_output in self.parent_input_output]
        for StringProperty in StringProperties:
            property_value = StringProperty(output_strings)
            populate_property_value(self.parent_ps, self.property_encodings[property_value])

        # input strings and output string with string-string properties
        for string_variable in string_variables_list:
            for InputStringOutputStringProperty in InputStringOutputStringProperties:
                property_value = InputStringOutputStringProperty(self.parent_input_output, string_variable)
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

        for padding_index in range(0, max_string_variables - len(string_variables_list)):
            for _ in InputStringOutputStringProperties:
                property_value = Padding
                populate_property_value(self.parent_ps, self.property_encodings[property_value])

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

                # boolean output of subexpression with boolean only properties
                if program.getReturnType() == BOOL_TYPES['type']:
                    for BooleanProperty in BooleanProperties:
                        property_value = BooleanProperty(outputs)
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in BooleanProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                # integer output of expression with integer only properties -
                if program.getReturnType() == INT_TYPES['type']:
                    for IntegerProperty in IntegerProperties:
                        property_value = IntegerProperty(outputs)
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in IntegerProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                # string output of subexpression with string only properties
                if program.getReturnType() == STR_TYPES['type']:
                    for StringProperty in StringProperties:
                        property_value = StringProperty(outputs)
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in StringProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                # integer output of subexpression and string output of main expression with integer-string properties
                if program.getReturnType() == INT_TYPES['type']:
                    for InputInterOutputStringProperty in InputIntegerOutputStringProperties:
                        property_value = InputInterOutputStringProperty(child_input_outputs, 'cout')
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in InputIntegerOutputStringProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                # string output of subexpression and string output of main expression with string-string properties
                if program.getReturnType() == STR_TYPES['type']:
                    for InputStringOutputStringProperty in InputStringOutputStringProperties:
                        property_value = InputStringOutputStringProperty(child_input_outputs, 'cout')
                        populate_property_value(test_row, self.property_encodings[property_value])
                else:
                    for _ in InputStringOutputStringProperties:
                        property_value = Padding
                        populate_property_value(test_row, self.property_encodings[property_value])

                current_batch_ps.append(test_row)

            current_batch_predictions = BustleModel.predict(np.array(current_batch_ps))

            for program_index, program in enumerate(current_batch):

                program_size = program.size

                # Reweighing the size of the program as per BUSTLE algorithm using the neural model

                program_probability = current_batch_predictions[program_index]

                if program_probability <= 0.1:
                    program_size += 5
                elif program_probability <= 0.2:
                    program_size += 4
                elif program_probability <= 0.3:
                    program_size += 3
                elif program_probability <= 0.4:
                    program_size += 2
                elif program_probability <= 0.6:
                    program_size += 1

                program.size = program_size

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
                   string_variables_list, integer_variables_list, added_partialprogs):
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

        if len(added_partialprogs) > 0:
            for pprog in added_partialprogs:
                pprog.size = 1
                self.init_insert(pprog)

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

    def __init__(self, string_variables_list, integer_variables_list, input_output, started_number_evaluations, started_unique_evaluations):
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

    def is_partial_solution(self, p):

        is_partial_program = False
        average_scores = float('inf')

        for inout in self._input_output:
            env = self.init_env(inout)
            out = p.interpret(env)
            if out == inout['out']:
                is_partial_program = True

        if is_partial_program:

            eval_scores = []
            for inout in self._input_output:
                env = self.init_env(inout)
                out = p.interpret(env)

                if not type(out) == str:
                    out = str(out)
                if not type(inout['out']) == str:
                    inout['out'] = str(inout['out'])

                eval_scores.append(distance(out, inout['out']))
            average_scores = sum(eval_scores) / len(eval_scores)

        return is_partial_program, average_scores

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

    def has_equivalent_partialprogs(self, program):
        p_out = []
        for inout in self._input_output:
            env = self.init_env(inout)
            out = program.interpret(env)
            if out is not None:
                p_out.append(out)
            else:
                return True

        tuple_out = tuple(p_out)

        if tuple_out not in outputsPartialProgs:
            outputsPartialProgs.add(tuple_out)
            return False
        return True

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
               integer_variables_list, added_partialprogs):

        self.plist.init_plist(string_literals_list, integer_literals_list, string_variables_list,
                              integer_variables_list, added_partialprogs)

        logging.info('Number of programs: ' + str(self.plist.get_number_programs()))

        number_evaluations_Onesearch = 0
        current_size = 0
        partialprog_number = 0
        candidate_partialprogram_list = []
        candidate_pprog_scores = []

        while current_size <= bound:

            number_evaluations_bound = 0

            for new_program in self.grow(operations, current_size):

                self.unique_evaluations += 1
                number_evaluations_Onesearch += 1
                number_evaluations_bound += 1

                is_p_correct = self.is_correct(new_program)
                if is_p_correct:
                    return new_program, self.number_evaluations, candidate_partialprogram_list, candidate_pprog_scores, partialprog_number, current_size, self.unique_evaluations


                else:
                    is_p_partial_program, sc = self.is_partial_solution(new_program)

                    if is_p_partial_program:

                        if not self.has_equivalent_partialprogs(new_program):
                            candidate_pprog_scores.append(sc)

                            partialprog_number += 1
                            candidate_partialprogram_list.append(new_program)

                if number_evaluations_Onesearch > program_limit:
                    return None, self.number_evaluations, candidate_partialprogram_list, candidate_pprog_scores, partialprog_number, current_size, self.unique_evaluations

            logging.info('Size: ' + str(current_size) + ' Evaluations: ' + str(number_evaluations_bound))
            current_size += 1

        return None, self.number_evaluations, candidate_partialprogram_list, candidate_pprog_scores, partialprog_number, current_size, self.unique_evaluations

    def synthesize(self, bound, operations, string_literals_list, integer_literals_list,
                   string_variables_list,
                   integer_variables_list, added_partialprogs):

        BustlePCFG.initialize(operations, string_literals_list, integer_literals_list,
                              string_variables_list)

        program_solution, evaluations, candidate_partialprogram_list, candidate_pprog_scores, partialprog_number, depth, unique_evaluations = self.search(
            bound, operations, string_literals_list, integer_literals_list,
            string_variables_list, integer_variables_list, added_partialprogs)

        return program_solution, evaluations, candidate_partialprogram_list, candidate_pprog_scores, partialprog_number, depth, unique_evaluations


def load_bustle_model(model_filename):
    logging.info("Loading bustle model....")
    global BustleModel
    model_filename = models_directory + model_filename
    os.makedirs(os.path.dirname(model_filename), exist_ok=True)
    BustleModel = keras_model.load_model(model_filename)


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
        default="BUSTLE_Augmented_sygus.log",
        type=str,
        help="Log filename - if not specified, defaults to BUSTLE_Augmented_sygus.log",
    )

    parser.add_argument(
        "-m",
        "--model",
        dest="model_filename",
        default="EncodedBustleModelforPS_1234.hdf5",
        type=str,
        help="Model filename - if not specified, defaults to EncodedBustleModelforPS_1234.hdf5",
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

    parser.add_argument(
        "-p",
        "--program_limit",
        dest="program_limit",
        default=14000000,
        type=int,
        help="Program Limit - Number of programs evaluated before augmenting. If not specified, defaults to 14 million.",
    )


    parameters = parser.parse_args()
    TaskId = parameters.TaskId - 1
    log_filename = logs_directory + parameters.log_filename
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    
    model_filename = parameters.model_filename
    benchmark_filename = parameters.benchmark_filename
    benchmark_name = parameters.benchmark_name
    global program_limit
    program_limit = parameters.program_limit

    logging.basicConfig(filename=log_filename,
                        filemode='a',
                        format="[Task: " + str(TaskId) + "] " + '%(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    load_bustle_model(model_filename)

    with open(config_directory + benchmark_filename) as f:
        benchmarks = f.read().splitlines()

    logging.info('TaskId: ' + str(TaskId))
    
    benchmark = None
    
    filename = benchmarks[TaskId]

    benchmark = filename

    specification_parser = StrParser(benchmark) if benchmark_name == 'sygus' else StrParser38(benchmark)
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
    solution, num_evaluations, candidate_partialprogram_list, candidate_pprog_scores, partialprog_number, depth, unique_evaluations = synthesizer.synthesize(
        float('inf'), dsl_functions,
        string_literals,
        integer_literals,
        string_variables,
        integer_variables, added_partialprogs)

    if solution is not None:
        logging.info("Benchmark: " + str(benchmark))
        logging.info("Result: Success")
        logging.info("Program: " + solution.toString())
        logging.info("Program size: " + str(solution.size))
        logging.info("Number of evaluations: " + str(num_evaluations))
        logging.info("Number of unique evaluations: " + str(unique_evaluations))
        logging.info("Number of Iterations: " + str(1))
        logging.info(str(datetime.now()))
        logging.info("Time taken: " + str(datetime.now() - begin_time))
        # create a file named taskid_model_augmented/not_augmented.txt inside results folder
        with open(
            "../results/"
            + benchmark_name
            + "_"
            + 'A-Bustle_'
            + str(TaskId + 1)
            + "_"
            + str(model_filename)
            + "_"
            + str(1)
            + ".txt",
            "w",
        ) as f:
            f.write("Program: " + solution.toString() + "\n")
            f.write("Number of evaluations: " + str(num_evaluations) + "\n")
            f.close()
    else:
        num_iter = 0
        for i in range(10):
            num_iter += 1
            logging.info('Iteration number : ' + str(i))
            logging.info('Num of total candidate partial progs: ' + str(partialprog_number))

            logging.info("\n")

            min_ind = (np.array(candidate_pprog_scores)).argsort()[:(i + 1)]

            for counter in range(len(min_ind)):
                added_partialprogs.append(candidate_partialprogram_list[min_ind[counter]])

                logging.info('partial program added to the DSL: ' + candidate_partialprogram_list[
                    min_ind[counter]].toString())
                logging.info("\n")
                
            number_evaluations_sofar = synthesizer.number_evaluations
            unique_evaluations_sofar = synthesizer.unique_evaluations 
            synthesizer = BottomUpSearch(string_variables, integer_variables, input_output_examples, started_number_evaluations = number_evaluations_sofar, started_unique_evaluations=unique_evaluations_sofar)
            logging.info(str(datetime.now()))
            #begin_time = datetime.now()
            solution, num_evaluations, candidate_partialprogram_list, candidate_pprog_scores, partialprog_number, depth, unique_evaluations = synthesizer.synthesize(
                float("inf"), dsl_functions,
                string_literals,
                integer_literals,
                string_variables,
                integer_variables, added_partialprogs)

            logging.info("The depth of augmented BUS: " + str(depth))
            logging.info("\n")

            if solution is not None:
                logging.info("Benchmark: " + str(benchmark))
                logging.info("Result: Success")
                logging.info("Program: " + solution.toString())
                logging.info("Program size: " + str(solution.size))
                logging.info("Number of evaluations: " + str(num_evaluations))
                logging.info("Number of unique evaluations: " + str(unique_evaluations))
                logging.info("Number of Iterations: " + str(num_iter))
                logging.info(str(datetime.now()))
                logging.info("Time taken: " + str(datetime.now() - begin_time))
                
                # create a file named taskid_model_augmented/not_augmented.txt inside results folder
                with open(
                    "../results/"
                    + benchmark_name
                    + "_"
                    + 'A-Bustle_'
                    + str(TaskId + 1)
                    + "_"
                    + str(model_filename)
                    + "_"
                    + str(1)
                    + ".txt",
                    "w",
                ) as f:
                    f.write("Program: " + solution.toString() + "\n")
                    f.write("Number of evaluations: " + str(num_evaluations) + "\n")
                    f.close()
                
                break

        if solution is None:
            logging.info("Benchmark: " + str(benchmark))
            logging.info("Result: Fail")
            logging.info("Program: None")
            logging.info("Program size: " + str(solution.size))
            logging.info("Number of evaluations: " + str(num_evaluations))
            logging.info("Number of unique evaluations: " + str(unique_evaluations))
            logging.info("Number of Iterations: " + str(num_iter))
            logging.info(str(datetime.now()))
            logging.info("Time taken: " + str(datetime.now() - begin_time))

        logging.info("\n\n")