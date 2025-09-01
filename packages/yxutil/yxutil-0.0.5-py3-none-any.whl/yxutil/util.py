import configparser
import logging
import time
import os
import pickle
import codecs
from operator import attrgetter
from collections import OrderedDict
import math
import json

__author__ = 'Yuxing Xu'


def printer_list(list_input, sep="\t", head="", wrap_num=None):
    """
    make a list to a string with a given sep chara and head
    :param list_input: list you give me
    :param sep: Split character like "," or "\t"
    :param head: head for the output string
    :return: string
    """
    printer = head
    num = 0

    for i in list_input:
        printer = printer + str(i) + sep
        num = num + 1
        if wrap_num:
            if num % wrap_num == 0:
                printer = printer + "\n"

    printer = printer.rstrip(sep)
    return printer


def mulit_sort(xs, specs):
    """
    class Student:
        def __init__(self, name, grade, age):
            self.name = name
            self.grade = grade
            self.age = age
        def __repr__(self):
            return repr((self.name, self.grade, self.age))

    student_objects = [
        Student('john', 'A', 15),
        Student('jane', 'B', 12),
        Student('dave', 'B', 10),
    ]

    multisort(list(student_objects), (('grade', True), ('age', False)))
    """
    for key, reverse in reversed(specs):
        xs.sort(key=attrgetter(key), reverse=reverse)
    return xs


def log_print(print_string):
    time_tmp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print("%s\t\t\t%s" % (time_tmp, print_string))


def logging_init(program_name, log_file=None, log_level=logging.DEBUG, console_level=logging.ERROR):
    # create logger with 'program_name'
    logger = logging.getLogger(program_name)
    logger.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if not log_file is None:
        # create file handler which logs even debug messages
        fh = logging.FileHandler(log_file)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(console_level)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)

    return logger


def type_check(p_name, p_value, parameter_type_dict):
    if parameter_type_dict is None or p_name not in parameter_type_dict:
        return p_name, p_value
    else:
        if parameter_type_dict[p_name] == 'str':
            return p_name, str(p_value)
        elif parameter_type_dict[p_name] == 'int':
            return p_name, int(p_value)
        elif parameter_type_dict[p_name] == 'float':
            return p_name, float(p_value)
        elif parameter_type_dict[p_name] == 'bool':
            return p_name, bool(p_value)
        else:
            raise ValueError('Unknown type %s' % parameter_type_dict[p_name])


