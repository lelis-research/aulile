from ast import In
import logging
import os
import sys
from datetime import datetime, timedelta
import heapq
import bisect
import math

import numpy as np
import tensorflow.keras.models as keras_model
from scipy.interpolate import CubicSpline

from sygus_string_dsl import *
from sygus_parser import StrParser
from bm_38_parser import StrParser38
from utils import *

import argparse
from Levenshtein import distance


limit_decimal_places = True


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

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

    benchmark_filename = parameters.benchmark_filename
    benchmark_name = parameters.benchmark_name


    with open(config_directory + benchmark_filename) as f:
        benchmarks = f.read().splitlines()

        string_variables = []
        string_literals = []
        integer_variables = []
        integer_literals = []

    for index, filename in enumerate(benchmarks):
        specification_parser = StrParser(filename) if benchmark_name == "sygus" else StrParser38(filename)
        specifications = specification_parser.parse()
        string_variables = list(set(string_variables + specifications[0]))
        string_literals = list(set(string_literals + specifications[1]))
        integer_variables = list(set(integer_variables + specifications[2]))
        integer_literals = list(set(integer_literals + specifications[3]))
    lowercase_alphabets = set(
        [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
        ]
    )
    uppercase_alphabets = set(
        [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ]
    )
    all_alphabets = list(uppercase_alphabets.union(uppercase_alphabets))
    string_literals = list(set(string_literals + all_alphabets))

    benchmark = None

    benchmark = filename

    specification_parser = StrParser(benchmark) if benchmark_name == "sygus" else StrParser38(benchmark)
    specifications = specification_parser.parse()
    logging.info("\n")
    # Sygus grammar.
    dsl_functions = [
        StrConcat,
        StrReplace,
        StrSubstr,
        StrIte,
        StrIntToStr,
        StrCharAt,
        StrLower,
        StrUpper,
        IntStrToInt,
        IntPlus,
        IntMinus,
        IntLength,
        IntIteInt,
        IntIndexOf,
        IntFirstIndexOf,
        IntMultiply,
        IntModulo,
        BoolEqual,
        BoolContain,
        BoolSuffixof,
        BoolPrefixof,
        BoolGreaterThan,
        BoolLessThan,
    ]

    string_variables = specifications[0]
    integer_variables = specifications[2]
    string_literals = list(set(specifications[1] + string_literals))
    integer_literals = list(set(specifications[3] + integer_literals))
        
    BustlePCFG.initialize(
        dsl_functions,
        string_literals,
        integer_literals,
        [True, False],
        string_variables,
        integer_variables,
    )
    
    # Boolean classes and terminals

    # BOOL_TYPES = {'type': 'boolean', 'classes': (BoolLiteral, BoolEqual, BoolContain,
    #                                             BoolSuffixof, BoolPrefixof, BoolGreaterThan, BoolGreaterThan)}
    # TERMINALS = [StrLiteral, StrVar, IntLiteral, IntVar, BoolLiteral]


    # NON_TERMINALS = [StrConcat, StrReplace, StrSubstr, StrIte, StrIntToStr, StrCharAt, StrLower, StrUpper, IntStrToInt,
    #                 IntPlus, IntMinus, IntLength, IntIteInt, IntIndexOf, IntFirstIndexOf, IntMultiply, IntModulo,
    #                 BoolEqual, BoolContain, BoolSuffixof, BoolPrefixof, BoolGreaterThan, BoolLessThan]


    _arg_0 = StrLiteral("US")
    _arg_1 = StrLiteral("CA")
    _arg_2 = StrLiteral("MX")
    # program1 = _arg_0.Substr(0,(_arg_0.replace("US", "CAN").replace("CAN", _arg_0).Length() % (_arg_0.Length() + 1)))

    # programObject1 = StrSubstr(_arg_0, IntLiteral(0), IntModulo(IntLength(StrReplace(_arg_0, StrLiteral("US"), StrLiteral("CAN"))), IntPlus(IntLength(StrReplace(_arg_0, StrLiteral("US"), StrLiteral("CAN"))), IntLiteral(1))))
    # print("Program Size: ", programObject1.size)

    # print(_arg_0.size)
    # program1 = _arg_0.Substr(0,(_arg_0.IndexOf("/",(3 * 3)) + (_arg_0.Length() % 2)))
    programObject1 = StrSubstr(_arg_0, IntLiteral(0), IntPlus(IntIndexOf(_arg_0, StrLiteral("/"), IntMultiply(IntLiteral(3), IntLiteral(3))), IntModulo(IntLength(_arg_0), IntLiteral(2)))); print("Size_1: ", programObject1.size)
    # program2 = concat(concat(_arg_0.CharAt(0), concat(_arg_1, "_")), _arg_2)
    programObject2 = StrConcat(StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), _arg_1), StrLiteral("_")), _arg_2); print("Size_2: ", programObject2.size)
    # program3 = _arg_0.replace(_arg_0.Substr(1,_arg_0.IndexOf(" ")), "")
    programObject3 = StrReplace(_arg_0, StrSubstr(_arg_0, IntLiteral(1), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))), StrLiteral("")); print("Size_3: ", programObject3.size)
    # program4 = _arg_0.replace(_arg_0.lower(), _arg_1)
    programObject4 = StrReplace(_arg_0, StrLower(_arg_0), _arg_1); print("Size_4: ", programObject4.size)
    # program5 = name.Substr(0,3)
    programObject5 = StrSubstr(_arg_0, IntLiteral(0), IntLiteral(3)); print("Size_5: ", programObject5.size)
    # program6 = _arg_0.Substr(0,(_arg_0.IndexOf("Inc") + -1))
    programObject6 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("Inc"), IntLiteral(1)), IntLiteral(1))); print("Size_6: ", programObject6.size)
    # program7 = col2.replace(col2.replace("USA", col2), concat(col2, concat(",", concat(" ", "USA"))))
    programObject7 = StrReplace(_arg_0, StrReplace(_arg_0, StrLiteral("USA"), _arg_0), StrConcat(_arg_0, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrLiteral("USA"))))); print("Size_7: ", programObject7.size)
    # program8 = _arg_0.replace(",", "").replace("1", "apple").replace("2", "bananas").replace("3", "strawberries").replace("4", "oranges")
    programObject8 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral(","), StrLiteral("")), StrLiteral("1"), StrLiteral("apple")), StrLiteral("2"), StrLiteral("bananas")), StrLiteral("3"), StrLiteral("strawberries")), StrLiteral("4"), StrLiteral("oranges")); print("Size_8: ", programObject8.size)
    # program9 = name.Substr(4,(2 + 5))
    programObject9 = StrSubstr(_arg_0, IntLiteral(4), IntPlus(IntLiteral(2), IntLiteral(5))); print("Size_9: ", programObject9.size)
    # program10 = concat(concat(concat(name.CharAt(0), "."), name.CharAt((name.IndexOf(" ") + 1))), ".")
    programObject10 = StrConcat(StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrLiteral(".")), StrCharAt(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)))), StrLiteral(".")); print("Size_10: ", programObject10.size)
    # program11 = _arg_0.Substr(0,_arg_0.IndexOf(" ",("ssp.".Length() + "ssp.".Length())))
    programObject11 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntPlus(IntLength(IntLiteral("ssp.")), IntLength(IntLiteral("ssp."))))); print("Size_11: ", programObject11.size)
    # program12 = concat(concat(concat(name.CharAt(0), "."), name.CharAt((name.IndexOf(" ") + 1))), ".")
    programObject12 = StrConcat(StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrLiteral(".")), StrCharAt(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)))), StrLiteral(".")); print("Size_12: ", programObject12.size)
    # program13 = name.Substr(4,(0 - 4))
    programObject13 = StrSubstr(_arg_0, IntLiteral(4), IntMinus(IntLiteral(0), IntLiteral(4))); print("Size_13: ", programObject13.size)
    # program14 = _arg_0.replace(",", "").replace("1", "apple").replace("2", "bananas").replace("3", "strawberries").replace("4", "oranges")
    programObject14 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral(","), StrLiteral("")), StrLiteral("1"), StrLiteral("apple")), StrLiteral("2"), StrLiteral("bananas")), StrLiteral("3"), StrLiteral("strawberries")), StrLiteral("4"), StrLiteral("oranges")); print("Size_14: ", programObject14.size)
    # program15 = name.Substr((3 + 5),name.Length())
    programObject15 = StrSubstr(_arg_0, IntPlus(IntLiteral(3), IntLiteral(5)), IntLength(_arg_0)); print("Size_15: ", programObject15.size)
    # program16 = 
    # concat(
        # concat(
            # concat(
                # concat(
                    # concat( concat(_arg_0, ","), " ").replace(concat(concat(concat(_arg_0, ","), " "), _arg_1), _arg_0), 
                    # _arg_1
                # ), 
            # ","), 
        # " "), 
    # _arg_2)
    programObject16 = \
    StrConcat(
        StrConcat(
            StrConcat(
                StrConcat(
                    StrReplace(
                        StrConcat(StrConcat(_arg_0, StrLiteral(",")), StrLiteral(" ")), 
                        StrConcat(StrConcat(StrConcat(_arg_0, StrLiteral(",")),StrLiteral(" ")),_arg_1),
                        _arg_0
                    ),
                    _arg_1
                ),
                StrLiteral(",")
            ),
            StrLiteral(" ")
        ),
        _arg_2
    ); print("Size_16: ", programObject16.size)
    # program17 = _arg_0.Substr(0,(_arg_0.IndexOf("Inc") + -1))
    programObject17 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("Inc"), IntLiteral(1)), IntLiteral(1))); print("Size_17: ", programObject17.size)
    # program18 = (ifcol2.Contain("USA") then col2 else concat(col2, concat(",", concat(" ", "USA"))))
    programObject18 = StrIte(BoolContain(_arg_0, StrLiteral("USA")), _arg_0, StrConcat(_arg_0, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrLiteral("USA"))))); print("Size_18: ", programObject18.size)
    # program19 = name.Substr(0,3)
    programObject19 = StrSubstr(_arg_0, IntLiteral(0), IntLiteral(3)); print("Size_19: ", programObject19.size)
    # program20 = _arg_0.replace(_arg_0.lower(), _arg_1)
    programObject20 = StrReplace(_arg_0, StrLower(_arg_0), _arg_1); print("Size_20: ", programObject20.size)
    # program21 = _arg_0.Substr(0,_arg_0.IndexOf(" "))
    programObject21 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_21: ", programObject21.size)
    # program22 = concat(concat("Dr.", " "), name.Substr(0,name.IndexOf(" ")))
    programObject22 = StrConcat(StrConcat(StrLiteral("Dr."), StrLiteral(" ")), StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)))); print("Size_22: ", programObject22.size)
    # program23 = _arg_0.replace(_arg_0.Substr(1,_arg_0.IndexOf(" ")), "")
    programObject23 = StrReplace(_arg_0, StrSubstr(_arg_0, IntLiteral(1), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))), StrLiteral("")); print("Size_23: ", programObject23.size)
    # program24 = concat(concat(concat(_arg_0.CharAt(0), _arg_1), "_"), _arg_2)
    programObject24 = StrConcat(StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), _arg_1), StrLiteral("_")), _arg_2); print("Size_24: ", programObject24.size)
    # program25 = _arg_0.Substr(0,(_arg_0.IndexOf("/",(3 * 3)) + (_arg_0.Length() % 2)))
    programObject25 = StrSubstr(_arg_0, IntLiteral(0), IntPlus(IntIndexOf(_arg_0, StrLiteral("/"), IntMultiply(IntLiteral(3), IntLiteral(3))), IntModulo(IntLength(_arg_0), IntLiteral(2)))); print("Size_25: ", programObject25.size)
    # program26 = _arg_0.replace("DRS", "Direct Response").replace("BRD", "Branding").replace("LDS", "Leads")
    programObject26 = StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("DRS"), StrLiteral("Direct Response")), StrLiteral("BRD"), StrLiteral("Branding")), StrLiteral("LDS"), StrLiteral("Leads")); print("Size_26: ", programObject26.size)
    # program27 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),_arg_0.Length())
    programObject27 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLength(_arg_0)); print("Size_27: ", programObject27.size)
    # program28 = _arg_0.replace(_arg_0.Substr(1,_arg_0.IndexOf(" ")), "")
    programObject28 = StrReplace(_arg_0, StrSubstr(_arg_0, IntLiteral(1), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))), StrLiteral("")); print("Size_28: ", programObject28.size)
    # program29 = _arg_0.Substr(0,_arg_0.IndexOf(" "))
    programObject29 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_29: ", programObject29.size)
    # program30 = concat(concat("Dr.", " "), name.Substr(0,name.IndexOf(" ")))
    programObject30 = StrConcat(StrConcat(StrLiteral("Dr."), StrLiteral(" ")), StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)))); print("Size_30: ", programObject30.size)
    # program31 = _arg_0.replace(_arg_0.lower(), _arg_1)
    programObject31 = StrReplace(_arg_0, StrLower(_arg_0), _arg_1); print("Size_31: ", programObject31.size)
    # program32 = _arg_0.Substr(0,(_arg_0.IndexOf("Inc") + -1))
    programObject32 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("Inc"), IntLiteral(1)), IntLiteral(1))); print("Size_32: ", programObject32.size)
    # program33 = name.Substr(0,3)
    programObject33 = StrSubstr(_arg_0, IntLiteral(0), IntLiteral(3)); print("Size_33: ", programObject33.size)
    # program34 = name.Substr((3 + 5),name.Length())
    programObject34 = StrSubstr(_arg_0, IntPlus(IntLiteral(3), IntLiteral(5)), IntLength(_arg_0)); print("Size_34: ", programObject34.size)
    # program35 = concat(_arg_0, concat(",", concat(" ", concat(_arg_1, concat(",", concat(" ", _arg_2)).replace(concat(_arg_1, concat(",", concat(" ", _arg_2))), _arg_2)))))
    programObject35 = StrConcat(_arg_0, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrConcat(_arg_1, StrConcat(StrLiteral(","), StrReplace(StrConcat(_arg_1, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), _arg_2))), StrConcat(_arg_1, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), _arg_2))), _arg_2)))))); print("Size_35: ", programObject35.size)
    # program36 = name.Substr(1,name.Length()).replace(" ", ".").replace("-", ".").replace("-", ".")
    programObject36 = StrReplace(StrReplace(StrReplace(StrSubstr(_arg_0, IntLiteral(1), IntLength(_arg_0)), StrLiteral(" "), StrLiteral(".")), StrLiteral("-"), StrLiteral(".")), StrLiteral("-"), StrLiteral(".")); print("Size_36: ", programObject36.size)
    # program37 = _arg_0.Substr((_arg_0.IndexOf("_") + "2".StrToInt()),_arg_0.Length())
    programObject37 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntLiteral(2)), IntLength(_arg_0)); print("Size_37: ", programObject37.size)
    # program38 = concat(col1, concat(",", concat(" ", concat(col2.replace(concat(",", concat(" ", "USA")), col1.Substr(1,0)), concat(",", concat(" ", "USA"))))))
    programObject38 = StrConcat(StrConcat(StrConcat(StrConcat(_arg_0, StrLiteral(",")), StrLiteral(" ")), StrConcat(_arg_1, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrConcat(_arg_2, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrLiteral("USA")))))))), StrLiteral("USA")); print("Size_38: ", programObject38.size)
    # program39 = _arg_0.Substr(0,_arg_0.IndexOf(" ",("ssp.".Length() + "ssp.".Length())))
    programObject39 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntPlus(IntLength(IntLiteral("ssp.")), IntLength(IntLiteral("ssp."))))); print("Size_39: ", programObject39.size)
    # program40 = _arg_0.Substr(0,_arg_0.IndexOf(" ",("ssp.".Length() + "ssp.".Length())))
    programObject40 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntPlus(IntLength(IntLiteral("ssp.")), IntLength(IntLiteral("ssp."))))); print("Size_40: ", programObject40.size)
    # program41 = _arg_0.Substr((_arg_0.IndexOf("_") + "2".StrToInt()),_arg_0.Length())
    programObject41 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntLiteral(2)), IntLength(_arg_0)); print("Size_41: ", programObject41.size)
    # program42 = concat(col1, concat(concat(",", concat(" ", col2)), (ifcol2.Contain("USA") then col1.Substr(1,0) else concat(",", concat(" ", "USA")))))
    programObject42 = StrConcat(_arg_0, StrConcat(StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), _arg_1)), StrIte(BoolContain(_arg_1, StrLiteral("USA")), StrSubstr(_arg_0, IntLiteral(1), IntLiteral(0)), StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrLiteral("USA")))))); print("Size_42: ", programObject42.size)
    # program43 = name.Substr(1,name.Length()).replace("-", ".").replace(" ", ".").replace("-", ".")
    programObject43 = StrReplace(StrReplace(StrReplace(StrSubstr(_arg_0, IntLiteral(1), IntLength(_arg_0)), StrLiteral("-"), StrLiteral(".")), StrLiteral(" "), StrLiteral(".")), StrLiteral("-"), StrLiteral(".")); print("Size_43: ", programObject43.size)
    # program44 = 
    # concat(
        # concat(
            # concat(
                # concat(
                    # concat( concat(_arg_0, ","), " ").replace(
                        # concat(concat(concat(_arg_0, ","), " "), _arg_1), 
                        # _arg_0), 
                    # _arg_1), 
                # ","), 
            # " "), 
        # _arg_2)
    programObject44 = \
        StrConcat(
            StrConcat(
                StrConcat(
                    StrConcat(
                        StrReplace(
                            StrConcat( StrConcat(_arg_0, StrLiteral(",")), StrLiteral(" ")),
                            StrConcat(StrConcat( StrConcat(_arg_0, StrLiteral(",")), StrLiteral(" ")), _arg_1), 
                            _arg_0
                        ),
                        _arg_1
                    ), 
                    StrLiteral(",")
                ), 
                StrLiteral(" ")
            ), 
        _arg_2
    ); print("Size_44: ", programObject44.size)
    # program45 = name.Substr((3 + 5),name.Length())
    programObject45 = StrSubstr(_arg_0, IntPlus(IntLiteral(3), IntLiteral(5)), IntLength(_arg_0)); print("Size_45: ", programObject45.size)
    # program46 = col2.replace(col2.replace("USA", col2), concat(concat(concat(col2, ","), " "), "USA"))
    programObject46 = StrReplace(_arg_0, StrReplace(_arg_0, StrLiteral("USA"), _arg_0), StrConcat(StrConcat(_arg_0, StrLiteral(",")), StrConcat(StrLiteral(" "), StrLiteral("USA")))); print("Size_46: ", programObject46.size)
    # program47 = concat(concat("Dr.", " "), name.Substr(0,name.IndexOf(" ")))
    programObject47 = StrConcat(StrConcat(StrLiteral("Dr."), StrLiteral(" ")), StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)))); print("Size_47: ", programObject47.size)
    # program48 = _arg_0.Substr(0,_arg_0.IndexOf(" "))
    programObject48 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_48: ", programObject48.size)
    # program49 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),_arg_0.Length())
    programObject49 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLength(_arg_0)); print("Size_49: ", programObject49.size)
    # program50 = _arg_0.replace("DRS", "Direct Response").replace("BRD", "Branding").replace("LDS", "Leads")
    programObject50 = StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("DRS"), StrLiteral("Direct Response")), StrLiteral("BRD"), StrLiteral("Branding")), StrLiteral("LDS"), StrLiteral("Leads")); print("Size_50: ", programObject50.size)
    # program51 = _arg_0.replace("DRS", "Direct Response").replace("BRD", "Branding").replace("LDS", "Leads")
    programObject51 = StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("DRS"), StrLiteral("Direct Response")), StrLiteral("BRD"), StrLiteral("Branding")), StrLiteral("LDS"), StrLiteral("Leads")); print("Size_51: ", programObject51.size)
    # program52 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),_arg_0.Length())
    programObject52 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLength(_arg_0)); print("Size_52: ", programObject52.size)
    # program53 = concat(concat(concat(_arg_0.CharAt(0), _arg_1), "_"), _arg_2)
    programObject53 = StrConcat(StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), _arg_1), StrLiteral("_")), _arg_2); print("Size_53: ", programObject53.size)
    # program54 = _arg_0.Substr(0,((_arg_0.Length() % 2) + _arg_0.IndexOf("/",(3 * 3))))
    programObject54 = StrSubstr(_arg_0, IntLiteral(0), IntPlus(IntModulo(IntLength(_arg_0), IntLiteral(2)), IntIndexOf(_arg_0, StrLiteral("/"), IntMultiply(IntLiteral(3), IntLiteral(3))))); print("Size_54: ", programObject54.size)
    # program55 = _arg_0.replace(_arg_0.Substr(1,_arg_0.IndexOf(" ")), "")
    programObject55 = StrReplace(_arg_0, StrSubstr(_arg_0, IntLiteral(1), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))), StrLiteral("")); print("Size_55: ", programObject55.size)
    # program56 = _arg_0.replace(_arg_0.lower(), _arg_1)
    programObject56 = StrReplace(_arg_0, StrLower(_arg_0), _arg_1); print("Size_56: ", programObject56.size)
    # program57 = _arg_0.Substr(0,(_arg_0.IndexOf("Inc") + -1))
    programObject57 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("Inc"), IntLiteral(1)), IntLiteral(1))); print("Size_57: ", programObject57.size)
    # program58 = (ifcol2.Contain("USA") then col2 else concat(col2, concat(",", concat(" ", "USA"))))
    programObject58 = StrIte(BoolContain(_arg_0, StrLiteral("USA")), _arg_0, StrConcat(_arg_0, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrLiteral("USA"))))); print("Size_58: ", programObject58.size)
    # program59 = name.Substr(0,3)
    programObject59 = StrSubstr(_arg_0, IntLiteral(0), IntLiteral(3)); print("Size_59: ", programObject59.size)
    # program60 = _arg_0.replace(",", "").replace("1", "apple").replace("2", "bananas").replace("3", "strawberries").replace("4", "oranges")
    programObject60 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral(","), StrLiteral("")), StrLiteral("1"), StrLiteral("apple")), StrLiteral("2"), StrLiteral("bananas")), StrLiteral("3"), StrLiteral("strawberries")), StrLiteral("4"), StrLiteral("oranges")); print("Size_60: ", programObject60.size)
    # program61 = concat(concat(name.CharAt(0), "."), concat(name.CharAt((name.IndexOf(" ") + 1)), "."))
    programObject61 = StrConcat(StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrLiteral(".")), StrCharAt(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)))), StrLiteral(".")); print("Size_61: ", programObject61.size)
    # program62 = name.Substr(4,(2 + 5))
    programObject62 = StrSubstr(_arg_0, IntLiteral(4), IntPlus(IntLiteral(2), IntLiteral(5))); print("Size_62: ", programObject62.size)
    # program63 = name.Substr(1,name.Length()).replace(" ", ".").replace("-", ".").replace("-", ".")
    programObject63 = StrReplace(StrReplace(StrReplace(StrSubstr(_arg_0, IntLiteral(1), IntLength(_arg_0)), StrLiteral(" "), StrLiteral(".")), StrLiteral("-"), StrLiteral(".")), StrLiteral("-"), StrLiteral(".")); print("Size_63: ", programObject63.size)
    # program64 = _arg_0.Substr((_arg_0.IndexOf("_") + "2".StrToInt()),_arg_0.Length())
    programObject64 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntLiteral(2)), IntLength(_arg_0)); print("Size_64: ", programObject64.size)
    # program65 = concat(col1, concat(",", concat(" ", concat(col2, (ifcol2.Contain("USA") then col1.Substr(1,0) else concat(",", concat(" ", "USA")))))))
    programObject65 = \
        StrConcat(
            _arg_0, 
            StrConcat(
                StrLiteral(","), 
                StrConcat(
                    StrLiteral(" "), 
                    StrConcat(
                        _arg_1, 
                        StrIte(
                            BoolContain(_arg_1, StrLiteral("USA")), 
                            StrSubstr(_arg_0, IntLiteral(1), IntLiteral(0)), 
                            StrConcat(
                                StrLiteral(","), 
                                StrConcat(
                                    StrLiteral(" "), 
                                    StrLiteral("USA")
                                )
                            )
                        )
                    )
                )
            )
        ); print("Size_65: ", programObject65.size)
    # program66 = name.Substr(4,(2 + 5))
    programObject66 = StrSubstr(_arg_0, IntLiteral(4), IntPlus(IntLiteral(2), IntLiteral(5))); print("Size_66: ", programObject66.size)
    # program67 = concat(name.CharAt(0), concat(concat(".", name.CharAt((name.IndexOf(" ") + 1))), "."))
    programObject67 = StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrConcat(StrConcat(StrLiteral("."), StrCharAt(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)))), StrLiteral("."))); print("Size_67: ", programObject67.size)
    # program68 = _arg_0.replace(",", "").replace("1", "apple").replace("2", "bananas").replace("3", "strawberries").replace("4", "oranges")
    programObject68 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral(","), StrLiteral("")), StrLiteral("1"), StrLiteral("apple")), StrLiteral("2"), StrLiteral("bananas")), StrLiteral("3"), StrLiteral("strawberries")), StrLiteral("4"), StrLiteral("oranges")); print("Size_68: ", programObject68.size)
    # program69 = name.Substr(0,3)
    programObject69 = StrSubstr(_arg_0, IntLiteral(0), IntLiteral(3)); print("Size_69: ", programObject69.size)
    # program70 = _arg_0.Substr(0,(_arg_0.IndexOf("Inc") + -1))
    programObject70 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("Inc"), IntLiteral(1)), IntLiteral(1))); print("Size_70: ", programObject70.size)
    # program71 = (ifcol2.Contain("USA") then col2 else concat(concat(concat(col2, ","), " "), "USA"))
    programObject71 = StrIte(BoolContain(_arg_0, StrLiteral("USA")), _arg_0, StrConcat(StrConcat(_arg_0, StrLiteral(",")), StrConcat(StrLiteral(" "), StrLiteral("USA")))); print("Size_71: ", programObject71.size)
    # program72 = _arg_0.replace(_arg_0.lower(), _arg_1)
    programObject72 = StrReplace(_arg_0, StrLower(_arg_0), _arg_1); print("Size_72: ", programObject72.size)
    # program73 = _arg_0.replace(_arg_0.Substr(1,_arg_0.IndexOf(" ")), "")
    programObject73 = StrReplace(_arg_0, StrSubstr(_arg_0, IntLiteral(1), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))), StrLiteral("")); print("Size_73: ", programObject73.size)
    # program74 = _arg_0.Substr(0,(_arg_0.IndexOf("/",(3 * 3)) + (_arg_0.Length() % 2)))
    programObject74 = StrSubstr(_arg_0, IntLiteral(0), IntPlus(IntIndexOf(_arg_0, StrLiteral("/"), IntMultiply(IntLiteral(3), IntLiteral(3))), IntModulo(IntLength(_arg_0), IntLiteral(2)))); print("Size_74: ", programObject74.size)
    # program75 = concat(concat(_arg_0.CharAt(0), concat(_arg_1, "_")), _arg_2)
    programObject75 = StrConcat(StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), _arg_1), StrLiteral("_")), _arg_2); print("Size_75: ", programObject75.size)
    # program76 = _arg_0.replace("BRD", "Branding").replace("DRS", "Direct Response").replace("LDS", "Leads")
    programObject76 = StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("BRD"), StrLiteral("Branding")), StrLiteral("DRS"), StrLiteral("Direct Response")), StrLiteral("LDS"), StrLiteral("Leads")); print("Size_76: ", programObject76.size)
    # program77 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),_arg_0.Length())
    programObject77 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLength(_arg_0)); print("Size_77: ", programObject77.size)
    # program78 = concat(concat("Dr.", " "), name.Substr(0,name.IndexOf(" ")))
    programObject78 = StrConcat(StrConcat(StrLiteral("Dr."), StrLiteral(" ")), StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)))); print("Size_78: ", programObject78.size)
    # program79 = _arg_0.Substr(0,_arg_0.IndexOf(" "))
    programObject79 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_79: ", programObject79.size)
    # program80 = concat(concat(concat(concat(concat(concat(_arg_0, ","), " ").replace(concat(concat(concat(_arg_0, ","), " "), _arg_1), _arg_0), _arg_1), ","), " "), _arg_2)
    programObject80 = \
        StrConcat(
            StrConcat(
                StrConcat(
                    StrConcat(
                        StrConcat(
                            StrConcat(
                                _arg_0,
                                StrLiteral(",")
                            ),
                            StrLiteral(" ")
                        ),
                        StrReplace(
                            StrConcat(
                                StrConcat(
                                    StrConcat(
                                        _arg_0,
                                        StrLiteral(",")
                                    ),
                                    StrLiteral(" ")
                                ),
                                _arg_1
                            ),
                            StrConcat(
                                StrConcat(
                                    StrConcat(
                                        _arg_0,
                                        StrLiteral(",")
                                    ),
                                    StrLiteral(" ")
                                ),
                                _arg_1
                            ),
                            _arg_0
                        )
                    ),
                    _arg_1
                ),
                StrLiteral(",")
            ),
            StrConcat(
                StrLiteral(" "),
                _arg_2
            )
        ); print("Size_80: ", programObject80.size)
        
    # program81 = name.Substr((3 + 5),name.Length())
    programObject81 = StrSubstr(_arg_0, IntPlus(IntLiteral(3), IntLiteral(5)), IntLength(_arg_0)); print("Size_81: ", programObject81.size)
    # program82 = _arg_0.replace(",", "").replace("1", "apple").replace("2", "bananas").replace("3", "strawberries").replace("4", "oranges")
    programObject82 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral(","), StrLiteral("")), StrLiteral("1"), StrLiteral("apple")), StrLiteral("2"), StrLiteral("bananas")), StrLiteral("3"), StrLiteral("strawberries")), StrLiteral("4"), StrLiteral("oranges")); print("Size_82: ", programObject82.size)
    # program83 = _arg_0.Substr(("2".StrToInt() + _arg_0.IndexOf("_")),_arg_0.Length())
    programObject83 = StrSubstr(_arg_0, IntPlus(IntLiteral(2), IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1))), IntLength(_arg_0)); print("Size_83: ", programObject83.size)
    # program84 = concat(col1, concat(",", concat(" ", concat(col2.replace(concat(",", concat(" ", "USA")), col1.Substr(1,0)), concat(",", concat(" ", "USA"))))))
    programObject84 = StrConcat(_arg_0, StrConcat(StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), _arg_1)), StrConcat(_arg_2, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrLiteral("USA")))))) ; print("Size_84: ", programObject84.size)
    # program85 = name.Substr(1,name.Length()).replace("-", ".").replace(" ", ".").replace("-", ".")
    programObject85 = StrReplace(StrReplace(StrReplace(StrSubstr(_arg_0, IntLiteral(1), IntLength(_arg_0)), StrLiteral("-"), StrLiteral(".")), StrLiteral(" "), StrLiteral(".")), StrLiteral("-"), StrLiteral(".")); print("Size_85: ", programObject85.size)
    # program86 = _arg_0.Substr(0,_arg_0.IndexOf(" ",("ssp.".Length() + "ssp.".Length())))
    programObject86 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntPlus(IntLength(IntLiteral("ssp.")), IntLength(IntLiteral("ssp."))))); print("Size_86: ", programObject86.size)
    # program87 = _arg_0.Substr(0,_arg_0.IndexOf(" ",("ssp.".Length() + "ssp.".Length())))
    programObject87 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntPlus(IntLength(IntLiteral("ssp.")), IntLength(IntLiteral("ssp."))))); print("Size_87: ", programObject87.size)
    # program88 = name.Substr(1,name.Length()).replace("-", ".").replace("-", ".").replace(" ", ".")
    programObject88 = StrReplace(StrReplace(StrReplace(StrSubstr(_arg_0, IntLiteral(1), IntLength(_arg_0)), StrLiteral("-"), StrLiteral(".")), StrLiteral("-"), StrLiteral(".")), StrLiteral(" "), StrLiteral(".")); print("Size_88: ", programObject88.size)
    # program89 = _arg_0.Substr((_arg_0.IndexOf("_") + "2".StrToInt()),_arg_0.Length())
    programObject89 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntLiteral(2)), IntLength(_arg_0)); print("Size_89: ", programObject89.size)
    # program90 = concat(col1, concat(",", concat(" ", concat(col2, (ifcol2.Contain("USA") then col1.Substr(1,0) else concat(",", concat(" ", "USA")))))))
    programObject90 = StrConcat(_arg_0, StrConcat(StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), _arg_1)), StrIte(BoolContain(_arg_1, StrLiteral("USA")), StrSubstr(_arg_0, IntLiteral(1), IntLiteral(0)), StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrLiteral("USA")))))) ; print("Size_90: ", programObject90.size)
    # program91 = concat(concat(name.CharAt(0), concat(".", name.CharAt((name.IndexOf(" ") + 1)))), ".")
    programObject91 = \
        StrConcat(
            StrConcat(
                StrCharAt(_arg_0, IntLiteral(0)), 
                StrConcat(
                    StrLiteral("."), 
                    StrCharAt(
                        _arg_0, 
                        IntPlus(
                            IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), 
                            IntLiteral(1)
                        )
                    )
                )
            ), 
            StrLiteral(".")
        ); print("Size_91: ", programObject91.size)
    # program92 = name.Substr(4,(2 + 5))
    programObject92 = StrSubstr(_arg_0, IntLiteral(4), IntPlus(IntLiteral(2), IntLiteral(5))); print("Size_92: ", programObject92.size)
    # program93 = name.Substr((0 - 3),name.Length())
    programObject93 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntLength(_arg_0), IntLiteral(3))); print("Size_93: ", programObject93.size)
    # program94 = 
    # concat(
        # concat(concat(concat(_arg_0, ","), " "), _arg_1), 
        # concat(",", concat(" ", _arg_2)).replace(
            # concat(_arg_1, concat(",", concat(" ", _arg_2))),
            # _arg_2)
        # )
    programObject94 = \
        StrConcat(
            StrConcat(
                StrConcat(
                    StrConcat(
                        _arg_0, 
                        StrLiteral(",")
                    ), 
                    StrLiteral(" ")
                ), 
                _arg_1
            ), 
            StrReplace(
                StrConcat(
                    _arg_1, 
                    StrConcat(
                        StrLiteral(","), 
                        StrConcat(
                            StrLiteral(" "), 
                            _arg_2
                        )
                    )
                ), 
                StrConcat(
                    _arg_1, 
                    StrConcat(
                        StrLiteral(","), 
                        StrConcat(
                            StrLiteral(" "), 
                            _arg_2
                        )
                    )
                ), 
                _arg_2
            )
        ); print("Size_94: ", programObject94.size)
    # program95 = _arg_0.Substr(0,_arg_0.IndexOf(" "))
    programObject95 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_95: ", programObject95.size)
    # program96 = concat(concat("Dr.", " "), name.Substr(0,name.IndexOf(" ")))
    programObject96 = StrConcat(StrConcat(StrLiteral("Dr."), StrLiteral(" ")), StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)))); print("Size_96: ", programObject96.size)
    # program97 = concat(concat(concat(_arg_0.CharAt(0), _arg_1), "_"), _arg_2)
    programObject97 = StrConcat(StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), _arg_1), StrLiteral("_")), _arg_2); print("Size_97: ", programObject97.size)
    # program98 = _arg_0.Substr(0,(_arg_0.IndexOf("/",(3 * 3)) + (_arg_0.Length() % 2)))
    programObject98 = StrSubstr(_arg_0, IntLiteral(0), IntPlus(IntIndexOf(_arg_0, StrLiteral("/"), IntMultiply(IntLiteral(3), IntLiteral(3))), IntModulo(IntLength(_arg_0), IntLiteral(2)))) ; print("Size_98: ", programObject98.size)
    # program99 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),_arg_0.Length())
    programObject99 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLength(_arg_0)); print("Size_99: ", programObject99.size)
    # program100 = _arg_0.replace("DRS", "Direct Response").replace("BRD", "Branding").replace("LDS", "Leads")
    programObject100 = StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("DRS"), StrLiteral("Direct Response")), StrLiteral("BRD"), StrLiteral("Branding")), StrLiteral("LDS"), StrLiteral("Leads")); print("Size_100: ", programObject100.size)
    # program101 = name.Substr((0 - 3),name.Length())
    programObject101 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntLength(_arg_0), IntLiteral(3))); print("Size_101: ", programObject101.size)
    # program102 = (if_arg_0.Contain(_arg_0.Substr((_arg_0.IndexOf(" ") + 3),_arg_0.Length()).replace(" ", "").Substr(0,4)) then _arg_0.Substr((_arg_0.IndexOf(" ") + 3),_arg_0.Length()).replace(" ", "").Substr(0,4) else _arg_0).Substr((1 - 5),_arg_0.Length())
    programObject102 = StrSubstr(StrIte(BoolContain(_arg_0, StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(3)), IntLength(_arg_0))), StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(3)), IntLength(_arg_0)), _arg_0), IntMinus(IntLiteral(1), IntLiteral(5)), IntLength(_arg_0)); print("Size_102: ", programObject102.size)
    # program103 = concat(concat(concat(col1, ","), " "), col2)
    programObject103 = StrConcat(StrConcat(StrConcat(_arg_0, StrLiteral(",")), StrLiteral(" ")), _arg_1); print("Size_103: ", programObject103.size)
    # program104 = concat(lastname, concat(" ", firstname))
    programObject104 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), _arg_1)); print("Size_104: ", programObject104.size)
    # program105 = name.Substr((name.IndexOf("-") + 1),(0 - 4))
    programObject105 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1)), IntLiteral(1)), IntMinus(IntLiteral(0), IntLiteral(4))); print("Size_105: ", programObject105.size)
    # program106 = concat("(", name.replace("-", concat(")", " ")))
    programObject106 = StrConcat(StrLiteral("("), StrReplace(_arg_0, StrLiteral("-"), StrConcat(StrLiteral(")"), StrLiteral(" ")))); print("Size_106: ", programObject106.size)
    # program107 = concat(concat(_arg_0, " "), _arg_1)
    programObject107 = StrConcat(StrConcat(_arg_0, StrLiteral(" ")), _arg_1); print("Size_107: ", programObject107.size)
    # program108 = name.Substr(0,name.IndexOf(" "))
    programObject108 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_108: ", programObject108.size)
    # program109 = _arg_0.replace(".", "").replace(".", "").replace("-", "").replace("<", "").replace(" ", "").replace(">", "").replace("-", "")
    # programObject109 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("."), StrLiteral("")), StrLiteral("."), StrLiteral("")), StrLiteral("-"), StrLiteral("")), StrLiteral("<"), StrLiteral("")), StrLiteral(" "), StrLiteral("")), StrLiteral(">"), StrLiteral("")), StrLiteral("-"), StrLiteral(""))); print("Size_109: ", programObject109.size)
    programObject109 = \
            StrReplace(
                StrReplace(
                    StrReplace(
                        StrReplace(
                            StrReplace(
                                StrReplace(
                                    StrReplace(
                                        _arg_0, 
                                        StrLiteral("."), 
                                        StrLiteral("")
                                    ), 
                                    StrLiteral("."), 
                                    StrLiteral("")
                                ), 
                                StrLiteral("-"), 
                                StrLiteral("")
                            ), 
                            StrLiteral("<"), 
                            StrLiteral("")
                        ), 
                        StrLiteral(" "), 
                        StrLiteral("")
                    ), 
                    StrLiteral(">"), 
                    StrLiteral("")
                ), 
                StrLiteral("-"), 
                StrLiteral("")
            ); print("Size_109: ", programObject109.size)
    
    # program110 = (if_arg_0.Contain("microsoft") then (if_arg_0.Contain("windows") then "windows" else "microsoft") else "mac")
    programObject110 = StrIte(BoolContain(_arg_0, StrLiteral("microsoft")), StrIte(BoolContain(_arg_0, StrLiteral("windows")), StrLiteral("windows"), StrLiteral("microsoft")), StrLiteral("mac")); print("Size_110: ", programObject110.size)
    # program111 = _arg_0.Substr(0,(((_arg_0.replace("|", _arg_0).IndexOf(_arg_0) + -1) % _arg_0.Length()) + 1))
    programObject111 = StrSubstr(_arg_0, IntLiteral(0), IntPlus(IntModulo(IntMinus(IntIndexOf(_arg_0, StrLiteral("|"), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)), IntLiteral(1))); print("Size_111: ", programObject111.size)
    # program112 = _arg_0.Substr((-1 - (_arg_0.IndexOf("/") + 1)),_arg_0.Length()).replace("/", "")
    # programObject112 = StrReplace(StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntPlus(IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(1)), IntLiteral(1)))), StrLiteral("/"), StrLiteral("")); print("Size_112: ", programObject112.size)
    programObject112 = \
    StrReplace(
        StrSubstr(
            _arg_0, 
            IntMinus(
                IntLiteral(-1),
                IntPlus(
                    IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(0)), 
                    IntLiteral(1)
                ),
            ), 
            IntLength(_arg_0)
        ), 
        StrLiteral("/"), 
        StrLiteral("")
    ); print("Size_112: ", programObject112.size)

    # program113 = _arg_0.replace(_arg_1.upper(), "").replace(concat(1.IntToStr(), " "), 1.IntToStr())
    programObject113 = StrReplace(StrReplace(_arg_0, StrUpper(_arg_1), StrLiteral("")), StrConcat(StrIntToStr(IntLiteral(1)), StrLiteral(" ")), StrIntToStr(IntLiteral(1))); print("Size_113: ", programObject113.size)
    # program114 = _arg_0.Substr(0,(_arg_0.IndexOf("-") + -1))
    programObject114 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1)), IntLiteral(1))); print("Size_114: ", programObject114.size)
    # program115 = _arg_0.replace(" ", "-").replace(" ", "-")
    programObject115 = StrReplace(StrReplace(_arg_0, StrLiteral(" "), StrLiteral("-")), StrLiteral(" "), StrLiteral("-")); print("Size_115: ", programObject115.size)
    # program116 = _arg_0.Substr(0,(_arg_0.IndexOf("-") + -1))
    programObject116 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1)), IntLiteral(1))); print("Size_116: ", programObject116.size)
    # program117 = _arg_0.replace(" ", "-").replace(" ", "-")
    programObject117 = StrReplace(StrReplace(_arg_0, StrLiteral(" "), StrLiteral("-")), StrLiteral(" "), StrLiteral("-")); print("Size_117: ", programObject117.size)
    # program118 = _arg_0.replace(_arg_1.upper(), "").replace(concat(1.IntToStr(), " "), 1.IntToStr())
    programObject118 = StrReplace(StrReplace(_arg_0, StrUpper(_arg_1), StrLiteral("")), StrConcat(StrIntToStr(IntLiteral(1)), StrLiteral(" ")), StrIntToStr(IntLiteral(1))); print("Size_118: ", programObject118.size)
    # program119 = _arg_0.Substr((-1 - (_arg_0.IndexOf("/") + 1)),_arg_0.Length()).replace("/", "")
    programObject119 =\
    StrReplace(
        StrSubstr(
            _arg_0, 
            IntMinus(
                IntLiteral(-1),
                IntPlus(
                    IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(0)), 
                    IntLiteral(1)
                ),
            ), 
            IntLength(_arg_0)
        ), 
        StrLiteral("/"), 
        StrLiteral("")
    );  print("Size_119: ", programObject119.size)
    # program120 = _arg_0.replace(".", "").replace(".", "").replace(" ", "").replace("-", "").replace("-", "").replace(">", "").replace("<", "")
    programObject120 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("."), StrLiteral("")), StrLiteral("."), StrLiteral("")), StrLiteral(" "), StrLiteral("")), StrLiteral("-"), StrLiteral("")), StrLiteral("-"), StrLiteral("")), StrLiteral(">"), StrLiteral("")), StrLiteral("<"), StrLiteral("")); print("Size_120: ", programObject120.size)
    # program121 = name.Substr(0,name.IndexOf(" "))
    programObject121 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_121: ", programObject121.size)
    # program122 = concat(concat(_arg_0, " "), _arg_1)
    programObject122 = StrConcat(StrConcat(_arg_0, StrLiteral(" ")), _arg_1); print("Size_122: ", programObject122.size)
    # program123 = concat("(", name.replace("-", concat(")", " ")))
    programObject123 = StrConcat(StrLiteral("("), StrReplace(_arg_0, StrLiteral("-"), StrConcat(StrLiteral(")"), StrLiteral(" ")))); print("Size_123: ", programObject123.size)
    # program124 = (ifEqual(_arg_0,_arg_0.replace(_arg_0.Substr(0,_arg_0.IndexOf(" ")).upper(), "")) then concat(" ", _arg_0.replace(_arg_0.Substr(0,_arg_0.IndexOf(" ")).upper(), "").Substr(0,9)) else _arg_0.replace(_arg_0.Substr(0,_arg_0.IndexOf(" ")).upper(), ""))
    # programObject124 = StrIte(BoolEqual(_arg_0, StrReplace(_arg_0, StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))), StrLiteral(""))), StrConcat(StrLiteral(" "), StrSubstr(StrReplace(_arg_0, StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))), StrLiteral("")), IntLiteral(0), IntLiteral(9))), StrReplace(_arg_0, StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))), StrLiteral("")))); print("Size_124: ", programObject124.size)
    programObject124 = \
    StrIte(
        BoolEqual(
            _arg_0, 
            StrReplace(
                _arg_0, 
                StrUpper(
                    StrSubstr(
                        _arg_0, 
                        IntLiteral(0), 
                        IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(0))
                    )
                ), 
                StrLiteral("")
            )
        ), 
        StrConcat(
            StrLiteral(" "), 
            StrSubstr(
                StrReplace(
                    _arg_0, 
                    StrUpper(
                        StrSubstr(
                            _arg_0, 
                            IntLiteral(0), 
                            IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(0))
                        )
                    ), 
                    StrLiteral("")
                ), 
                IntLiteral(0), 
                IntLiteral(9)
            )
        ), 
        StrReplace(
            _arg_0, 
            StrUpper(
                StrSubstr(
                    _arg_0, 
                    IntLiteral(0), 
                    IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(0))
                )
            ), 
            StrLiteral("")
        )
    ); print("Size_124: ", programObject124.size)

    # program125 = (if_arg_0.Contain(_arg_0.Substr((_arg_0.IndexOf(" ") + 3),_arg_0.Length()).replace(" ", "").Substr(0,4)) then _arg_0.Substr((_arg_0.IndexOf(" ") + 3),_arg_0.Length()).replace(" ", "").Substr(0,4) else _arg_0).Substr((1 - 5),_arg_0.Length())
    programObject125 = StrSubstr(StrIte(BoolContain(_arg_0, StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(0)), IntLiteral(3)), IntLength(_arg_0))), StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(0)), IntLiteral(3)), IntLength(_arg_0)), _arg_0), IntMinus(IntLiteral(1), IntLiteral(5)), IntLength(_arg_0)); print("Size_125: ", programObject125.size)
    # program126 = concat(concat(concat(col1, ","), " "), col2)
    programObject126 = StrConcat(StrConcat(StrConcat(_arg_0, StrLiteral(",")), StrLiteral(" ")), _arg_1); print("Size_126: ", programObject126.size)
    # program127 = name.Substr((0 - 3),name.Length())
    programObject127 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntLength(_arg_0), IntLiteral(3))); print("Size_127: ", programObject127.size)
    # program128 = name.replace("-", ".").replace("-", ".")
    programObject128 = StrReplace(StrReplace(_arg_0, StrLiteral("-"), StrLiteral(".")), StrLiteral("-"), StrLiteral(".")); print("Size_128: ", programObject128.size)
    # program129 = name.Substr((name.IndexOf(" ") + 1),name.Length())
    programObject129 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)); print("Size_129: ", programObject129.size)
    # program130 = name.Substr((name.IndexOf("-") + 1),(0 - 4))
    programObject130 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1)), IntLiteral(1)), IntMinus(IntLiteral(0), IntLiteral(4))); print("Size_130: ", programObject130.size)
    # program131 = concat(lastname, concat(" ", firstname))
    programObject131 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), _arg_1)); print("Size_131: ", programObject131.size)
    # program132 = concat(concat(" ", _arg_0), " ").Substr(concat(_arg_0.CharAt(8), _arg_0).IndexOf(" "),-1).replace(concat(" ", _arg_0), concat(concat(concat(" ", _arg_0), " ").Substr(concat(_arg_0.CharAt(8), _arg_0).IndexOf(" "),-1).Substr(0,9), " "))
    programObject132 = \
    StrReplace(
        StrSubstr(
            StrConcat(
                StrConcat(
                    StrLiteral(" "),
                    _arg_0
                ),
                StrLiteral(" ")
            ),
            IntIndexOf(
                StrConcat(
                    StrConcat(
                        StrLiteral(" "),
                        _arg_0
                    ),
                    StrLiteral(" ")
                ),
                StrConcat(
                    StrCharAt(
                        _arg_0,
                        IntLiteral(8)
                    ),
                    _arg_0
                ),
                IntLiteral(0)
            ),
            IntLiteral(-1)
        ),
        StrConcat(
            StrConcat(
                StrConcat(
                    StrLiteral(" "),
                    _arg_0
                ),
                StrLiteral(" ")
            ),
            StrSubstr(
                StrSubstr(
                    StrConcat(
                        StrConcat(
                            StrConcat(
                                StrLiteral(" "),
                                _arg_0
                            ),
                            StrLiteral(" ")
                        ),
                        StrConcat(
                            StrCharAt(
                                _arg_0,
                                IntLiteral(8)
                            ),
                            _arg_0
                        )
                    ),
                    IntIndexOf(
                        StrConcat(
                            StrConcat(
                                StrConcat(
                                    StrLiteral(" "),
                                    _arg_0
                                ),
                                StrLiteral(" ")
                            ),
                            StrConcat(
                                StrCharAt(
                                    _arg_0,
                                    IntLiteral(8)
                                ),
                                _arg_0
                            )
                        ),
                        StrLiteral(" "),
                        IntLiteral(0)
                    ),
                    IntLiteral(-1)
                ),
                IntLiteral(0),
                IntLiteral(9)
            )
        ),
        StrConcat(
            StrConcat(
                StrConcat(
                    StrLiteral(" "),
                    _arg_0
                ),
                StrLiteral(" ")
            ),
            StrLiteral(" ")
        )
    ); print("Size_132: ", programObject132.size)
    # program133 = (if_arg_0.Contain("windows") then "windows" else (if"/".SuffixOf(_arg_0) then "microsoft" else "mac"))
    programObject133 = StrIte(BoolContain(_arg_0, StrLiteral("windows")), StrLiteral("windows"), StrIte(BoolSuffixof(StrLiteral("/"), _arg_0), StrLiteral("microsoft"), StrLiteral("mac"))); print("Size_133: ", programObject133.size)
    # program134 = _arg_0.Substr((-1 - (_arg_0.Length() % (_arg_0.IndexOf("=") + -1))),_arg_0.Length())
    programObject134 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntModulo(IntLength(_arg_0), IntPlus(IntIndexOf(_arg_0, StrLiteral("="), IntLiteral(1)), IntLiteral(-1)))) , IntLength(_arg_0)); print("Size_134: ", programObject134.size)
    # program135 = _arg_0.replace(_arg_1.lower(), "").replace(_arg_1.lower(), "")
    programObject135 = StrReplace(StrReplace(_arg_0, StrLower(_arg_1), StrLiteral("")), StrLower(_arg_1), StrLiteral("")); print("Size_135: ", programObject135.size)
    # program136 = (if_arg_0.Contain(" ") then _arg_0.Substr(0,_arg_0.replace("|", _arg_0).IndexOf(_arg_0)) else _arg_0)
    programObject136 = StrIte(BoolContain(_arg_0, StrLiteral(" ")), StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrReplace(_arg_0, StrLiteral("|"), _arg_0), IntLiteral(1))), _arg_0); print("Size_136: ", programObject136.size)
    # program137 = _arg_1.Substr(0,_arg_1.IndexOf("_"))
    programObject137 = StrSubstr(_arg_1, IntLiteral(0), IntIndexOf(_arg_1, StrLiteral("_"), IntLiteral(1))); print("Size_137: ", programObject137.size)
    # program138 = concat(concat(_arg_1.CharAt(0), _arg_0), "_acme.com")
    programObject138 = StrConcat(StrConcat(StrCharAt(_arg_1, IntLiteral(0)), _arg_0), StrLiteral("_acme.com")); print("Size_138: ", programObject138.size)
    # program139 = _arg_0.replace(" ", "-").replace(" ", "-")
    programObject139 = StrReplace(StrReplace(_arg_0, StrLiteral(" "), StrLiteral("-")), StrLiteral(" "), StrLiteral("-")); print("Size_139: ", programObject139.size)
    # program140 = _arg_0.replace(_arg_1.upper(), "").replace(concat(1.IntToStr(), " "), 1.IntToStr())
    programObject140 = StrReplace(StrReplace(_arg_0, StrUpper(_arg_1), StrLiteral("")), StrConcat(StrIntToStr(IntLiteral(1)), StrLiteral(" ")), StrIntToStr(IntLiteral(1))); print("Size_140: ", programObject140.size)
    # program141 = concat(concat(_arg_1.CharAt(0), _arg_0), "_acme.com")
    programObject141 = StrConcat(StrConcat(StrCharAt(_arg_1, IntLiteral(0)), _arg_0), StrLiteral("_acme.com")); print("Size_141: ", programObject141.size)
    # program142 = _arg_1.Substr(0,_arg_1.IndexOf("_"))
    programObject142 = StrSubstr(_arg_1, IntLiteral(0), IntIndexOf(_arg_1, StrLiteral("_"), IntLiteral(1))); print("Size_142: ", programObject142.size)
    # program143 = _arg_0.replace(_arg_1.lower(), "").replace(_arg_1.upper(), "")
    programObject143 = StrReplace(StrReplace(_arg_0, StrLower(_arg_1), StrLiteral("")), StrUpper(_arg_1), StrLiteral("")); print("Size_143: ", programObject143.size)
    # program144 = (if_arg_0.Contain(" ") then _arg_0.Substr(0,_arg_0.replace("|", _arg_0).IndexOf(_arg_0)) else _arg_0)
    programObject144 = StrIte(BoolContain(_arg_0, StrLiteral(" ")), StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrReplace(_arg_0, StrLiteral("|"), _arg_0), IntLiteral(1))), _arg_0); print("Size_144: ", programObject144.size)
    # program145 = _arg_0.Substr((-1 - (_arg_0.Length() % (_arg_0.IndexOf("=") + -1))),_arg_0.Length())
    programObject145 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntModulo(IntLength(_arg_0), IntPlus(IntIndexOf(_arg_0, StrLiteral("="), IntLiteral(1)), IntLiteral(-1)))) , IntLength(_arg_0)); print("Size_145: ", programObject145.size)
    # program146 = (if_arg_0.Contain("microsoft") then (if_arg_0.Contain("windows") then "windows" else "microsoft") else "mac")
    programObject146 = StrIte(BoolContain(_arg_0, StrLiteral("microsoft")), StrIte(BoolContain(_arg_0, StrLiteral("windows")), StrLiteral("windows"), StrLiteral("microsoft")), StrLiteral("mac")); print("Size_146: ", programObject146.size)
    # program147 = name.Substr(0,name.IndexOf(" "))
    programObject147 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_147: ", programObject147.size)
    # program148 = _arg_0.replace(".", "").replace(".", "").replace("-", "").replace("<", "").replace(">", "").replace(" ", "").replace("-", "")
    programObject148 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("."), StrLiteral("")), StrLiteral("."), StrLiteral("")), StrLiteral("-"), StrLiteral("")), StrLiteral("<"), StrLiteral("")), StrLiteral(">"), StrLiteral("")), StrLiteral(" "), StrLiteral("")), StrLiteral("-"), StrLiteral("")); print("Size_148: ", programObject148.size)
    # program149 = concat("(", name.replace("-", concat(")", " ")))
    programObject149 = StrConcat(StrLiteral("("), StrReplace(_arg_0, StrLiteral("-"), StrConcat(StrLiteral(")"), StrLiteral(" ")))); print("Size_149: ", programObject149.size)
    # program150 = concat(concat(_arg_0, " "), _arg_1)
    programObject150 = StrConcat(StrConcat(_arg_0, StrLiteral(" ")), _arg_1); print("Size_150: ", programObject150.size)
    # program151 = concat(lastname, concat(" ", firstname))
    programObject151 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), _arg_1)); print("Size_151: ", programObject151.size)
    # program152 = concat(concat(" ", _arg_0), " ").Substr(concat(_arg_0.CharAt(8), _arg_0).IndexOf(" "),-1).replace(concat(" ", _arg_0), concat(concat(concat(" ", _arg_0), " ").Substr(concat(_arg_0.CharAt(8), _arg_0).IndexOf(" "),-1).Substr(0,9), " "))
    programObject152 = \
    StrReplace(
        StrSubstr(
            StrConcat(
                StrConcat(
                    StrLiteral(" "),
                    _arg_0
                ),
                StrLiteral(" ")
            ),
            IntIndexOf(
                StrConcat(
                    StrConcat(
                        StrLiteral(" "),
                        _arg_0
                    ),
                    StrLiteral(" ")
                ),
                StrConcat(
                    StrCharAt(
                        _arg_0,
                        IntLiteral(8)
                    ),
                    _arg_0
                ),
                IntLiteral(0)
            ),
            IntLiteral(-1)
        ),
        StrConcat(
            StrConcat(
                StrConcat(
                    StrLiteral(" "),
                    _arg_0
                ),
                StrLiteral(" ")
            ),
            StrSubstr(
                StrSubstr(
                    StrConcat(
                        StrConcat(
                            StrConcat(
                                StrLiteral(" "),
                                _arg_0
                            ),
                            StrLiteral(" ")
                        ),
                        StrConcat(
                            StrCharAt(
                                _arg_0,
                                IntLiteral(8)
                            ),
                            _arg_0
                        )
                    ),
                    IntIndexOf(
                        StrConcat(
                            StrConcat(
                                StrConcat(
                                    StrLiteral(" "),
                                    _arg_0
                                ),
                                StrLiteral(" ")
                            ),
                            StrConcat(
                                StrCharAt(
                                    _arg_0,
                                    IntLiteral(8)
                                ),
                                _arg_0
                            )
                        ),
                        StrLiteral(" "),
                        IntLiteral(0)
                    ),
                    IntLiteral(-1)
                ),
                IntLiteral(0),
                IntLiteral(9)
            )
        ),
        StrConcat(
            StrConcat(
                StrConcat(
                    StrLiteral(" "),
                    _arg_0
                ),
                StrLiteral(" ")
            ),
            StrLiteral(" ")
        )
    ); print("Size_152: ", programObject152.size)
    
    # program153 = name.Substr((name.IndexOf(" ") + 5),(0 - 4))
    programObject153 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(5)), IntMinus(IntLiteral(0), IntLiteral(4))); print("Size_153: ", programObject153.size)
    # program154 = name.Substr((name.IndexOf(" ") + 1),name.Length())
    programObject154 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)); print("Size_154: ", programObject154.size)
    # program155 = name.replace("-", ".").replace("-", ".")
    programObject155 = StrReplace(StrReplace(_arg_0, StrLiteral("-"), StrLiteral(".")), StrLiteral("-"), StrLiteral(".")); print("Size_155: ", programObject155.size)
    # program156 = _arg_0.Substr(_arg_0.IndexOf(_arg_0.Substr(_arg_0.IndexOf(1.IntToStr(),(_arg_0.IndexOf(" ") + 3)),(3 * 5))),_arg_0.Length()).Substr(0,4)
    # programObject156 = StrSubstr(StrSubstr(_arg_0, IntIndexOf(_arg_0, StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(3)), IntMultiply(IntLiteral(3), IntLiteral(5)))), IntLength(_arg_0)), IntLiteral(0), IntLiteral(4)); print("Size_156: ", programObject156.size)
    programObject156 = \
    StrSubstr(
        StrSubstr(
            _arg_0,
            IntIndexOf(
                _arg_0,
                StrSubstr(
                    _arg_0,
                    IntIndexOf(
                        _arg_0, 
                        StrIntToStr(IntLiteral(1)), 
                        IntPlus(
                            IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(0)), 
                            IntLiteral(3)
                        )
                    ),
                    IntMultiply(IntLiteral(3), IntLiteral(5))
                ),
                IntLiteral(0)
            ),
            IntLength(_arg_0)
        ),
        IntLiteral(0),
        IntLiteral(4)
    )

    print("Size_156: ", programObject156.size)

    # program157 = concat(concat(concat(col1, ","), " "), col2)
    programObject157 = StrConcat(StrConcat(StrConcat(_arg_0, StrLiteral(",")), StrLiteral(" ")), _arg_1); print("Size_157: ", programObject157.size)
    # program158 = name.Substr((0 - 3),name.Length())
    programObject158 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntLength(_arg_0), IntLiteral(3))); print("Size_158: ", programObject158.size)
    # program159 = concat(concat(_arg_0, " "), _arg_1)
    programObject159 = StrConcat(StrConcat(_arg_0, StrLiteral(" ")), _arg_1); print("Size_159: ", programObject159.size)
    # program160 = concat("(", name.replace("-", concat(")", " ")))
    programObject160 = StrConcat(StrLiteral("("), StrReplace(_arg_0, StrLiteral("-"), StrConcat(StrLiteral(")"), StrLiteral(" ")))); print("Size_160: ", programObject160.size)
    # program161 = _arg_0.replace(".", "").replace(".", "").replace("-", "").replace("<", "").replace(" ", "").replace(">", "").replace("-", "")
    programObject161 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("."), StrLiteral("")), StrLiteral("."), StrLiteral("")), StrLiteral("-"), StrLiteral("")), StrLiteral("<"), StrLiteral("")), StrLiteral(" "), StrLiteral("")), StrLiteral(">"), StrLiteral("")), StrLiteral("-"), StrLiteral("")); print("Size_161: ", programObject161.size)
    # program162 = name.Substr(0,name.IndexOf(" "))
    programObject162 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_162: ", programObject162.size)
    # program163 = _arg_0.Substr((-1 - (_arg_0.Length() % (_arg_0.IndexOf("=") + -1))),_arg_0.Length())
    programObject163 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntModulo(IntLength(_arg_0), IntPlus(IntIndexOf(_arg_0, StrLiteral("="), IntLiteral(1)), IntLiteral(-1)))) , IntLength(_arg_0)); print("Size_163: ", programObject163.size)
    # program164 = _arg_0.replace(_arg_1.lower(), "").replace(_arg_1.lower(), "")
    # programObject164 = StrReplace(StrReplace(_arg_0, StrLower(_arg_1), StrLiteral("")), StrLower(_arg_1), StrLiteral("")); print("Size_164: ", programObject164.size)
    programObject164 = \
    StrReplace(
        StrReplace(
            _arg_0,
            StrLower(_arg_1),
            StrLiteral("")
        ),
        StrLower(_arg_1),
        StrLiteral("")
    )

    print("Size_164: ", programObject164.size)

    # program165 = _arg_0.Substr(((-1 + -1) - _arg_0.IndexOf("/")),_arg_0.Length()).replace("/", "")
    # programObject165 = StrReplace(StrSubstr(_arg_0, IntMinus(IntMinus(IntLiteral(-1), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(1)))), StrLiteral("/"), StrLiteral("")); print("Size_165: ", programObject165.size)
    programObject165 = \
    StrReplace(
        StrSubstr(
            _arg_0,
            IntMinus(
                IntMinus(
                    IntLiteral(-1),
                    IntLiteral(1)
                ),
                IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(0))
            ),
            IntLength(_arg_0)
        ),
        StrLiteral("/"),
        StrLiteral("")
    )

    print("Size_165: ", programObject165.size)

    # program166 = _arg_0.Substr(0,(_arg_0.IndexOf("-") + -1))
    programObject166 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1)), IntLiteral(1))); print("Size_166: ", programObject166.size)
    # program167 = _arg_0.replace(" ", "-").replace(" ", "-")
    programObject167 = StrReplace(StrReplace(_arg_0, StrLiteral(" "), StrLiteral("-")), StrLiteral(" "), StrLiteral("-")); print("Size_167: ", programObject167.size)
    # program168 = _arg_0.replace(concat((if_arg_1.SuffixOf(_arg_0) then " " else ""), _arg_1), "")
    programObject168 = StrReplace(_arg_0, StrConcat(StrIte(BoolSuffixof(_arg_1, _arg_0), StrLiteral(" "), StrLiteral("")), _arg_1), StrLiteral("")); print("Size_168: ", programObject168.size)
    # program169 = _arg_0.replace(concat((if_arg_1.SuffixOf(_arg_0) then " " else ""), _arg_1), "")
    programObject169 = StrReplace(_arg_0, StrConcat(StrIte(BoolSuffixof(_arg_1, _arg_0), StrLiteral(" "), StrLiteral("")), _arg_1), StrLiteral("")); print("Size_169: ", programObject169.size)
    # program170 = _arg_0.Substr(0,(_arg_0.IndexOf("-") + -1))
    programObject170 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1)), IntLiteral(1))); print("Size_170: ", programObject170.size)
    # program171 = _arg_0.replace(" ", "-").replace(" ", "-")
    programObject171 = StrReplace(StrReplace(_arg_0, StrLiteral(" "), StrLiteral("-")), StrLiteral(" "), StrLiteral("-")); print("Size_171: ", programObject171.size)
    # program172 = concat(concat(_arg_1.CharAt(0), _arg_0), "_acme.com")
    programObject172 = StrConcat(StrConcat(StrCharAt(_arg_1, IntLiteral(0)), _arg_0), StrLiteral("_acme.com")); print("Size_172: ", programObject172.size)
    # program173 = _arg_1.Substr(0,_arg_1.IndexOf("_"))
    programObject173 = StrSubstr(_arg_1, IntLiteral(0), IntIndexOf(_arg_1, StrLiteral("_"), IntLiteral(1))); print("Size_173: ", programObject173.size)
    # program174 = _arg_0.Substr((-1 - (_arg_0.IndexOf("/") + 1)),_arg_0.Length()).replace("/", "")
    programObject174 =\
    StrReplace(
        StrSubstr(
            _arg_0,
            IntMinus(
                IntLiteral(-1),
                IntPlus(
                    IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(0)), 
                    IntLiteral(1)
                ),
            ),
            IntLength(_arg_0)
        ),
        StrLiteral("/"),
        StrLiteral("")
    ); print("Size_174: ", programObject174.size)
    # program175 = name.Substr(0,name.IndexOf(" "))
    programObject175 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_175: ", programObject175.size)
    # program176 = _arg_0.replace(".", "").replace(".", "").replace("-", "").replace("<", "").replace(" ", "").replace(">", "").replace("-", "")
    programObject176 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("."), StrLiteral("")), StrLiteral("."), StrLiteral("")), StrLiteral("-"), StrLiteral("")), StrLiteral("<"), StrLiteral("")), StrLiteral(" "), StrLiteral("")), StrLiteral(">"), StrLiteral("")), StrLiteral("-"), StrLiteral("")); print("Size_176: ", programObject176.size)
    # program177 = concat("(", name.replace("-", concat(")", " ")))
    programObject177 = StrConcat(StrLiteral("("), StrReplace(_arg_0, StrLiteral("-"), StrConcat(StrLiteral(")"), StrLiteral(" ")))); print("Size_177: ", programObject177.size)
    # program178 = concat(concat(_arg_0, " "), _arg_1)
    programObject178 = StrConcat(StrConcat(_arg_0, StrLiteral(" ")), _arg_1); print("Size_178: ", programObject178.size)
    # program179 = name.Substr((0 - 3),name.Length())
    programObject179 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntLength(_arg_0), IntLiteral(3))); print("Size_179: ", programObject179.size)
    # program180 = _arg_0.Substr(_arg_0.IndexOf(_arg_0.Substr(_arg_0.IndexOf(1.IntToStr(),(_arg_0.IndexOf(" ") + 3)),(3 * 5))),_arg_0.Length()).Substr(0,4)
    # programObject180 = StrSubstr(StrSubstr(_arg_0, IntIndexOf(_arg_0, StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(3)), IntMultiply(IntLiteral(3), IntLiteral(5)))), IntLength(_arg_0)), IntLiteral(0), IntLiteral(4)); print("Size_180: ", programObject180.size)
    programObject180 = \
    StrSubstr(
        StrSubstr(
            _arg_0,
            IntIndexOf(
                _arg_0,
                StrSubstr(
                    _arg_0,
                    IntPlus(
                        IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(0)),
                        IntLiteral(3)
                    ),
                    IntMultiply(IntLiteral(3), IntLiteral(5))
                ),
                IntLiteral(0)
            ),
            IntLength(_arg_0)
        ),
        IntLiteral(0),
        IntLiteral(4)
    )

    print("Size_180: ", programObject180.size)

    # program181 = concat(col1, concat(",", concat(" ", col2)))
    programObject181 = StrConcat(_arg_0, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), _arg_1))); print("Size_181: ", programObject181.size)
    # program182 = name.Substr((name.IndexOf(" ") + 1),name.Length())
    programObject182 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)); print("Size_182: ", programObject182.size)
    # program183 = name.replace("-", ".").replace("-", ".")
    programObject183 = StrReplace(StrReplace(_arg_0, StrLiteral("-"), StrLiteral(".")), StrLiteral("-"), StrLiteral(".")); print("Size_183: ", programObject183.size)
    # program184 = name.Substr((name.IndexOf(" ") + 1),name.Length())
    programObject184 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)); print("Size_184: ", programObject184.size)
    # program185 = name.replace("-", ".").replace("-", ".")
    programObject185 = StrReplace(StrReplace(_arg_0, StrLiteral("-"), StrLiteral(".")), StrLiteral("-"), StrLiteral(".")); print("Size_185: ", programObject185.size)
    # program186 = name.Substr((0 - 3),name.Length())
    programObject186 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntLength(_arg_0), IntLiteral(3))); print("Size_186: ", programObject186.size)
    # program187 = _arg_0.Substr(_arg_0.IndexOf(_arg_0.Substr(_arg_0.IndexOf(1.IntToStr(),(_arg_0.IndexOf(" ") + 3)),(3 * 5))),_arg_0.Length()).Substr(0,4)
    # programObject187 = StrSubstr(StrSubstr(_arg_0, IntIndexOf(_arg_0, StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(3)), IntMultiply(IntLiteral(3), IntLiteral(5)))), IntLength(_arg_0)), IntLiteral(0), IntLiteral(4)); print("Size_187: ", programObject187.size)
    programObject187 = \
    StrSubstr(
        StrSubstr(
            _arg_0,
            IntIndexOf(
                _arg_0,
                StrSubstr(
                    _arg_0,
                    IntPlus(
                        IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(0)),
                        IntLiteral(3)
                    ),
                    IntMultiply(IntLiteral(3), IntLiteral(5))
                ),
                IntLiteral(0)
            ),
            IntLength(_arg_0)
        ),
        IntLiteral(0),
        IntLiteral(4)
    )

    print("Size_187: ", programObject187.size)

    # program188 = concat(lastname, concat(" ", firstname))
    programObject188 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), _arg_1)); print("Size_188: ", programObject188.size)
    # program189 = concat(concat(" ", _arg_0), " ").Substr(concat(_arg_0.CharAt(8), _arg_0).IndexOf(" "),-1).replace(concat(" ", _arg_0), concat(concat(concat(" ", _arg_0), " ").Substr(concat(_arg_0.CharAt(8), _arg_0).IndexOf(" "),-1).Substr(0,9), " "))
    programObject189 = \
        StrReplace(
            StrSubstr(
                StrConcat(
                    StrConcat(
                        StrLiteral(" "), 
                        _arg_0
                    ), 
                    StrLiteral(" ")
                ), 
                IntIndexOf(
                    StrConcat(
                        StrCharAt(_arg_0, IntLiteral(8)), 
                        _arg_0
                    ), 
                    StrLiteral(" "), 
                    IntLiteral(0)
                ), 
                IntLiteral(-1)
            ), 
            StrConcat(
                StrLiteral(" "), 
                _arg_0
            ), 
            StrSubstr(
                StrSubstr(
                    StrConcat(
                        StrConcat(
                            StrConcat(
                                StrLiteral(" "), 
                                _arg_0
                            ), 
                            StrLiteral(" ")
                        ), 
                        IntIndexOf(
                            StrConcat(
                                StrCharAt(_arg_0, IntLiteral(8)), 
                                _arg_0
                            ), 
                            StrLiteral(" "), 
                            IntLiteral(0)
                        )
                    ), 
                    IntLiteral(0), 
                    IntLiteral(9)
                ), 
                StrLiteral(" "),
                IntLiteral(-1)
            )
        )

    print("Size_189: ", programObject189.size)
                
    # program190 = name.Substr((name.IndexOf("-") + 1),(0 - 4))
    # program191 = (if_arg_0.Contain("windows") then "windows" else (if"/".SuffixOf(_arg_0) then "microsoft" else "mac"))
    # program192 = _arg_0.replace(_arg_1.lower(), "").replace(_arg_1.lower(), "")
    # program193 = (if_arg_0.Contain(" ") then _arg_0.Substr(0,((-1 - (1 + 1)) * (1 + 1))) else _arg_0)
    # program194 = _arg_0.Substr((-1 - (_arg_0.Length() % (_arg_0.IndexOf("=") + -1))),_arg_0.Length())
    # program195 = _arg_0.Substr((-1 - (_arg_0.IndexOf("/") + 1)),_arg_0.Length()).replace("/", "")
    # program196 = concat(concat(_arg_1.CharAt(0), _arg_0), "_acme.com")
    # program197 = _arg_1.Substr(0,_arg_1.IndexOf("_"))
    # program198 = _arg_0.Substr(0,(_arg_0.IndexOf("-") + -1))
    # program199 = _arg_1.Substr(0,_arg_1.IndexOf("_"))
    programObject190 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1)), IntLiteral(1)), IntMinus(IntLiteral(0), IntLiteral(4))); print("Size_190: ", programObject190.size)
    programObject191 = StrIte(BoolContain(_arg_0, StrLiteral("windows")), StrLiteral("windows"), StrIte(BoolSuffixof(StrLiteral("/"), _arg_0), StrLiteral("microsoft"), StrLiteral("mac"))); print("Size_191: ", programObject191.size)
    programObject192 = StrReplace(StrReplace(_arg_0, StrLower(_arg_1), StrLiteral("")), StrLower(_arg_1), StrLiteral("")); print("Size_192: ", programObject192.size)
    programObject193 = StrIte(BoolContain(_arg_0, StrLiteral(" ")), StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntMinus(IntLiteral(-1), IntPlus(IntLiteral(1), IntLiteral(1))), IntMultiply(IntPlus(IntLiteral(1), IntLiteral(1)), IntLiteral(1)))), _arg_0); print("Size_193: ", programObject193.size)
    programObject194 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntModulo(IntLength(_arg_0), IntPlus(IntIndexOf(_arg_0, StrLiteral("="), IntLiteral(1)), IntLiteral(-1)))), IntLength(_arg_0)); print("Size_194: ", programObject194.size)
    programObject195 = StrReplace(StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntPlus(IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(1)), IntLiteral(1))), IntLength(_arg_0)), StrLiteral("/"), StrLiteral("")); print("Size_195: ", programObject195.size)
    programObject196 = StrConcat(StrConcat(StrCharAt(_arg_1, IntLiteral(0)), _arg_0), StrLiteral("_acme.com")); print("Size_196: ", programObject196.size)
    programObject197 = StrSubstr(_arg_1, IntLiteral(0), IntIndexOf(_arg_1, StrLiteral("_"), IntLiteral(1))); print("Size_197: ", programObject197.size)
    programObject198 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1)), IntLiteral(1))); print("Size_198: ", programObject198.size)
    programObject199 = StrSubstr(_arg_1, IntLiteral(0), IntIndexOf(_arg_1, StrLiteral("_"), IntLiteral(1))); print("Size_199: ", programObject199.size)

    # program200 = concat(concat(_arg_1.CharAt(0), _arg_0), "_acme.com")
    programObject200 = StrConcat(StrConcat(StrCharAt(_arg_1, IntLiteral(0)), _arg_0), StrLiteral("_acme.com")); print("Size_200: ", programObject200.size)
    # program201 = _arg_0.Substr((-1 - (_arg_0.Length() % (_arg_0.IndexOf("=") + -1))),_arg_0.Length())
    programObject201 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntModulo(IntLength(_arg_0), IntPlus(IntIndexOf(_arg_0, StrLiteral("="), IntLiteral(1)), IntLiteral(-1)))) , IntLength(_arg_0)); print("Size_201: ", programObject201.size)
    # program202 = _arg_0.replace(_arg_1.lower(), "").replace(_arg_1.lower(), "")
    programObject202 = StrReplace(StrReplace(_arg_0, StrLower(_arg_1), StrLiteral("")), StrLower(_arg_1), StrLiteral("")); print("Size_202: ", programObject202.size)
    # program203 = (if_arg_0.Contain(" ") then _arg_0.Substr(0,_arg_0.replace("|", _arg_0).IndexOf(_arg_0)) else _arg_0)
    programObject203 = StrIte(BoolContain(_arg_0, StrLiteral(" ")), StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrReplace(_arg_0, StrLiteral("|"), _arg_0), IntLiteral(1))), _arg_0); print("Size_203: ", programObject203.size)
    # program204 = (if_arg_0.Contain("windows") then "windows" else (if"/".SuffixOf(_arg_0) then "microsoft" else "mac"))
    programObject204 = StrIte(BoolContain(_arg_0, StrLiteral("windows")), StrLiteral("windows"), StrIte(BoolSuffixof(StrLiteral("/"), _arg_0), StrLiteral("microsoft"), StrLiteral("mac"))); print("Size_204: ", programObject204.size)
    # program205 = name.Substr((name.IndexOf("-") + 1),(0 - 4))
    programObject205 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1)), IntLiteral(1)), IntMinus(IntLiteral(0), IntLiteral(4))); print("Size_205: ", programObject205.size)
    # program206 = concat(lastname, concat(" ", firstname))
    programObject206 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), _arg_1)); print("Size_206: ", programObject206.size)
    # program207 = concat(concat(" ", _arg_0), " ").Substr(concat(_arg_0.CharAt(8), _arg_0).IndexOf(" "),-1).replace(concat(" ", _arg_0), concat(concat(concat(" ", _arg_0), " ").Substr(concat(_arg_0.CharAt(8), _arg_0).IndexOf(" "),-1).Substr(0,9), " "))
    # program208 = concat(concat(concat(col1, ","), " "), col2)
    programObject208 = StrConcat(StrConcat(StrConcat(_arg_0, StrLiteral(",")), StrLiteral(" ")), _arg_1); print("Size_208: ", programObject208.size)
    # program209 = name.replace("-", ".").replace("-", ".")
    programObject209 = StrReplace(StrReplace(_arg_0, StrLiteral("-"), StrLiteral(".")), StrLiteral("-"), StrLiteral(".")); print("Size_209: ", programObject209.size)
    # program210 = name.Substr((name.IndexOf(" ") + 1),name.Length())
    programObject210 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)); print("Size_210: ", programObject210.size)
    # program211 = _arg_0.Substr((-1 - ((1 + 1) + 1)),-1)
    programObject211 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntLiteral(1))), IntLiteral(-1)); print("Size_211: ", programObject211.size)
    # program212 = _arg_0.Substr(((1 + 1) + _arg_0.IndexOf("=")),_arg_0.Length())
    programObject212 = StrSubstr(_arg_0, IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("="), IntLiteral(1))), IntLength(_arg_0)); print("Size_212: ", programObject212.size)
    # program213 = concat(_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", ""), (ifEqual("",_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", "")) then "" else _arg_0).Substr(0,1)).lower().replace(_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", ""), _arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", "").replace(_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", "").Substr(0,1), (ifEqual("",_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", "")) then "" else _arg_0).Substr(0,1)))
    # program214 = _arg_0.Substr((_arg_0.IndexOf(".") + -1),((1 + 1) + _arg_0.IndexOf(".")))
    programObject214 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(1)), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)))); print("Size_214: ", programObject214.size)
    # program215 = _arg_0.Substr((_arg_0.IndexOf(".") * -1),_arg_0.Length()).replace(".", "")
    programObject215 = StrReplace(StrSubstr(_arg_0, IntMultiply(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(-1)), IntLength(_arg_0)), StrLiteral("."), StrLiteral("")); print("Size_215: ", programObject215.size)
    # program216 = _arg_0.Substr(("/n".Length() * (_arg_0.Length() % (-1 - (_arg_0.IndexOf(" ") * "/n".Length())))),_arg_0.Length()).Substr(_arg_0.Substr(("/n".Length() * (_arg_0.Length() % (-1 - (_arg_0.IndexOf(" ") * "/n".Length())))),_arg_0.Length()).IndexOf(1.IntToStr()),_arg_0.Substr(("/n".Length() * (_arg_0.Length() % (-1 - (_arg_0.IndexOf(" ") * "/n".Length())))),_arg_0.Length()).Length())
    # program217 = _arg_0.Substr((("9".StrToInt() * 2) + -1),_arg_0.Length())
    programObject217 = StrSubstr(_arg_0, IntPlus(IntMultiply(IntStrToInt(StrLiteral("9")), IntLiteral(2)), IntLiteral(-1)), IntLength(_arg_0)); print("Size_217: ", programObject217.size)
    # program218 = _arg_0.Substr((_arg_0.IndexOf(" ",(_arg_0.IndexOf(" ") + 1)) + 1),_arg_0.Length())
    programObject218 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1))), IntLiteral(1)), IntLength(_arg_0)); print("Size_218: ", programObject218.size)
    # program219 = _arg_0.replace(concat(" ", " "), "").replace(concat(" ", " "), " ")
    programObject219 = StrReplace(StrReplace(_arg_0, StrConcat(StrLiteral(" "), StrLiteral(" ")), StrLiteral("")), StrConcat(StrLiteral(" "), StrLiteral(" ")), StrLiteral(" ")); print("Size_219: ", programObject219.size)
    # program220 = _arg_0.Substr(0,(((-1 + -1) * (_arg_0.Length() % ((-1 + -1) + -1))) % (1 - _arg_0.Length())))
    programObject220 = StrSubstr(_arg_0, IntLiteral(0), IntModulo(IntMultiply(IntMinus(IntLiteral(-1), IntLiteral(1)), IntModulo(IntLength(_arg_0), IntPlus(IntMinus(IntLiteral(-1), IntLiteral(1)), IntLiteral(-1)))), IntMinus(IntLiteral(1), IntLength(_arg_0)))); print("Size_220: ", programObject220.size)
    # program221 = _arg_1.Substr((_arg_1.IndexOf("_") + 1),_arg_1.Length())
    programObject221 = StrSubstr(_arg_1, IntPlus(IntIndexOf(_arg_1, StrLiteral("_"), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_1)); print("Size_221: ", programObject221.size)
    # program222 = _arg_0.Substr((-1 - (3 * 3)),_arg_0.Length())
    programObject222 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntMultiply(IntLiteral(3), IntLiteral(3))), IntLength(_arg_0)); print("Size_222: ", programObject222.size)
    # program223 = _arg_0.Substr((-1 - ((1 + 1) + 1)),_arg_0.Length())
    programObject223 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntLiteral(1))), IntLength(_arg_0)); print("Size_223: ", programObject223.size)
    # program224 = concat(firstname, concat(" ", lastname))
    programObject224 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), _arg_1)); print("Size_224: ", programObject224.size)
    # program225 = concat(firstname, concat(" ", lastname))
    programObject225 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), _arg_1)); print("Size_225: ", programObject225.size)
    # program226 = _arg_0.Substr((-1 - ((1 + 1) + 1)),_arg_0.Length())
    programObject226 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntLiteral(1))), IntLength(_arg_0)); print("Size_226: ", programObject226.size)
    # program227 = _arg_0.Substr(0,_arg_0.IndexOf(" ",(-1 - _arg_0.IndexOf(" "))))
    programObject227 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntMinus(IntLiteral(-1), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))))); print("Size_227: ", programObject227.size)
    # program228 = _arg_0.Substr(0,_arg_0.IndexOf("."))
    programObject228 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1))); print("Size_228: ", programObject228.size)
    # program229 = _arg_1.Substr((_arg_1.IndexOf("_") + 1),_arg_1.Length())
    programObject229 = StrSubstr(_arg_1, IntPlus(IntIndexOf(_arg_1, StrLiteral("_"), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_1)); print("Size_229: ", programObject229.size)
    # program230 = _arg_0.Substr(0,_arg_0.replace(" ", _arg_0).IndexOf(_arg_0))
    programObject230 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrReplace(_arg_0, StrLiteral(" "), _arg_0), IntLiteral(1))); print("Size_230: ", programObject230.size)
    # program231 = _arg_0.replace(concat(" ", " "), "").replace(concat(" ", " "), " ")
    programObject231 = StrReplace(StrReplace(_arg_0, StrConcat(StrLiteral(" "), StrLiteral(" ")), StrLiteral("")), StrConcat(StrLiteral(" "), StrLiteral(" ")), StrLiteral(" ")); print("Size_231: ", programObject231.size)
    # program232 = _arg_0.Substr((("9".StrToInt() * 2) + -1),_arg_0.Length())
    programObject232 = StrSubstr(_arg_0, IntPlus(IntMultiply(IntStrToInt(StrLiteral("9")), IntLiteral(2)), IntLiteral(-1)), IntLength(_arg_0)); print("Size_232: ", programObject232.size)
    # program233 = _arg_0.Substr((_arg_0.IndexOf(" ",(_arg_0.IndexOf(" ") + 1)) + 1),_arg_0.Length())
    programObject233 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1))), IntLiteral(1)), IntLength(_arg_0)); print("Size_233: ", programObject233.size)
    # program234 = _arg_0.Substr((_arg_0.IndexOf(".") + -1),((1 + 1) + _arg_0.IndexOf(".")))
    programObject234 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(1)), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)))); print("Size_234: ", programObject234.size)
    # program235 = concat(_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", ""), (ifEqual("",_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", "")) then "" else _arg_0).Substr(0,1)).lower().replace(_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", ""), _arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", "").replace(_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", "").Substr(0,1), (ifEqual("",_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", "")) then "" else _arg_0).Substr(0,1)))
    # program236 = concat(concat(0.IntToStr(), _arg_0.CharAt(1)), concat("/", _arg_0.Substr(_arg_0.IndexOf((1 + 1).IntToStr()),_arg_0.Length())))
    programObject236 = StrConcat(StrConcat(StrConcat(StrIntToStr(IntLiteral(0)), StrCharAt(_arg_0, IntLiteral(1))), StrLiteral("/")), StrSubstr(_arg_0, IntIndexOf(_arg_0, StrConcat(StrIntToStr(IntPlus(IntLiteral(1), IntLiteral(1))), StrLiteral(".")), IntLiteral(0)), IntLength(_arg_0))); print("Size_236: ", programObject236.size)
    # program237 = _arg_0.replace("<", "").replace(">", "").replace("<", "").replace("<", "").replace(">", "").replace(">", "")
    # programObject237 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("<"), StrLiteral("")), StrLiteral(">"), StrLiteral("")), StrLiteral("<"), StrLiteral("")), StrLiteral("<"), StrLiteral("")), StrLiteral(">"), StrLiteral("")), StrLiteral(">"), StrLiteral(""))); print("Size_237: ", programObject237.size)
    # program238 = _arg_0.Substr(((1 + 1) + _arg_0.IndexOf("=")),_arg_0.Length())
    programObject238 = StrSubstr(_arg_0, IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("="), IntLiteral(1))), IntLength(_arg_0)); print("Size_238: ", programObject238.size)
    # program239 = _arg_0.Substr((-1 - ((1 + 1) + 1)),-1)
    programObject239 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntLiteral(1))), IntLiteral(-1)); print("Size_239: ", programObject239.size)
    # program240 = _arg_0.Substr(((1 + 1) + _arg_0.IndexOf("=")),_arg_0.Length())
    programObject240 = StrSubstr(_arg_0, IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("="), IntLiteral(1))), IntLength(_arg_0)); print("Size_240: ", programObject240.size)
    # program241 = _arg_0.Substr((-1 - ((1 + 1) + 1)),-1)
    programObject241 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntLiteral(1))), IntLiteral(-1)); print("Size_241: ", programObject241.size)
    # program242 = _arg_0.replace("<", "").replace(">", "").replace("<", "").replace("<", "").replace(">", "").replace(">", "")
    # programObject242 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("<"), StrLiteral("")), StrLiteral(">"), StrLiteral("")), StrLiteral("<"), StrLiteral("")), StrLiteral("<"), StrLiteral("")), StrLiteral(">"), StrLiteral("")), StrLiteral(">"), StrLiteral(""))); print("Size_242: ", programObject242.size)
    # program243 = concat(0.IntToStr(), concat(_arg_0.CharAt(1), concat("/", _arg_0.Substr(_arg_0.IndexOf((1 + 1).IntToStr()),_arg_0.Length()))))
    # programObject243 = StrConcat(StrConcat(StrConcat(StrIntToStr(IntLiteral(0)), StrCharAt(_arg_0, IntLiteral(1))), StrLiteral("/")), StrSubstr(_arg_0, IntIndexOf(_arg_0, StrConcat(StrIntToStr(IntPlus(IntLiteral(1), IntLiteral(1))), StrLiteral("."))), IntLength(_arg_0))); print("Size_243: ", programObject243.size)
    # program244 = (ifEqual(col2,col2.replace(concat(" ", (ifcol2.Contain("USA") then "New York" else "USA")), "NY")) then concat(col2.replace(concat(" ", (ifcol2.Contain("USA") then "New York" else "USA")), "NY").replace(concat(",", concat(" ", "USA")), ","), concat(" ", "USA")).replace(col2.replace("USA", " "), concat(col2, ",")) else concat(col2.replace(concat(" ", (ifcol2.Contain("USA") then "New York" else "USA")), "NY").replace(concat(",", concat(" ", "USA")), ","), concat(" ", "USA")).replace("CA", concat("CA", ",")).replace("NY", concat(" ", "NY")))
    # program245 = concat(concat(concat(_arg_0, concat("/n", _arg_1)), "/n"), _arg_2)
    # programObject245 = StrConcat(StrConcat(StrConcat(StrConcat(_arg_0, StrConcat(StrLiteral("/n"), _arg_1)), StrLiteral("/n")), _arg_2)); print("Size_245: ", programObject245.size)
    # program246 = _arg_0.Substr((_arg_0.IndexOf("/") - (-1 + -1)),_arg_0.Length())
    programObject246 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(1)), IntLiteral(-1)), IntLength(_arg_0)); print("Size_246: ", programObject246.size)
    # program247 = _arg_0.Substr(_arg_0.IndexOf(1.IntToStr(),(((-1 - "/n".Length()) + -1) * _arg_0.IndexOf(" "))),_arg_0.Length())
    programObject247 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrConcat(StrIntToStr(IntLiteral(1)), StrLiteral(".")), IntMultiply(IntMinus(IntMinus(IntLiteral(-1), IntLength(StrLiteral("/n"))), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)))), IntLength(_arg_0)); print("Size_247: ", programObject247.size)
    # program248 = _arg_0.Substr((_arg_0.IndexOf(".") * -1),_arg_0.Length()).replace(".", "")
    programObject248 = StrReplace(StrSubstr(_arg_0, IntMultiply(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(-1)), IntLength(_arg_0)), StrLiteral("."), StrLiteral("")); print("Size_248: ", programObject248.size)
    # program249 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),((-1 + -1) * (1 - (-1 + -1))))
    programObject249 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntMultiply(IntMinus(IntLiteral(-1), IntLiteral(1)), IntMinus(IntLiteral(1), IntMinus(IntLiteral(-1), IntLiteral(1))))); print("Size_249: ", programObject249.size)
    # program250 = name.replace(" ", concat(" ", "(")).replace("-", concat(")", " "))
    programObject250 = StrReplace(StrReplace(_arg_0, StrLiteral(" "), StrConcat(StrLiteral(" "), StrLiteral("("))), StrLiteral("-"), StrConcat(StrLiteral(")"), StrLiteral(" "))); print("Size_250: ", programObject250.size)
    # program251 = _arg_0.Substr(0,((-1 - "in".Length()) * "in".Length()))
    programObject251 = StrSubstr(_arg_0, IntLiteral(0), IntMultiply(IntMinus(IntMinus(IntLiteral(-1), IntLength(StrLiteral("in"))), IntLiteral(1)), IntLength(StrLiteral("in")))); print("Size_251: ", programObject251.size)
    # program252 = _arg_0.Substr((-1 - (3 * 3)),_arg_0.Length())
    programObject252 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntMultiply(IntLiteral(3), IntLiteral(3))), IntLength(_arg_0)); print("Size_252: ", programObject252.size)
    # program253 = _arg_0.Substr(0,_arg_0.IndexOf("."))
    programObject253 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1))); print("Size_253: ", programObject253.size)
    # program254 = concat(firstname, concat(" ", lastname))
    programObject254 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), _arg_1)); print("Size_254: ", programObject254.size)
    # program255 = _arg_0.Substr((-1 - ((1 + 1) + 1)),_arg_0.Length())
    programObject255 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntLiteral(1))), IntLength(_arg_0)); print("Size_255: ", programObject255.size)
    # program256 = _arg_0.Substr(0,_arg_0.IndexOf("."))
    programObject256 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1))); print("Size_256: ", programObject256.size)
    # program257 = _arg_0.Substr(0,((-1 - "in".Length()) * "in".Length()))
    programObject257 = StrSubstr(_arg_0, IntLiteral(0), IntMultiply(IntMinus(IntMinus(IntLiteral(-1), IntLength(StrLiteral("in"))), IntLiteral(1)), IntLength(StrLiteral("in")))); print("Size_257: ", programObject257.size)
    # program258 = _arg_0.Substr((-1 - (3 * 3)),_arg_0.Length())
    programObject258 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntMultiply(IntLiteral(3), IntLiteral(3))), IntLength(_arg_0)); print("Size_258: ", programObject258.size)
    # program259 = name.replace(" ", concat(" ", "(")).replace("-", concat(")", " "))
    programObject259 = StrReplace(StrReplace(_arg_0, StrLiteral(" "), StrConcat(StrLiteral(" "), StrLiteral("("))), StrLiteral("-"), StrConcat(StrLiteral(")"), StrLiteral(" "))); print("Size_259: ", programObject259.size)
    # program260 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),((1 - (-1 + -1)) * (-1 + -1)))
    # programObject260 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntMultiply(IntMinus(IntLiteral(1), IntMinus(IntLiteral(-1), IntLiteral(1)))), IntMinus(IntLiteral(1), IntMinus(IntLiteral(-1), IntLiteral(1)))); print("Size_260: ", programObject260.size)
    # program261 = _arg_0.Substr((_arg_0.IndexOf(".") * -1),_arg_0.Length()).replace(".", "")
    programObject261 = StrReplace(StrSubstr(_arg_0, IntMultiply(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(-1)), IntLength(_arg_0)), StrLiteral("."), StrLiteral("")); print("Size_261: ", programObject261.size)
    # program262 = _arg_0.Substr(_arg_0.IndexOf(1.IntToStr(),("/n".Length() * ((-1 + -1) * _arg_0.IndexOf(" ")))),_arg_0.Length())
    # programObject262 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrConcat(StrIntToStr(IntLiteral(1)), StrLiteral(".")), IntMultiply(IntLength(StrLiteral("/n")), IntMultiply(IntMinus(IntLiteral(-1), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)))))), IntLength(_arg_0); print("Size_262: ", programObject262.size)
    # program263 = _arg_0.Substr(((_arg_0.IndexOf("/") + 1) + 1),_arg_0.Length())
    programObject263 = StrSubstr(_arg_0, IntPlus(IntPlus(IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(1)), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)); print("Size_263: ", programObject263.size)
    # program264 = concat(concat(concat(concat(_arg_0, "/n"), _arg_1), "/n"), _arg_2)
    programObject264 = StrConcat(StrConcat(StrConcat(StrConcat(_arg_0, StrLiteral("/n")), _arg_1), StrLiteral("/n")), _arg_2); print("Size_264: ", programObject264.size)
    # program265 = concat(col2.replace(concat(" ", (ifcol2.Contain("NY") then "NY" else "New York")), "NY").replace(concat(concat(",", " "), "USA"), ","), concat(" ", "USA")).replace("CA", concat("CA", ",")).replace("NY", concat(" ", "NY")).replace(concat(col2.replace(concat(" ", (ifcol2.Contain("NY") then "NY" else "New York")), "NY").replace(concat(concat(",", " "), "USA"), ","), concat(" ", "USA")), concat(col2.replace(concat(" ", (ifcol2.Contain("NY") then "NY" else "New York")), "NY").replace(concat(concat(",", " "), "USA"), ","), concat(" ", "USA")).replace("MD", concat("MD", ",")).replace("NY", concat(" ", "NY")))
    # program266 = concat(0.IntToStr(), concat(_arg_0.CharAt(1), concat("/", _arg_0.Substr(_arg_0.IndexOf((1 + 1).IntToStr()),_arg_0.Length()))))
    # programObject266 = StrConcat(StrConcat(StrConcat(StrIntToStr(IntLiteral(0)), StrCharAt(_arg_0, IntLiteral(1))), StrLiteral("/")), StrSubstr(_arg_0, IntIndexOf(_arg_0, StrConcat(StrIntToStr(IntPlus(IntLiteral(1), IntLiteral(1))), StrLiteral("."))), IntLength(_arg_0))); print("Size_266: ", programObject266.size)
    # program267 = _arg_0.replace("<", "").replace(">", "").replace("<", "").replace("<", "").replace(">", "").replace(">", "")
    # programObject267 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("<"), StrLiteral("")), StrLiteral(">"), StrLiteral("")), StrLiteral("<"), StrLiteral("")), StrLiteral("<"), StrLiteral("")), StrLiteral(">"), StrLiteral("")), StrLiteral(">"), StrLiteral(""))); print("Size_267: ", programObject267.size)
    # program268 = _arg_0.Substr((_arg_0.IndexOf("=") + (1 + 1)),_arg_0.Length())
    programObject268 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral("="), IntLiteral(1)), IntPlus(IntLiteral(1), IntLiteral(1))), IntLength(_arg_0)); print("Size_268: ", programObject268.size)
    # program269 = _arg_0.Substr((-1 - ((1 + 1) + 1)),-1)
    programObject269 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntLiteral(1))), IntLiteral(-1)); print("Size_269: ", programObject269.size)
    # program270 = concat(concat(_arg_0.Substr(0,_arg_0.IndexOf("/")), _arg_0.Substr((-1 - _arg_0.Substr(1,_arg_0.IndexOf("/")).Substr(1,-1).Length()),-1)), concat(_arg_0.Substr(0,_arg_0.IndexOf("/")), _arg_0.Substr((-1 - _arg_0.Substr(1,_arg_0.IndexOf("/")).Substr(1,-1).Length()),-1)).Substr(0,1).lower())
    # programObject270 = StrConcat(StrConcat(StrConcat(StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(1))), StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntLength(StrSubstr(_arg_0, IntLiteral(1), IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(1)))))), StrConcat(StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(1))), StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntLength(StrSubstr(_arg_0, IntLiteral(1), IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(1)))))), StrSubstr(StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(1))), IntLiteral(0), IntLiteral(1)), StrLiteral("lower")))); print("Size_270: ", programObject270.size)
    # program271 = concat(_arg_0, concat("/n", concat(_arg_1, concat("/n", _arg_2))))
    programObject271 = StrConcat(StrConcat(StrConcat(StrConcat(_arg_0, StrLiteral("/n")), _arg_1), StrLiteral("/n")), _arg_2); print("Size_271: ", programObject271.size)
    # program272 = _arg_0.Substr(((1 + 1) + _arg_0.IndexOf("/")),_arg_0.Length())
    programObject272 = StrSubstr(_arg_0, IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(1))), IntLength(_arg_0)); print("Size_272: ", programObject272.size)
    # program273 = _arg_0.Substr((_arg_0.IndexOf(".") + -1),((1 + 1) + _arg_0.IndexOf(".")))
    programObject273 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(1)), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)))); print("Size_273: ", programObject273.size)
    # program274 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),((1 - (-1 + -1)) * (-1 + -1)))
    # programObject274 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntMultiply(IntMinus(IntLiteral(1), IntMinus(IntLiteral(-1), IntLiteral(1)))), IntMinus(IntLiteral(1), IntMinus(IntLiteral(-1), IntLiteral(1)))); print("Size_274: ", programObject274.size)
    # program275 = name.replace(" ", concat(" ", "(")).replace("-", concat(")", " "))
    programObject275 = StrReplace(StrReplace(_arg_0, StrLiteral(" "), StrConcat(StrLiteral(" "), StrLiteral("("))), StrLiteral("-"), StrConcat(StrLiteral(")"), StrLiteral(" "))); print("Size_275: ", programObject275.size)
    # program276 = _arg_0.replace(concat(" ", " "), "").replace(concat(" ", " "), " ")
    programObject276 = StrReplace(StrReplace(_arg_0, StrConcat(StrLiteral(" "), StrLiteral(" ")), StrLiteral("")), StrConcat(StrLiteral(" "), StrLiteral(" ")), StrLiteral(" ")); print("Size_276: ", programObject276.size)
    # program277 = _arg_0.Substr((("9".StrToInt() * 2) + -1),_arg_0.Length())
    programObject277 = StrSubstr(_arg_0, IntPlus(IntMultiply(IntStrToInt(StrLiteral("9")), IntLiteral(2)), IntLiteral(-1)), IntLength(_arg_0)); print("Size_277: ", programObject277.size)
    # program278 = _arg_0.Substr((_arg_0.IndexOf(" ",(_arg_0.IndexOf(" ") + 1)) + 1),_arg_0.Length())
    programObject278 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1))), IntLiteral(1)), IntLength(_arg_0)); print("Size_278: ", programObject278.size)
    # program279 = _arg_1.Substr((_arg_1.IndexOf("_") + 1),_arg_1.Length())
    programObject279 = StrSubstr(_arg_1, IntPlus(IntIndexOf(_arg_1, StrLiteral("_"), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_1)); print("Size_279: ", programObject279.size)
    # program280 = _arg_0.Substr(0,_arg_0.replace(" ", _arg_0).IndexOf(_arg_0))
    programObject280 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrReplace(_arg_0, StrLiteral(" "), _arg_0), IntLiteral(1))); print("Size_280: ", programObject280.size)
    # program281 = concat(firstname, concat(" ", lastname))
    programObject281 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), _arg_1)); print("Size_281: ", programObject281.size)
    # program282 = _arg_0.Substr((-1 - ((1 + 1) + 1)),_arg_0.Length())
    programObject282 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntLiteral(1))), IntLength(_arg_0)); print("Size_282: ", programObject282.size)
    # program283 = _arg_0.Substr((-1 - ((1 + 1) + 1)),_arg_0.Length())
    programObject283 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntLiteral(1))), IntLength(_arg_0)); print("Size_283: ", programObject283.size)
    # program284 = concat(firstname, concat(" ", lastname))
    programObject284 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), _arg_1)); print("Size_284: ", programObject284.size)
    # program285 = _arg_0.Substr(0,(((_arg_0.Length() % ((-1 + -1) + -1)) * (-1 + -1)) % (1 - _arg_0.Length())))
    programObject285 = StrSubstr(_arg_0, IntLiteral(0), IntModulo(IntMultiply(IntModulo(IntLength(_arg_0), IntMinus(IntMinus(IntLiteral(-1), IntLiteral(1)), IntLiteral(1))), IntMinus(IntLiteral(-1), IntLiteral(1))), IntMinus(IntLiteral(1), IntLength(_arg_0)))); print("Size_285: ", programObject285.size)
    # program286 = _arg_1.Substr((_arg_1.IndexOf("_") + 1),_arg_1.Length())
    programObject286 = StrSubstr(_arg_1, IntPlus(IntIndexOf(_arg_1, StrLiteral("_"), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_1)); print("Size_286: ", programObject286.size)
    # program287 = _arg_0.Substr((("9".StrToInt() * 2) + -1),_arg_0.Length())
    programObject287 = StrSubstr(_arg_0, IntPlus(IntMultiply(IntStrToInt(StrLiteral("9")), IntLiteral(2)), IntLiteral(-1)), IntLength(_arg_0)); print("Size_287: ", programObject287.size)
    # program288 = _arg_0.Substr((_arg_0.IndexOf(" ",(_arg_0.IndexOf(" ") + 1)) + 1),_arg_0.Length())
    programObject288 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1))), IntLiteral(1)), IntLength(_arg_0)); print("Size_288: ", programObject288.size)
    # program289 = _arg_0.replace(concat(" ", " "), "").replace(concat(" ", " "), " ")
    programObject289 = StrReplace(StrReplace(_arg_0, StrConcat(StrLiteral(" "), StrLiteral(" ")), StrLiteral("")), StrConcat(StrLiteral(" "), StrLiteral(" ")), StrLiteral(" ")); print("Size_289: ", programObject289.size)
    # program290 = _arg_0.Substr((_arg_0.IndexOf(".") + -1),((1 + 1) + _arg_0.IndexOf(".")))
    programObject290 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(1)), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)))); print("Size_290: ", programObject290.size)
    # program291 = concat(_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", ""), _arg_0.Substr(0,_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", "").Length()).Substr(0,1)).lower().replace(_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", ""), _arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", "").replace(_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", "").Substr(0,1), _arg_0.Substr(0,_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace("/", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace(" ", "").Length()).Substr(0,1)))
    programObject291 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(1)), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)))); print("Size_291: ", programObject291.size)
    # program292 = _arg_0.Substr((-1 - ((1 + 1) + 1)),-1)
    programObject292 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntLiteral(1))), IntLiteral(-1)); print("Size_292: ", programObject292.size)
    # program293 = _arg_0.Substr(((1 + 1) + _arg_0.IndexOf("=")),_arg_0.Length())
    programObject293 = StrSubstr(_arg_0, IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("="), IntLiteral(1))), IntLength(_arg_0)); print("Size_293: ", programObject293.size)
    # program294 = _arg_0.replace("<", "").replace(">", "").replace("<", "").replace("<", "").replace(">", "").replace(">", "")
    programObject294 = StrReplace(StrReplace(_arg_0, StrConcat(StrLiteral(" "), StrLiteral(" ")), StrLiteral("")), StrConcat(StrLiteral(" "), StrLiteral(" ")), StrLiteral(" ")); print("Size_294: ", programObject294.size)
    # program295 = (if"New York".Prefixof(col2) then col2 else (ifcol2.Contain("USA") then col2 else concat(concat(col2, ","), concat(" ", "USA"))).replace("New York", "NY")).replace("New York", "CT").replace("New York", "NY").replace("CT", "New York")
    programObject295 = StrSubstr(_arg_1, IntPlus(IntIndexOf(_arg_1, StrLiteral("_"), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_1)); print("Size_295: ", programObject295.size)
    # program296 = concat(concat(concat(0.IntToStr(), _arg_0.CharAt(1)), "/"), _arg_0.Substr(_arg_0.IndexOf((1 + 1).IntToStr()),_arg_0.Length()))
    programObject296 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntMultiply(IntLiteral(3), IntLiteral(3))), IntLength(_arg_0)); print("Size_296: ", programObject296.size)
    # program297 = _arg_0.Substr((1 - (-1 - _arg_0.IndexOf("/"))),_arg_0.Length())
    programObject297 = StrSubstr(_arg_0, IntMinus(IntLiteral(1), IntMinus(IntLiteral(-1), IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(1)))), IntLength(_arg_0)); print("Size_297: ", programObject297.size)
    # program298 = concat(concat(_arg_0, concat(concat("/n", _arg_1), "/n")), _arg_2)
    programObject298 = StrSubstr(_arg_0, IntLiteral(0), IntMultiply(IntMinus(IntMinus(IntLiteral(-1), IntLength(StrLiteral("in"))), IntLiteral(1)), IntLength(StrLiteral("in")))); print("Size_298: ", programObject298.size)
    # program299 = _arg_0.Substr((_arg_0.IndexOf(".") * -1),_arg_0.Length()).replace(".", "")
    programObject299 = StrReplace(StrSubstr(_arg_0, IntMultiply(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(-1)), IntLength(_arg_0)), StrLiteral("."), StrLiteral("")); print("Size_299: ", programObject299.size)
    # program300 = _arg_0.Substr(_arg_0.IndexOf(1.IntToStr(),("/n".Length() * (_arg_0.IndexOf(" ") * (-1 + -1)))),_arg_0.Length())
    programObject300 = StrReplace(StrReplace(_arg_0, StrLiteral(" "), StrConcat(StrLiteral(" "), StrLiteral("("))), StrLiteral("-"), StrConcat(StrLiteral(")"), StrLiteral(" "))); print("Size_300: ", programObject300.size)
    # program301 = name.replace(" ", concat(" ", "(")).replace("-", concat(")", " "))
    programObject301 = StrReplace(StrReplace(_arg_0, StrLiteral(" "), StrConcat(StrLiteral(" "), StrLiteral("("))), StrLiteral("-"), StrConcat(StrLiteral(")"), StrLiteral(" "))); print("Size_301: ", programObject301.size)
    # program302 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),((1 - (-1 + -1)) * (-1 + -1)))
    programObject302 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntMultiply(IntMinus(IntLiteral(1), IntMinus(IntLiteral(-1), IntLiteral(-1))), IntMinus(IntLiteral(-1), IntLiteral(-1)))); print("Size_302: ", programObject302.size)
    # program303 = _arg_0.Substr((_arg_0.IndexOf(" ",(_arg_0.IndexOf(" ") + 1)) + 1),_arg_0.Length())
    programObject303 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1))), IntLiteral(1)), IntLength(_arg_0)); print("Size_303: ", programObject303.size)
    # program304 = _arg_0.Substr(0,_arg_0.replace(" ", _arg_0).IndexOf(_arg_0))
    programObject304 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrReplace(_arg_0, StrLiteral(" "), _arg_0), IntLiteral(1))); print("Size_304: ", programObject304.size)
    # program305 = _arg_1.Substr((_arg_1.IndexOf("_") + 1),_arg_1.Length())
    programObject305 = StrSubstr(_arg_1, IntPlus(IntIndexOf(_arg_1, StrLiteral("_"), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_1)); print("Size_305: ", programObject305.size)
    # program306 = _arg_0.Substr(0,_arg_0.IndexOf("."))
    programObject306 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1))); print("Size_306: ", programObject306.size)
    # program307 = _arg_0.Substr(0,((-1 - "in".Length()) * "in".Length()))
    programObject307 = StrSubstr(_arg_0, IntLiteral(0), IntMultiply(IntMinus(IntMinus(IntLiteral(-1), IntLength(StrLiteral("in"))), IntLiteral(1)), IntLength(StrLiteral("in")))); print("Size_307: ", programObject307.size)
    # program308 = _arg_0.Substr((-1 - (3 * 3)),_arg_0.Length())
    programObject308 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntMultiply(IntLiteral(3), IntLiteral(3))), IntLength(_arg_0)); print("Size_308: ", programObject308.size)
    # program309 = _arg_0.Substr(0,_arg_0.IndexOf(" ",(-1 - _arg_0.IndexOf(" "))))
    programObject309 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral(" "), IntMinus(IntLiteral(-1), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))))); print("Size_309: ", programObject309.size)
    # program310 = _arg_0.Substr((-1 - (3 * 3)),_arg_0.Length())
    programObject310 = StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntMultiply(IntLiteral(3), IntLiteral(3))), IntLength(_arg_0)); print("Size_310: ", programObject310.size)
    # program311 = _arg_0.Substr(0,_arg_0.IndexOf("."))
    programObject311 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1))); print("Size_311: ", programObject311.size)
    # program312 = _arg_0.replace(concat(" ", " "), "").replace(concat(" ", " "), " ")
    programObject312 = StrReplace(StrReplace(_arg_0, StrConcat(StrLiteral(" "), StrLiteral(" ")), StrLiteral("")), StrConcat(StrLiteral(" "), StrLiteral(" ")), StrLiteral(" ")); print("Size_312: ", programObject312.size)
    # program313 = _arg_0.Substr(("9".StrToInt() - (1 - "9".StrToInt())),_arg_0.Length())
    programObject313 = StrSubstr(_arg_0, IntMinus(IntStrToInt(StrLiteral("9")), IntMinus(IntLiteral(1), IntStrToInt(StrLiteral("9")))), IntLength(_arg_0)); print("Size_313: ", programObject313.size)
    # program314 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),((1 - (-1 + -1)) * (-1 + -1)))
    programObject314 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntMultiply(IntMinus(IntLiteral(1), IntMinus(IntLiteral(-1), IntLiteral(-1))), IntMinus(IntLiteral(-1), IntLiteral(-1)))); print("Size_314: ", programObject314.size)
    # program315 = name.replace(" ", concat(" ", "(")).replace("-", concat(")", " "))
    programObject315 = StrReplace(StrReplace(_arg_0, StrLiteral(" "), StrConcat(StrLiteral(" "), StrLiteral("("))), StrLiteral("-"), StrConcat(StrLiteral(")"), StrLiteral(" "))); print("Size_315: ", programObject315.size)
    # program316 = _arg_0.Substr(_arg_0.IndexOf(1.IntToStr(),((-1 + -1) - _arg_0.IndexOf(_arg_0.Substr(-1,_arg_0.Length())))),_arg_0.Length())
    programObject316 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrIntToStr(IntLiteral(1)), IntMinus(IntMinus(IntLiteral(-1), IntLiteral(-1)), IntIndexOf(_arg_0, StrSubstr(_arg_0, IntLiteral(-1), IntLength(_arg_0)), IntLiteral(1)))), IntLength(_arg_0)); print("Size_316: ", programObject316.size)
    # program317 = _arg_0.Substr((_arg_0.IndexOf(".") * -1),_arg_0.Length()).replace(".", "")
    programObject317 = StrReplace(StrSubstr(_arg_0, IntMultiply(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(-1)), IntLength(_arg_0)), StrLiteral("."), StrLiteral("")); print("Size_317: ", programObject317.size)
    # program318 = _arg_0.Substr((_arg_0.IndexOf(".") + -1),((1 + 1) + _arg_0.IndexOf(".")))
    programObject318 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(1)), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)))); print("Size_318: ", programObject318.size)
    # program319 = concat(_arg_0, concat("/n", concat(_arg_1, concat("/n", _arg_2))))
    programObject319 = StrConcat(StrConcat(StrConcat(StrConcat(_arg_0, StrLiteral("/n")), _arg_1), StrLiteral("/n")), _arg_2); print("Size_319: ", programObject319.size)
    # program320 = _arg_0.Substr(((_arg_0.IndexOf("/") + 1) + 1),_arg_0.Length())
    programObject320 = StrSubstr(_arg_0, IntPlus(IntPlus(IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(1)), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)); print("Size_320: ", programObject320.size)
    # program321 = concat(_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace(" ", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace("/", ""), _arg_0.Substr(0,_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace(" ", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace("/", "").Length()).Substr(0,1)).lower().replace(_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace(" ", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace("/", ""), _arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace(" ", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace("/", "").replace(_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace(" ", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace("/", "").Substr(0,1), _arg_0.Substr(0,_arg_0.Substr((-1 - _arg_0.IndexOf("/")),-1).replace(" ", _arg_0.Substr(1,_arg_0.IndexOf("/"))).replace("/", "").Length()).Substr(0,1)))
    # programObject321 = StrReplace(StrLower(StrConcat(StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(0)), IntLiteral(-1)), StrSubstr(StrSubstr(_arg_0, IntLiteral(0), IntLength(StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntIndexOf(_arg_0, StrLiteral("/")), IntLiteral(-1)))), IntLiteral(0), IntLiteral(1)))), StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(0)), IntLiteral(-1)), StrReplace(StrSubstr(_arg_0, IntLiteral(0), IntLength(StrSubstr(_arg_0, IntMinus(IntLiteral(-1), IntIndexOf(_arg_0, StrLiteral("/"), IntLiteral(0)), IntLiteral(-1)))), IntLiteral(0), IntLiteral(1)))); print("Size_321: ", programObject321.size)
    # program322 = concat(concat(0.IntToStr(), _arg_0.CharAt(1)), concat("/", _arg_0.Substr(_arg_0.IndexOf((1 + 1).IntToStr()),_arg_0.Length())))
    # programObject322 = StrConcat(StrConcat(StrIntToStr(IntLiteral(0)), StrCharAt(_arg_0, IntLiteral(1))), StrConcat(StrLiteral("/"), StrSubstr(_arg_0, IntIndexOf(_arg_0, StrIntToStr(IntPlus(IntLiteral(1), IntLiteral(1))), IntLength(_arg_0))))); print("Size_322: ", programObject322.size)
    # programObject322 = StrConcat(StrConcat(StrConcat(StrIntToStr(IntLiteral(0)), StrCharAt(_arg_0, IntLiteral(1))), StrLiteral("/")), StrSubstr(_arg_0, IntIndexOf(_arg_0, StrConcat(StrIntToStr(IntPlus(IntLiteral(1), IntLiteral(1))), StrLiteral("."))), IntLength(_arg_0)))); print("Size_322: ", programObject322.size)
    # program323 = concat(col2.replace(concat(",", concat(" ", "USA")), ","), concat(" ", "USA")).replace("New York", "CT").replace("New York", "NY").replace("CT", "New York").replace(concat(col2.replace(concat(",", concat(" ", "USA")), ","), concat(" ", "USA")), (if"New York".Prefixof(col2) then col2 else concat(col2.replace(concat(",", concat(" ", "USA")), ","), concat(" ", "USA")).replace("New York", "NY"))).replace("CA", concat("CA", ",")).replace(concat(col2.replace(concat(",", concat(" ", "USA")), ","), concat(" ", "USA")), concat(col2.replace(concat(",", concat(" ", "USA")), ","), concat(" ", "USA")).replace("New York", "CT").replace("New York", "NY").replace("CT", "New York").replace(concat(col2.replace(concat(",", concat(" ", "USA")), ","), concat(" ", "USA")), (if"New York".Prefixof(col2) then col2 else concat(col2.replace(concat(",", concat(" ", "USA")), ","), concat(" ", "USA")).replace("New York", "NY"))).replace("MD", concat("MD", ",")))
    # programObject323 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrConcat(col2, StrReplace(StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrLiteral("USA"))), StrLiteral(",")), StrConcat(StrLiteral(" "), StrLiteral("USA"))), StrLiteral("New York"), StrLiteral("CT")), StrLiteral("New York"), StrLiteral("NY")), StrLiteral("CT"), StrLiteral("New York")), StrConcat(col2, StrReplace(StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrLiteral("USA"))), StrLiteral(",")), StrConcat(StrLiteral(" "), StrLiteral("USA"))), Ite(StrPrefixOf(StrLiteral("New York"), col2), col2, StrReplace(StrConcat(col2, StrReplace(StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrLiteral("USA"))), StrLiteral(",")), StrConcat(StrLiteral(" "), StrLiteral("USA")), StrLiteral("New York"), StrLiteral("NY"))), StrLiteral("CA"), StrConcat(StrLiteral("CA"), StrLiteral(","))); print("Size_323: ", programObject323.size)
    # program324 = _arg_0.replace("<", "").replace(">", "").replace("<", "").replace("<", "").replace(">", "").replace(">", "")
    programObject324 = StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("<"), StrLiteral("")), StrLiteral(">"), StrLiteral("")), StrLiteral("<"), StrLiteral("")), StrLiteral("<"), StrLiteral("")), StrLiteral(">"), StrLiteral("")), StrLiteral(">"), StrLiteral("")); print("Size_324: ", programObject324.size)
    # program325 = _arg_0.Substr(0,(_arg_0.IndexOf("1") + -1))
    programObject325 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("1"), IntLiteral(1)), IntLiteral(1))); print("Size_325: ", programObject325.size)
    # program326 = concat(_arg_0.Substr((1 - 7),_arg_0.IndexOf((_arg_0.Length() * (_arg_0.Length() - (5 % (_arg_0.Length() % 9)))).IntToStr())), (_arg_0.Length() * (_arg_0.Length() - (5 % (_arg_0.Length() % 9)))).IntToStr())
    # program327 = _arg_0.Substr((_arg_0.IndexOf(" ",5) + 1),_arg_0.IndexOf(" ",(4 * 4)))
    programObject327 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(5)), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral(" "), IntMultiply(IntLiteral(4), IntLiteral(4)))); print("Size_327: ", programObject327.size)
    # program328 = _arg_0.Substr(((1 + 1) * (_arg_0.IndexOf("/",((1 + 1) + 1)) + -1)),_arg_0.Length())
    # programObject328 = StrSubstr(_arg_0, IntMultiply(IntLiteral(1), IntMinus(IntIndexOf(_arg_0, StrLiteral("/"), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntLiteral(1)))), IntLength(_arg_0))); print("Size_328: ", programObject328.size)
    # program329 = concat(lastname, concat(",", concat(" ", concat(firstname.CharAt(0), "."))))
    programObject329 = StrConcat(_arg_1, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrLiteral("."))))); print("Size_329: ", programObject329.size)
    # program330 = concat(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).replace(_arg_0.CharAt(1), "").Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(0,_arg_0.Length()), concat(concat(_arg_0.replace(",", ""), ","), _arg_0).replace(_arg_0.CharAt(1), "").Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1)).replace(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).replace(_arg_0.CharAt(1), "").Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1), concat(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).replace(_arg_0.CharAt(1), "").Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(0,-1), concat(concat(_arg_0.replace(",", ""), ","), _arg_0).replace(_arg_0.CharAt(1), "").Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1)).replace(concat(",", concat(concat(_arg_0.replace(",", ""), ","), _arg_0).replace(_arg_0.CharAt(1), "").Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1)), "").replace(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).replace(_arg_0.CharAt(1), "").Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1), "")).replace(concat(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).replace(_arg_0.CharAt(1), "").Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(0,-1), concat(concat(_arg_0.replace(",", ""), ","), _arg_0).replace(_arg_0.CharAt(1), "").Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1)).replace(concat(",", concat(concat(_arg_0.replace(",", ""), ","), _arg_0).replace(_arg_0.CharAt(1), "").Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1)), "").replace(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).replace(_arg_0.CharAt(1), "").Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1), ""), "")
    # program331 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),_arg_0.Length())
    programObject331 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)); print("Size_331: ", programObject331.size)
    # program332 = concat(concat(firstname.CharAt(0), "."), concat(" ", lastname))
    programObject332 = StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrLiteral(".")), StrConcat(StrLiteral(" "), _arg_1)); print("Size_332: ", programObject332.size)
    # program333 = name.Substr(1,name.IndexOf(" "))
    programObject333 = StrSubstr(_arg_0, IntLiteral(1), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_333: ", programObject333.size)
    # program334 = (ifEqual(_arg_0,_arg_1) then _arg_0 else _arg_2)
    programObject334 = \
        StrIte(
            BoolEqual(_arg_0, _arg_1),
            _arg_0,
            _arg_2
        )
    print("Size_334: ", programObject334.size)
    # program335 = name.Substr(0,(0 - 3))
    programObject335 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntLiteral(0), IntLiteral(3))); print("Size_335: ", programObject335.size)
    # program336 = _arg_0.Substr((_arg_0.IndexOf("_") - 4),(_arg_0.IndexOf(".") + 4))
    programObject336 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntLiteral(4)), IntPlus(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(4))); print("Size_336: ", programObject336.size)
    # program337 = _arg_0.Substr(_arg_0.IndexOf("_"),concat(_arg_0, _arg_0).IndexOf(" ",_arg_0.IndexOf("_")))
    programObject337 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntIndexOf(StrConcat(_arg_0, _arg_0), StrLiteral(" "), IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)))); print("Size_337: ", programObject337.size)
    # program338 = _arg_0.replace("-", "")
    programObject338 = StrReplace(_arg_0, StrLiteral("-"), StrLiteral("")); print("Size_338: ", programObject338.size)
    # program339 = _arg_0.replace("that", (ifEqual("that",_arg_0) then "that" else ""))
    programObject339 = \
        StrReplace(
            _arg_0,
            StrLiteral("that"),
            StrIte(
                BoolEqual(StrLiteral("that"), _arg_0),
                StrLiteral("that"),
                StrLiteral("")
            )
        )
    print("Size_339: ", programObject339.size)
    # program340 = (ifEqual("that",_arg_0) then "that" else _arg_0.replace("that", ""))
    programObject340 = \
        StrIte(
            BoolEqual(StrLiteral("that"), _arg_0),
            StrLiteral("that"),
            StrReplace(_arg_0, StrLiteral("that"), StrLiteral(""))
        )
    print("Size_340: ", programObject340.size)
    
    # program341 = _arg_0.Substr((_arg_0.IndexOf("_") - 4),(_arg_0.IndexOf(".") + 4))
    programObject341 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntLiteral(4)), IntPlus(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(4))); print("Size_341: ", programObject341.size)
    # program342 = name.Substr(0,(0 - 3))
    programObject342 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntLiteral(0), IntLiteral(3))); print("Size_342: ", programObject342.size)
    # program343 = _arg_1.replace(_arg_1.replace(_arg_0.CharAt(1), " "), _arg_2)
    # programObject343 = StrReplace(StrReplace(_arg_1, StrCharAt(_arg_0, IntLiteral(1)), StrLiteral(" ")), _arg_2); print("Size_343: ", programObject343.size)
    # program344 = name.Substr(1,name.IndexOf(" "))
    programObject344 = StrSubstr(_arg_0, IntLiteral(1), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_344: ", programObject344.size)
    # program345 = concat(concat(concat(firstname.CharAt(0), "."), " "), lastname)
    programObject345 = StrConcat(StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrLiteral(".")), StrLiteral(" ")), _arg_1); print("Size_345: ", programObject345.size)
    # program346 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),_arg_0.Length())
    programObject346 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)); print("Size_346: ", programObject346.size)
    # program347 = _arg_0.Substr(0,concat(_arg_0, " ").IndexOf(" ",("Company".Length() + 1)))
    # programObject347 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(StrConcat(_arg_0, StrLiteral(" ")), StrLiteral(" "), IntPlus(IntLiteral("Company".size), IntLiteral(1)))); print("Size_347: ", programObject347.size)
    # program348 = _arg_0.Substr((_arg_0.IndexOf(" ",5) + 1),_arg_0.IndexOf(" ",(4 * 4)))
    programObject348 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(5)), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral(" "), IntMultiply(IntLiteral(4), IntLiteral(4)))); print("Size_348: ", programObject348.size)
    # program349 = _arg_0.Substr(((-1 + -1) * (1 - _arg_0.IndexOf("/",(1 - (-1 + -1))))),_arg_0.Length())
    programObject349 = StrSubstr(_arg_0, IntMultiply(IntMinus(IntLiteral(-1), IntLiteral(1)), IntMinus(IntLiteral(1), IntIndexOf(_arg_0, StrLiteral("/"), IntMinus(IntLiteral(1), IntMinus(IntLiteral(-1), IntLiteral(1)))))), IntLength(_arg_0)); print("Size_349: ", programObject349.size)
    # program350 = _arg_0.Substr(0,(_arg_0.IndexOf("1") + -1))
    programObject350 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("1"), IntLiteral(1)), IntLiteral(1))); print("Size_350: ", programObject350.size)
    # program351 = concat(_arg_0.Substr((1 - 7),_arg_0.IndexOf((_arg_0.Length() * (_arg_0.Length() - (5 % (_arg_0.Length() % 9)))).IntToStr())), (_arg_0.Length() * (_arg_0.Length() - (5 % (_arg_0.Length() % 9)))).IntToStr())
    # programObject351 = StrConcat(StrSubstr(_arg_0, IntMinus(IntLiteral(1), IntLiteral(7)), IntIndexOf(_arg_0, StrIntToStr(IntMultiply(_arg_0.size, IntMinus(_arg_0.size, IntModulo(IntLiteral(5), IntModulo(_arg_0.size, IntLiteral(9)))))), IntLiteral(1))), StrIntToStr(IntMultiply(_arg_0.size, IntMinus(_arg_0.size, IntModulo(IntLiteral(5), IntModulo(_arg_0.size, IntLiteral(9))))))); print("Size_351: ", programObject351.size)
    # program352 = concat(_arg_0.Substr((1 - 7),_arg_0.IndexOf((_arg_0.Length() * (_arg_0.Length() - (5 % (_arg_0.Length() % 9)))).IntToStr())), (_arg_0.Length() * (_arg_0.Length() - (5 % (_arg_0.Length() % 9)))).IntToStr())
    # programObject352 = StrConcat(StrSubstr(_arg_0, IntMinus(IntLiteral(1), IntLiteral(7)), IntIndexOf(_arg_0, StrIntToStr(IntMultiply(_arg_0.size, IntMinus(_arg_0.size, IntModulo(IntLiteral(5), IntModulo(_arg_0.size, IntLiteral(9)))))), IntLiteral(1))), StrIntToStr(IntMultiply(_arg_0.size, IntMinus(_arg_0.size, IntModulo(IntLiteral(5), IntModulo(_arg_0.size, IntLiteral(9))))))); print("Size_352: ", programObject352.size)
    # program353 = concat(concat(_arg_0.Substr((_arg_0.IndexOf(",") + 1),_arg_0.Length()), ","), _arg_0).Substr(0,_arg_0.Length())
    # programObject353 = StrConcat(StrConcat(StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(","), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)), StrLiteral(",")), _arg_0), StrLiteral(""); print("Size_353: ", programObject353.size)
    # program354 = concat(lastname, concat(",", concat(" ", concat(firstname.CharAt(0), "."))))
    programObject354 = StrConcat(_arg_1, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrLiteral("."))))); print("Size_354: ", programObject354.size)
    # program355 = _arg_0.replace(">", "").replace("<", " ").replace(",", " ").replace(",", " ")
    programObject355 = StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral(">"), StrLiteral("")), StrLiteral("<"), StrLiteral(" ")), StrLiteral(","), StrLiteral(" ")), StrLiteral(","), StrLiteral(" ")); print("Size_355: ", programObject355.size)
    # program356 = _arg_0.Substr(_arg_0.IndexOf(0.IntToStr()),_arg_0.IndexOf("<",1))
    programObject356 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrIntToStr(IntLiteral(0)), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("<"), IntLiteral(1))); print("Size_356: ", programObject356.size)
    # program357 = _arg_0.replace("-", "").replace("-", "")
    programObject357 = StrReplace(StrReplace(_arg_0, StrLiteral("-"), StrLiteral("")), StrLiteral("-"), StrLiteral("")); print("Size_357: ", programObject357.size)
    # program358 = _arg_0.Substr(0,concat(_arg_0, " ").IndexOf(" ",("Company".Length() + 1)))
    # programObject358 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(StrConcat(_arg_0, StrLiteral(" ")), StrLiteral(" "), IntPlus(IntLiteral("Company".size), IntLiteral(1)))); print("Size_358: ", programObject358.size)
    # program359 = _arg_0.Substr(0,(_arg_0.replace("US", "CAN").replace("CAN", _arg_0).Length() % (_arg_0.Length() + 1)))
    # programObject359 = StrSubstr(_arg_0, IntLiteral(0), IntModulo(IntLength(StrReplace(StrReplace(_arg_0, StrLiteral("US"), StrLiteral("CAN")), StrLiteral("CAN"), _arg_0)), IntPlus(_arg_0.size, IntLiteral(1)))); print("Size_359: ", programObject359.size)
    # program360 = _arg_1.replace(_arg_1.replace(_arg_2.lower(), " "), _arg_0)
    programObject360 = StrReplace(StrReplace(_arg_1, StrReplace(_arg_2, StrLiteral(""), StrLiteral(" ")), _arg_0), StrLiteral(""), StrLiteral(" ")); print("Size_360: ", programObject360.size)
    # program361 = name.Substr(1,name.IndexOf(" "))
    programObject361 = StrSubstr(_arg_0, IntLiteral(1), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_361: ", programObject361.size)
    # program362 = (if_arg_0.Contain(_arg_2) then _arg_0 else _arg_1)
    programObject362 = \
        StrIte(
            BoolContain(_arg_0, _arg_2),
            _arg_0,
            _arg_1
        )
    print("Size_362: ", programObject362.size)
    # program363 = name.Substr((name.IndexOf("-") - 3),name.IndexOf("-"))
    programObject363 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1)), IntLiteral(3)), IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1))); print("Size_363: ", programObject363.size)
    # program364 = concat(firstname, concat(concat(" ", lastname.CharAt(0)), "."))
    programObject364 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), StrConcat(StrCharAt(_arg_1, IntLiteral(0)), StrLiteral(".")))); print("Size_364: ", programObject364.size)
    # program365 = _arg_0.replace("-", "")
    programObject365 = StrReplace(_arg_0, StrLiteral("-"), StrLiteral("")); print("Size_365: ", programObject365.size)
    # program366 = _arg_0.Substr(_arg_0.IndexOf("_"),concat(_arg_0, _arg_0).IndexOf(" ",_arg_0.IndexOf("_")))
    programObject366 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntIndexOf(StrConcat(_arg_0, _arg_0), StrLiteral(" "), IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)))); print("Size_366: ", programObject366.size)
    # program367 = _arg_0.replace("that".lower().replace(_arg_0.lower(), ""), "")
    programObject367 = StrReplace(_arg_0, StrReplace(StrLower(StrReplace(_arg_0, _arg_0, StrLiteral(""))), StrLiteral("that"), StrLiteral("")), StrLiteral("")); print("Size_367: ", programObject367.size)
    # program368 = _arg_0.Substr(_arg_0.IndexOf("_"),concat(_arg_0, _arg_0).IndexOf(" ",_arg_0.IndexOf("_")))
    programObject368 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntIndexOf(StrConcat(_arg_0, _arg_0), StrLiteral(" "), IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)))); print("Size_368: ", programObject368.size)
    # program369 = _arg_0.replace("-", "")
    programObject369 = StrReplace(_arg_0, StrLiteral("-"), StrLiteral("")); print("Size_369: ", programObject369.size)
    # program370 = concat(firstname, concat(concat(" ", lastname.CharAt(0)), "."))
    programObject370 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), StrConcat(StrCharAt(_arg_1, IntLiteral(0)), StrLiteral(".")))); print("Size_370: ", programObject370.size)
    # program371 = name.Substr((name.IndexOf("-") - 3),name.IndexOf("-"))
    programObject371 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1)), IntLiteral(3)), IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1))); print("Size_371: ", programObject371.size)
    # program372 = (if_arg_0.Contain(_arg_2) then _arg_0 else _arg_1)
    programObject372 = \
        StrIte(
            BoolContain(_arg_0, _arg_2),
            _arg_0,
            _arg_1
        )
    print("Size_372: ", programObject372.size)
    
    # program373 = _arg_0.Substr(0,(_arg_0.replace("US", "CAN").replace("CAN", _arg_0).Length() % (_arg_0.Length() + 1)))
    # programObject373 = StrSubstr(_arg_0, IntLiteral(0), IntModulo(IntLength(StrReplace(StrReplace(_arg_0, StrLiteral("US"), StrLiteral("CAN")), StrLiteral("CAN"), _arg_0)), IntPlus(_arg_0.size, IntLiteral(1)))); print("Size_373: ", programObject373.size)
    # program374 = _arg_0.replace("-", "").replace("-", "")
    programObject374 = StrReplace(StrReplace(_arg_0, StrLiteral("-"), StrLiteral("")), StrLiteral("-"), StrLiteral("")); print("Size_374: ", programObject374.size)
    # program375 = _arg_0.Substr(0,concat(_arg_0, " ").IndexOf(" ",("Company".Length() + 1)))
    # programObject375 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(StrConcat(_arg_0, StrLiteral(" ")), StrLiteral(" "), IntPlus(IntLiteral("Company".size), IntLiteral(1)))); print("Size_375: ", programObject375.size)
    # program376 = concat(concat(_arg_0.CharAt(0), "/"), _arg_0.replace("/", "").replace(",", " ").replace(",", " ").replace("<", " ").Substr(1,-1))
    programObject376 = StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrLiteral("/")), StrSubstr(StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral("/"), StrLiteral("")), StrLiteral(","), StrLiteral(" ")), StrLiteral(","), StrLiteral(" ")), StrLiteral("<"), StrLiteral("")), IntLiteral(1), IntLiteral(-1))); print("Size_376: ", programObject376.size)
    # program377 = _arg_0.Substr(_arg_0.IndexOf(0.IntToStr()),_arg_0.IndexOf("<",1))
    # programObject377 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrIntToStr(IntLiteral(0))), IntIndexOf(_arg_0, StrLiteral("<"), IntLiteral(1))); print("Size_377: ", programObject377.size)
    # program378 = concat(lastname, concat(",", concat(" ", concat(firstname.CharAt(0), "."))))
    programObject378 = StrConcat(_arg_1, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrLiteral("."))))); print("Size_378: ", programObject378.size)
    # program379 = concat(_arg_0.replace(",", concat(concat(_arg_0, ","), _arg_0)).replace(",", " ").Substr(_arg_0.Length(),-1).replace(" ", "").Substr(0,_arg_0.Length()), _arg_0.replace(",", concat(concat(_arg_0, ","), _arg_0)).replace(",", " ").Substr(_arg_0.Length(),-1).replace(" ", "").Substr(0,_arg_0.Length()).replace(_arg_0.CharAt(0), _arg_0).CharAt(_arg_0.Length()).replace(",", "")).replace(_arg_0.replace(",", concat(concat(_arg_0, ","), _arg_0)).replace(",", " ").Substr(_arg_0.Length(),-1).replace(" ", "").Substr(0,_arg_0.Length()), _arg_0.replace(",", concat(concat(_arg_0, ","), _arg_0)).replace(",", " ").Substr(_arg_0.Length(),-1).replace(" ", "").Substr(0,_arg_0.Length()).replace(_arg_0.replace(",", concat(concat(_arg_0, ","), _arg_0)).replace(",", " ").Substr(_arg_0.Length(),-1).replace(" ", "").Substr(0,_arg_0.Length()).replace(_arg_0.CharAt(0), _arg_0).CharAt(_arg_0.Length()).replace(",", ""), ""))
    # program380 = _arg_0.Substr(0,(_arg_0.IndexOf("1") + -1))
    programObject380 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("1"), IntLiteral(1)), IntLiteral(1))); print("Size_380: ", programObject380.size)
    # program381 = _arg_0.Substr(((1 + 1) * (_arg_0.IndexOf("/",((1 + 1) + 1)) + -1)),_arg_0.Length())
    # programObject381 = StrSubstr(_arg_0, IntMultiply(IntLiteral(1), IntMinus(IntIndexOf(_arg_0, StrLiteral("/"), IntPlus(IntPlus(IntLiteral(1), IntLiteral(1)), IntLiteral(1)))), IntLength(_arg_0))); print("Size_381: ", programObject381.size)
    # program382 = _arg_0.Substr((_arg_0.IndexOf(" ",5) + 1),_arg_0.IndexOf(" ",(4 * 4)))
    programObject382 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(5)), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral(" "), IntMultiply(IntLiteral(4), IntLiteral(4)))); print("Size_382: ", programObject382.size)
    # program383 = _arg_0.Substr(((1 - _arg_0.IndexOf("/",(1 - (-1 + -1)))) * (-1 + -1)),_arg_0.Length())
    # programObject383 = StrSubstr(_arg_0, IntMultiply(IntMinus(IntLiteral(1), IntIndexOf(_arg_0, StrLiteral("/"), IntMinus(IntLiteral(1), IntMinus(IntLiteral(-1), IntLiteral(1)))))), IntLength(_arg_0)); print("Size_383: ", programObject383.size)
    # program384 = _arg_0.Substr(0,(_arg_0.IndexOf("1") + -1))
    programObject384 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("1"), IntLiteral(1)), IntLiteral(1))); print("Size_384: ", programObject384.size)
    # program385 = concat(5.IntToStr().Substr(concat(_arg_0.Substr((-1 - 9),1), _arg_0.Substr(_arg_0.IndexOf(0.IntToStr()),(((5 * 8) % _arg_0.Length()) + 3)).replace(" ", "")).StrToInt(),1), concat(_arg_0.Substr((-1 - 9),1), _arg_0.Substr(_arg_0.IndexOf(0.IntToStr()),(((5 * 8) % _arg_0.Length()) + 3)).replace(" ", "")))
    # program386 = concat(concat(firstname.CharAt(0), "."), concat(" ", lastname))
    programObject386 = StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrLiteral(".")), StrConcat(StrLiteral(" "), _arg_1)); print("Size_386: ", programObject386.size)
    # program387 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),_arg_0.Length())
    programObject387 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)); print("Size_387: ", programObject387.size)
    # program388 = _arg_0.Substr(_arg_0.IndexOf(0.IntToStr()),_arg_0.IndexOf("<",1))
    programObject388 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrIntToStr(IntLiteral(0)), IntLiteral(0)), IntIndexOf(_arg_0, StrLiteral("<"), IntLiteral(1))); print("Size_388: ", programObject388.size)
    # program389 = _arg_1.replace(_arg_1.replace(_arg_0.CharAt(1), " "), _arg_2)
    # programObject389 = StrReplace(StrReplace(_arg_1, StrCharAt(_arg_0, IntLiteral(1)), StrLiteral(" ")), _arg_2); print("Size_389: ", programObject389.size)
    # program390 = name.Substr(1,name.IndexOf(" "))
    programObject390 = StrSubstr(_arg_0, IntLiteral(1), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_390: ", programObject390.size)
    # program391 = _arg_0.Substr((_arg_0.IndexOf("_") - 4),(_arg_0.IndexOf(".") + 4))
    programObject391 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntLiteral(4)), IntPlus(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(4))); print("Size_391: ", programObject391.size)
    # program392 = name.Substr(0,(0 - 3))
    programObject392 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntLiteral(0), IntLiteral(3))); print("Size_392: ", programObject392.size)
    # program393 = name.Substr((name.IndexOf("-") - 3),name.IndexOf("-"))
    programObject393 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1)), IntLiteral(3)), IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1))); print("Size_393: ", programObject393.size)
    # program394 = concat(firstname, concat(" ", concat(lastname.CharAt(0), ".")))
    programObject394 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), StrConcat(StrCharAt(_arg_1, IntLiteral(0)), StrLiteral(".")))); print("Size_394: ", programObject394.size)
    # program395 = _arg_0.replace("that", (ifEqual("that",_arg_0) then "that" else ""))
    programObject395 = StrReplace(_arg_0, StrReplace(StrLower(StrReplace(_arg_0, _arg_0, StrLiteral(""))), StrLiteral("that"), StrLiteral("")), StrLiteral("")); print("Size_395: ", programObject395.size)
    # program396 = _arg_0.replace("that".lower().replace(_arg_0.lower(), ""), "")
    programObject396 = StrReplace(_arg_0, StrReplace(StrLower(StrReplace(_arg_0, _arg_0, StrLiteral(""))), StrLiteral("that"), StrLiteral("")), StrLiteral("")); print("Size_396: ", programObject396.size)
    # program397 = name.Substr(0,(0 - 3))
    programObject397 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntLiteral(0), IntLiteral(3))); print("Size_397: ", programObject397.size)
    # program398 = _arg_0.Substr((_arg_0.IndexOf("_") - 4),(_arg_0.IndexOf(".") + 4))
    programObject398 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntLiteral(4)), IntPlus(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(4))); print("Size_398: ", programObject398.size)
    # program399 = (if_arg_0.Contain(_arg_2) then _arg_0 else _arg_1)
    programObject399 = \
        StrIte(
            BoolContain(_arg_0, _arg_2),
            _arg_0,
            _arg_1
        )
    print("Size_399: ", programObject399.size)
    # program400 = _arg_0.Substr(0,(_arg_0.replace("US", "CAN").replace("CAN", _arg_0).Length() % (_arg_0.Length() + 1)))
    # programObject400 = StrSubstr(_arg_0, IntLiteral(0), IntModulo(IntLength(StrReplace(StrReplace(_arg_0, StrLiteral("US"), StrLiteral("CAN")), StrLiteral("CAN"), _arg_0)), IntPlus(_arg_0.size, IntLiteral(1)))); print("Size_400: ", programObject400.size)
    # program401 = name.Substr(1,name.IndexOf(" "))
    programObject401 = StrSubstr(_arg_0, IntLiteral(1), IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1))); print("Size_401: ", programObject401.size)
    # program402 = (ifEqual(_arg_0,_arg_1) then _arg_0 else _arg_2)
    programObject402 = \
        StrIte(
            BoolEqual(_arg_0, _arg_1),
            _arg_0,
            _arg_2
        )
    print("Size_402: ", programObject402.size)
    # program403 = _arg_0.replace("-", "").replace("-", "")
    programObject403 = StrReplace(StrReplace(_arg_0, StrLiteral("-"), StrLiteral("")), StrLiteral("-"), StrLiteral("")); print("Size_403: ", programObject403.size)
    # program404 = _arg_0.replace(">", "").replace("<", " ").replace(",", " ").replace(",", " ")
    programObject404 = StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral(">"), StrLiteral("")), StrLiteral("<"), StrLiteral(" ")), StrLiteral(","), StrLiteral(" ")), StrLiteral(","), StrLiteral(" ")); print("Size_404: ", programObject404.size)
    # program405 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),_arg_0.Length())
    programObject405 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)); print("Size_405: ", programObject405.size)
    # program406 = concat(concat(firstname.CharAt(0), "."), concat(" ", lastname))
    programObject406 = StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrLiteral(".")), StrConcat(StrLiteral(" "), _arg_1)); print("Size_406: ", programObject406.size)
    # program407 = _arg_0.Substr(0,(_arg_0.IndexOf("1") + -1))
    programObject407 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntIndexOf(_arg_0, StrLiteral("1"), IntLiteral(1)), IntLiteral(1))); print("Size_407: ", programObject407.size)
    # program408 = concat(_arg_0.Substr((1 - 7),_arg_0.IndexOf((_arg_0.Length() * (_arg_0.Length() - (5 % (_arg_0.Length() % 9)))).IntToStr())), (_arg_0.Length() * (_arg_0.Length() - (5 % (_arg_0.Length() % 9)))).IntToStr())
    # programObject408 = StrConcat(StrSubstr(_arg_0, IntMinus(IntLiteral(1), IntLiteral(7)), IntIndexOf(_arg_0, StrIntToStr(IntMultiply(_arg_0.size, IntMinus(_arg_0.size, IntModulo(IntLiteral(5), IntModulo(_arg_0.size, IntLiteral(9)))))), IntLiteral(1))), StrIntToStr(IntMultiply(_arg_0.size, IntMinus(_arg_0.size, IntModulo(IntLiteral(5), IntModulo(_arg_0.size, IntLiteral(9))))))); print("Size_408: ", programObject408.size)
    # program409 = _arg_0.Substr((_arg_0.IndexOf(" ",5) + 1),_arg_0.IndexOf(" ",(4 * 4)))
    programObject409 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(5)), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral(" "), IntMultiply(IntLiteral(4), IntLiteral(4)))); print("Size_409: ", programObject409.size)
    # program410 = _arg_0.Substr(((-1 + -1) * (1 - _arg_0.IndexOf("/",(1 - (-1 + -1))))),_arg_0.Length())
    programObject410 = StrSubstr(_arg_0, IntMultiply(IntMinus(IntLiteral(-1), IntLiteral(1)), IntMinus(IntLiteral(1), IntIndexOf(_arg_0, StrLiteral("/"), IntMinus(IntLiteral(1), IntMinus(IntLiteral(-1), IntLiteral(1)))))), IntLength(_arg_0)); print("Size_410: ", programObject410.size)
    # program411 = concat(concat(concat(concat(lastname, ","), " "), firstname.CharAt(0)), ".")
    # programObject411 = StrConcat(StrConcat(StrConcat(StrConcat(_arg_1, StrLiteral(",")), StrLiteral(" ")), StrCharAt(_arg_0, IntLiteral(0))), StrLiteral(".")); print("Size_411: ", programObject411.size)
    # program412 = concat(concat(_arg_0.Substr((_arg_0.IndexOf(",") + 1),_arg_0.Length()), ","), _arg_0).Substr(0,_arg_0.Length())
    # programObject412 = StrConcat(StrConcat(StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(","), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)), StrLiteral(",")), _arg_0), StrLiteral(""); print("Size_412: ", programObject412.size)
    # program413 = _arg_0.Substr((_arg_0.IndexOf(" ") + 1),_arg_0.Length())
    programObject413 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntLength(_arg_0)); print("Size_413: ", programObject413.size)
    # program414 = concat(concat(concat(firstname.CharAt(0), "."), " "), lastname)
    programObject414 = StrConcat(StrConcat(StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrLiteral(".")), StrLiteral(" ")), _arg_1); print("Size_414: ", programObject414.size)
    # program415 = _arg_0.replace("-", "").replace("-", "")
    programObject415 = StrReplace(StrReplace(_arg_0, StrLiteral("-"), StrLiteral("")), StrLiteral("-"), StrLiteral("")); print("Size_415: ", programObject415.size)
    # program416 = _arg_0.Substr(0,concat(_arg_0, " ").IndexOf(" ",("Company".Length() + 1)))
    # programObject416 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(StrConcat(_arg_0, StrLiteral(" ")), StrLiteral(" "), IntPlus(IntLiteral("Company".size), IntLiteral(1)))); print("Size_416: ", programObject416.size)
    # program417 = _arg_0.replace(">", "").replace(",", " ").replace(",", " ").replace("<", " ")
    programObject417 = StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral(">"), StrLiteral("")), StrLiteral(","), StrLiteral(" ")), StrLiteral(","), StrLiteral(" ")), StrLiteral("<"), StrLiteral(" ")); print("Size_417: ", programObject417.size)
    # program418 = _arg_0.Substr(_arg_0.IndexOf(0.IntToStr()),_arg_0.IndexOf("<",1))
    programObject418 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrIntToStr(IntLiteral(0)), IntLiteral(0)), IntIndexOf(_arg_0, StrLiteral("<"), IntLiteral(1))); print("Size_418: ", programObject418.size)
    # program419 = _arg_0.Substr(0,(_arg_0.replace("US", "CAN").replace("CAN", _arg_0).Length() % (_arg_0.Length() + 1)))
    # programObject419 = StrSubstr(_arg_0, IntLiteral(0), IntModulo(IntLength(StrReplace(StrReplace(_arg_0, StrLiteral("US"), StrLiteral("CAN")), StrLiteral("CAN"), _arg_0)), IntPlus(_arg_0.size, IntLiteral(1)))); print("Size_419: ", programObject419.size)
    # program420 = (if_arg_0.Contain(_arg_2) then _arg_0 else _arg_1)
    programObject420 = \
        StrIte(
            BoolContain(_arg_0, _arg_2),
            _arg_0,
            _arg_1
        )
    print("Size_420: ", programObject420.size)
    # program421 = name.Substr(0,(0 - 3))
    programObject421 = StrSubstr(_arg_0, IntLiteral(0), IntMinus(IntLiteral(0), IntLiteral(3))); print("Size_421: ", programObject421.size)
    # program422 = _arg_0.Substr((_arg_0.IndexOf("_") - 4),(_arg_0.IndexOf(".") + 4))
    programObject422 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntLiteral(4)), IntPlus(IntIndexOf(_arg_0, StrLiteral("."), IntLiteral(1)), IntLiteral(4))); print("Size_422: ", programObject422.size)
    # program423 = concat(firstname, concat(" ", concat(lastname.CharAt(0), ".")))
    programObject423 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), StrConcat(StrCharAt(_arg_1, IntLiteral(0)), StrLiteral(".")))); print("Size_423: ", programObject423.size)
    # program424 = name.Substr((name.IndexOf("-") - 3),name.IndexOf("-"))
    programObject424 = StrSubstr(_arg_0, IntMinus(IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1)), IntLiteral(3)), IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1))); print("Size_424: ", programObject424.size)
    # program425 = _arg_0.Substr(_arg_0.IndexOf("_"),concat(_arg_0, _arg_0).IndexOf(" ",_arg_0.IndexOf("_")))
    programObject425 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntIndexOf(StrConcat(_arg_0, _arg_0), StrLiteral(" "), IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)))); print("Size_425: ", programObject425.size)
    # program426 = _arg_0.replace("-", "")
    programObject426 = StrReplace(_arg_0, StrLiteral("-"), StrLiteral("")); print("Size_426: ", programObject426.size)
    # program427 = _arg_0.replace("-", "")
    programObject427 = StrReplace(_arg_0, StrLiteral("-"), StrLiteral("")); print("Size_427: ", programObject427.size)
    # program428 = _arg_0.Substr(_arg_0.IndexOf("_"),concat(_arg_0, _arg_0).IndexOf(" ",_arg_0.IndexOf("_")))
    programObject428 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)), IntIndexOf(StrConcat(_arg_0, _arg_0), StrLiteral(" "), IntIndexOf(_arg_0, StrLiteral("_"), IntLiteral(1)))); print("Size_428: ", programObject428.size)
    # program429 = name.Substr((name.IndexOf(" ") + 1),name.IndexOf("-"))
    programObject429 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(1)), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral("-"), IntLiteral(1))); print("Size_429: ", programObject429.size)
    # program430 = concat(firstname, concat(" ", concat(lastname.CharAt(0), ".")))
    programObject430 = StrConcat(_arg_0, StrConcat(StrLiteral(" "), StrConcat(StrCharAt(_arg_1, IntLiteral(0)), StrLiteral(".")))); print("Size_430: ", programObject430.size)
    # program431 = (if_arg_0.Contain(_arg_2) then _arg_0 else _arg_1)
    programObject431 = \
        StrIte(
            BoolContain(_arg_0, _arg_2),
            _arg_0,
            _arg_1
        )
    print("Size_431: ", programObject431.size)
    # program432 = _arg_0.Substr(0,(_arg_0.replace("US", "CAN").replace("CAN", _arg_0).Length() % (_arg_0.Length() + 1)))
    # programObject432 = StrSubstr(_arg_0, IntLiteral(0), IntModulo(IntLength(StrReplace(StrReplace(_arg_0, StrLiteral("US"), StrLiteral("CAN")), StrLiteral("CAN"), _arg_0)), IntPlus(_arg_0.size, IntLiteral(1)))); print("Size_432: ", programObject432.size)
    # program433 = _arg_0.replace(">", "").replace(",", " ").replace(",", " ").replace("<", " ")
    programObject433 = StrReplace(StrReplace(StrReplace(StrReplace(_arg_0, StrLiteral(">"), StrLiteral("")), StrLiteral(","), StrLiteral(" ")), StrLiteral(","), StrLiteral(" ")), StrLiteral("<"), StrLiteral(" ")); print("Size_433: ", programObject433.size)
    # program434 = _arg_0.Substr(_arg_0.IndexOf(0.IntToStr()),_arg_0.IndexOf("<",1))
    programObject434 = StrSubstr(_arg_0, IntIndexOf(_arg_0, StrIntToStr(IntLiteral(0)), IntLiteral(0)), IntIndexOf(_arg_0, StrLiteral("<"), IntLiteral(1))); print("Size_434: ", programObject434.size)
    # program435 = _arg_0.replace("-", "").replace("-", "")
    programObject435 = StrReplace(StrReplace(_arg_0, StrLiteral("-"), StrLiteral("")), StrLiteral("-"), StrLiteral("")); print("Size_435: ", programObject435.size)
    # program436 = _arg_0.Substr(0,concat(_arg_0, " ").IndexOf(" ",("Company".Length() + 1)))
    # programObject436 = StrSubstr(_arg_0, IntLiteral(0), IntIndexOf(StrConcat(_arg_0, StrLiteral(" ")), StrLiteral(" "), IntPlus(IntLiteral("Company".size), IntLiteral(1)))); print("Size_436: ", programObject436.size)
    # program437 = _arg_0.Substr((_arg_0.IndexOf(" ",5) + 1),_arg_0.IndexOf(" ",(4 * 4)))
    programObject437 = StrSubstr(_arg_0, IntPlus(IntIndexOf(_arg_0, StrLiteral(" "), IntLiteral(5)), IntLiteral(1)), IntIndexOf(_arg_0, StrLiteral(" "), IntMultiply(IntLiteral(4), IntLiteral(4)))); print("Size_437: ", programObject437.size)
    # program438 = (ifconcat(concat(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1), ",").Substr(1,-1), (if",".SuffixOf(concat(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1), ",").Substr(1,-1).Substr(1,-1)) then concat(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1), ",").Substr(1,-1).Substr(1,-1).Substr(0,-1) else concat(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1), ",").Substr(1,-1))).Contain(_arg_0) then (if",".SuffixOf(concat(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1), ",").Substr(1,-1).Substr(1,-1)) then concat(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1), ",").Substr(1,-1).Substr(0,-1).Substr(0,-1) else concat(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1), ",").Substr(1,-1)) else (if",".SuffixOf(concat(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1), ",").Substr(1,-1).Substr(1,-1)) then concat(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1), ",").Substr(1,-1).Substr(1,-1).Substr(0,-1) else concat(concat(concat(_arg_0.replace(",", ""), ","), _arg_0).Substr(1,-1).Substr(1,-1).Substr(1,-1).Substr(1,-1), ",").Substr(1,-1)))
    # program439 = concat(lastname, concat(",", concat(" ", concat(firstname.CharAt(0), "."))))
    programObject439 = StrConcat(_arg_1, StrConcat(StrLiteral(","), StrConcat(StrLiteral(" "), StrConcat(StrCharAt(_arg_0, IntLiteral(0)), StrLiteral("."))))); print("Size_439: ", programObject439.size)