def configure_parser(arg_obj, defaults_config_file=None, config_file=None, parameter_type_dict=None,
                     parameter_parser_block=None):
    """
    config_file should be ini file

    [Simple Values]
    key=value
    spaces in keys=allowed
    spaces in values=allowed as well
    spaces around the delimiter = obviously
    you can also use : to delimit keys from values

    [All Values Are Strings]
    values like this: 1000000
    or this: 3.14159265359
    are they treated as numbers? : no
    integers, floats and booleans are held as: strings
    can use the API to get converted values directly: true

    [Multiline Values]
    chorus: I'm a lumberjack, and I'm okay
        I sleep all night and I work all day

    [No Values]
    key_without_value
    empty string value here =

    [You can use comments]
    # like this
    ; or this

    # By default only in an empty line.
    # Inline comments can be harmful because they prevent users
    # from using the delimiting characters as parts of values.
    # That being said, this can be customized.

        [Sections Can Be Indented]
            can_values_be_as_well = True
            does_that_mean_anything_special = False
            purpose = formatting for readability
            multiline_values = are
                handled just fine as
                long as they are indented
                deeper than the first line
                of a value
            # Did I mention we can indent comments, too?

        :param arg_obj:

    args

    :param parameter_type_dict:

    parameter_type_dict = {"reference_genome": "str",
                       "work_dir": "str",
                       "db_file_fnf": "str",
                       "speci_tree_file": "str",
                       "taxonomy_dir": "str",
                       "target_speci": "str",
                       "prominence": "int",
                       "gap_limit": "int",
                       "min_ranges": "int",
                       "query_step": "int",
                       "query_length": "int",
                       "subseq_kmer_frequencies_thre": "int",
                       "threshold_node_level": "str",
                       "permutation_round": "int",
                       "seed": "int",
                       "p_value_thre": "float",
                       "evalue": "float",
                       "num_threads": "int"
                       }

    :param parameter_parser_block:

    """

    output_cfg_dict = {}

    # read defaults config
    if defaults_config_file is not None:
        def_cfg = configparser.ConfigParser()
        def_cfg.read(defaults_config_file)

        for cfg_block in def_cfg.sections():
            for key in def_cfg[cfg_block]:
                value = def_cfg[cfg_block][key]
                p_name, p_value = type_check(key, value, parameter_type_dict)
                output_cfg_dict[p_name] = p_value

    # read given config
    if config_file is not None:
        cfg = configparser.ConfigParser()
        cfg.read(config_file)

        for cfg_block in cfg.sections():
            for key in cfg[cfg_block]:
                if (parameter_parser_block is not None) and (cfg_block not in parameter_parser_block):
                    continue
                value = cfg[cfg_block][key]
                p_name, p_value = type_check(key, value, parameter_type_dict)
                # if p_name not in output_cfg_dict:
                #     raise ValueError("unknown parameter %s" % p_name)
                # else:
                #     output_cfg_dict[p_name] = p_value
                output_cfg_dict[p_name] = p_value

    # read command arg
    for p_name in output_cfg_dict:
        if hasattr(arg_obj, p_name) and (getattr(arg_obj, p_name) is not None):
            output_cfg_dict[p_name] = getattr(arg_obj, p_name)

    # output to args
    for p_name in output_cfg_dict:
        setattr(arg_obj, p_name, output_cfg_dict[p_name])

    return arg_obj


def json_dump(save_object, output_json_file):
    try:
        OUT = open(output_json_file, 'w')
        json.dump(save_object, OUT)
        OUT.close()
        return output_json_file
    except:
        raise ValueError("Failed to write %s" % output_json_file)
    

def json_load(input_json_file):
    try:
        TEMP = open(input_json_file, 'r')
        output_object = json.load(TEMP)
        TEMP.close()
        return output_object
    except:
        raise ValueError("Failed to open %s" % input_json_file)


def pickle_dump(save_object, output_pickle_file):
    try:
        OUT = open(output_pickle_file, 'wb')
        pickle.dump(save_object, OUT)
        OUT.close()
        return output_pickle_file
    except:
        raise ValueError("Failed to write %s" % output_pickle_file)


def pickle_load(input_pickle_file):
    try:
        TEMP = open(input_pickle_file, 'rb')
        output_object = pickle.load(TEMP)
        TEMP.close()
        return output_object
    except:
        raise ValueError("Failed to open %s" % input_pickle_file)


def pickle_step(function, input_args_list, output_pickle_file):
    """
    Sometimes the result of a function may have already been run and saved, so I can try to read the result and run the function again if it doesn't work
    """

    if os.path.exists(output_pickle_file):
        try:
            TEMP = open(output_pickle_file, 'rb')
            output_object = pickle.load(TEMP)
            TEMP.close()
            return output_object
        except:
            pass
    output_object = function(*input_args_list)
    OUT = open(output_pickle_file, 'wb')
    pickle.dump(output_object, OUT)
    OUT.close()

    return output_object


def pickle_dump_obj(unpickled_obj):
    pickled = codecs.encode(pickle.dumps(unpickled_obj), "base64").decode()
    return pickled


def pickle_load_obj(pickled_string):
    unpickled_obj = pickle.loads(
        codecs.decode(pickled_string.encode(), "base64"))
    return unpickled_obj


def time_now():
    time_tmp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    return time_tmp


# dict common tools
def dict_key_value_transpose(input_list_dict):
    """
    将一个字典的key和value转置
    transpose a dict with key and value
    :param input_list_dict: a dict with key and value, value is a list
    :return: a dict with value as key and key as value
    example:
    input_list_dict = {"a": [1, 2, 3], "b": [2, 3, 4]}
    dict_key_value_transpose(input_list_dict)
    Out[1]: {1: ['a'], 2: ['a', 'b'], 3: ['a', 'b'], 4: ['b']}
    """
    dict_hash = {}
    for i in input_list_dict:
        for j in input_list_dict[i]:
            if j not in dict_hash:
                dict_hash[j] = []
            dict_hash[j].append(i)
    return dict_hash


def dict_key_value_interchange(dict_input):
    """
    将一个字典的key和value互换，value应该是一个list并且唯一
    interchange key and value, value should in list and uniq
    :param dict_input: a dict with key and value
    :return: a dict with value as key and key as value
    example:
    dict_input = {1: ['a'], 2: ['b'], 3: ['c', 'd']}
    dict_key_value_interchange(dict_input)
    Out[1]: {'a': 1, 'b': 2, 'c': 3, 'd': 3}
    """
    dict_output = {}
    for i in dict_input:
        for j in dict_input[i]:
            dict_output[j] = i

    return dict_output


def dict2class(dict_input, class_target, attribute_list, key2attr=None):
    """
    This func can trans a dict with many object which attr recorded as a list in dict value
    to a dict with many object which recorded as a given class
    :param dict_input:      As dict output from tsv_file_parse, which key is a object id and value
                            is a list that many attr are recorded with a order but no name of
                            attribute.
    :param class_target:    which class you want
    :param attribute_list:  a list including name of attributes, order is same as dict_input
                            value and length of attribute_list should short or same as value
                            of dict_input.
    :param key2attr:        if key should record as an attr in class, give me the name.
    :return:    a dict with many object which recorded as a given class.
    """
    dict_output = {}

    for i in dict_input:
        key = i
        value_list = dict_input[i]
        dict_output[i] = class_target()

        if key2attr is not None:
            setattr(dict_output[i], key2attr, key)

        for rank in range(0, len(attribute_list)):
            if rank > len(value_list) - 1:
                break
            setattr(dict_output[i], attribute_list[rank], value_list[rank])

    return dict_output


def dict_slice(target_dict, slice_used, sort_flag=False, sort_key_function=None, reverse=False):
    """
    get something in dict as slice for a list, better for a OrderedDict
    :param target_dict: a dict, if it's a OrderedDict will be better
    :param slice_used: a object from slice function output. See https://docs.python.org/3/library/functions.html#slice
    :param sort_flag: do you want to sort keys in a dict
    :param sort_key_function: key args from sorted function
    :param reverse: if reverse
    :return:
    """

    if sort_flag:
        target_dict_sorted_keys = list(
            sorted(target_dict, key=sort_key_function, reverse=reverse))
    else:
        target_dict_sorted_keys = list(target_dict.keys())

    output_dir = OrderedDict()
    for i in target_dict_sorted_keys[slice_used]:
        output_dir[i] = target_dict[i]

    return output_dir


def merge_dict(dict_list, extend_value=True):
    """
    merge some dict into one dict

    extend_value:
    if same key find in diff dict, extend value as list, if extend_value is True, all value will be list

    else, old value will be delete

    a = {1:1,2:2,3:3}
    b = {1:2,4:4,5:5}

    merge_dict([a,b])
    Out[11]: OrderedDict([(1, [1, 2]), (2, [2]), (3, [3]), (4, [4]), (5, [5])])

    merge_dict([a,b], False)
    Out[12]: OrderedDict([(1, 2), (2, 2), (3, 3), (4, 4), (5, 5)])

    """

    output_dict = OrderedDict()

    for dict_tmp in dict_list:
        for i in dict_tmp:
            if extend_value:
                if not i in output_dict:
                    output_dict[i] = []

                if isinstance(dict_tmp[i], list):
                    output_dict[i].extend(dict_tmp[i])
                else:
                    output_dict[i].append(dict_tmp[i])
            else:
                output_dict[i] = dict_tmp[i]

    return output_dict


def millify(n):
    """
    let size in byte is easy for human, 1000 base
    :param n: 100000
    :return:  100 KB
    """
    millnames = ['', ' K', ' M', ' G', ' P']

    n = float(n)
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return '{:.2f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])
