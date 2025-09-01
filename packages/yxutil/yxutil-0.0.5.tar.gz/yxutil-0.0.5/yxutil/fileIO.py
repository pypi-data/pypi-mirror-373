import re
import csv
import gzip
import pandas as pd
import numpy as np
from collections import OrderedDict
import hashlib

csv.field_size_limit(100000000)


def tsv_file_parse(file_name, key_col=0, fields="all", delimiter="\t", prefix="ID_", ignore_prefix=r'^#'):
    """
    This func can parse tsv-like file to dict.
    :param file_name:   path for file
    :param key_col:     which column should be key for output dict
    :param fields:      which column should be value for output dict, field can be "all" or given
                        column like "1,2,3" or "3,4,1"
    :param delimiter:         separator for tsv-like file
    :return: a dict with given key and value, value is a list for column chosen.
    """
    dict_output = OrderedDict()
    num = 0

    with open(file_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=delimiter, quotechar='"')
        for info in spamreader:
            if len(info) == 0 or re.match(ignore_prefix, info[0]):
                continue
            if fields == "all":
                record = info
            else:
                field_list = fields.split(",")
                record = []
                for field in field_list:
                    record.append(info[int(field) - 1])

            record = tuple(record)

            if key_col == 0:
                dict_output[prefix + str(num)] = record
            else:
                dict_output[info[key_col - 1]] = record
            num = num + 1

    return dict_output


def tsv_file_parse_big(file_name, key_col=None, fields="all", delimiter="\t", prefix="ID_", gzip_flag=False,
                       fieldnames=None, ignore_prefix=r'^#'):
    """
    This func can parse tsv-like file to dict.
    :param file_name:   path for file
    :param key_col:     which column should be key for output dict
    :param fields:      which column should be value for output dict, field can be "all" or given
                        column like list("A","B","C")
    :param delimiter:         separator for tsv-like file
    :param prefix:      When key_col is None, we will get key as prefix write
    :param gzip_flag:   If this is a .gz file
    :param fieldnames:  if tsv file don't have title line, you should give it by list
    :return: a dict with given key and value, value is a list for column chosen.
    """
    # dict_output = OrderedDict()
    num = 0

    if gzip_flag is True:
        csvfile = gzip.open(file_name, 'rt')
    else:
        csvfile = open(file_name, 'r', newline='')

    spamreader = csv.DictReader(
        csvfile, delimiter=delimiter, quotechar='"', fieldnames=fieldnames)
    for info in spamreader:
        if len(info) == 0 or re.match(ignore_prefix, info[fieldnames[0]]):
            continue
        if fields == "all":
            record = info
        else:
            field_list = fields
            record = {}
            for i in field_list:
                record[i] = info[i]

        if key_col is None:
            ID_tmp = prefix + str(num)
        else:
            ID_tmp = info[key_col]
        num = num + 1

        # dict_output[ID_tmp] = OrderedDict.fromkeys(record)
        output_dir = OrderedDict.fromkeys(record)
        for keys in record:
            values = record[keys]
            output_dir[keys] = values
            # dict_output[ID_tmp][keys] = values

        yield output_dir

    csvfile.close()

    # return dict_output


def tsv_file_dict_parse(file_name, key_col=None, fields="all", delimiter="\t", prefix="ID_", gzip_flag=False,
                        fieldnames=None, ignore_head_num=0, ignore_prefix=r'^#'):
    """
    This func can parse tsv-like file to dict.
    :param file_name:   path for file
    :param key_col:     which column should be key for output dict
    :param fields:      which column should be value for output dict, field can be "all" or given
                        column like list("A","B","C")
    :param delimiter:         separator for tsv-like file
    :param prefix:      When key_col is None, we will get key as prefix write
    :param gzip_flag:   If this is a .gz file
    :param fieldnames:  if tsv file don't have title line, you should give it by list
    :return: a dict with given key and value, value is a list for column chosen.
    """
    dict_output = OrderedDict()
    num = 0

    if gzip_flag is True:
        csvfile = gzip.open(file_name, 'rt')
    else:
        csvfile = open(file_name, 'r', newline='')

    for i in range(0, ignore_head_num):
        next(csvfile)

    spamreader = csv.DictReader(
        csvfile, delimiter=delimiter, quotechar='"', fieldnames=fieldnames)
    for info in spamreader:
        if len(info) == 0 or re.match(ignore_prefix, info[spamreader.fieldnames[0]]):
            continue
        if fields == "all":
            record = info
        else:
            field_list = fields
            record = {}
            for i in field_list:
                record[i] = info[i]

        if key_col is None:
            ID_tmp = prefix + str(num)
        else:
            ID_tmp = info[key_col]
        num = num + 1

        dict_output[ID_tmp] = OrderedDict.fromkeys(record)
        for keys in record:
            values = record[keys]
            dict_output[ID_tmp][keys] = values

    csvfile.close()

    return dict_output


def tsv_file_dict_parse_big(file_name, key_col=None, fields="all", delimiter="\t", prefix="ID_", gzip_flag=False,
                            fieldnames=None, ignore_head_num=0, ignore_prefix=r'^#'):
    """
    This func can parse tsv-like file to dict.
    :param file_name:   path for file
    :param key_col:     which column should be key for output dict
    :param fields:      which column should be value for output dict, field can be "all" or given
                        column like list("A","B","C")
    :param delimiter:         separator for tsv-like file
    :param prefix:      When key_col is None, we will get key as prefix write
    :param gzip_flag:   If this is a .gz file
    :param fieldnames:  if tsv file don't have title line, you should give it by list
    :return: a dict with given key and value, value is a list for column chosen.
    """
    num = 0

    if gzip_flag is True:
        csvfile = gzip.open(file_name, 'rt')
    else:
        csvfile = open(file_name, 'r', newline='')

    for i in range(0, ignore_head_num):
        next(csvfile)

    spamreader = csv.DictReader(
        csvfile, delimiter=delimiter, quotechar='"', fieldnames=fieldnames)
    for info in spamreader:
        if len(info) == 0 or re.match(ignore_prefix, info[spamreader.fieldnames[0]]):
            continue
        if fields == "all":
            record = info
        else:
            field_list = fields
            record = {}
            for i in field_list:
                record[i] = info[i]

        if key_col is None:
            ID_tmp = prefix + str(num)
        else:
            ID_tmp = info[key_col]
        num = num + 1

        tmp_dict = OrderedDict.fromkeys(record)
        for keys in record:
            values = record[keys]
            tmp_dict[keys] = values

        yield (ID_tmp, tmp_dict)

    csvfile.close()


def read_list_file(file_name, ignore_prefix=r'^#', ignore_head=0):
    output_list = []
    with open(file_name, "r") as f:
        num = 0
        for each_line in f:
            num += 1
            if re.match(ignore_prefix, each_line):
                continue
            each_line = re.sub(r'\n', '', each_line)
            if each_line.strip() == '':
                continue
            if num <= ignore_head:
                continue
            output_list.append(each_line)
    return output_list


def write_list_file(input_list, file_name):
    with open(file_name, "w") as f:
        for i in input_list:
            f.write(str(i) + "\n")
    return file_name


def excel_file_parse(file_name, key_col=None, prefix="ID_", fields="all", str_flag=True):
    df = pd.read_excel(file_name)
    if str_flag is True:
        df = df.astype(str)
    colname = list(df.columns)
    spamreader = df.values
    dict_output = {}
    num = 0
    for info in spamreader:
        if fields == "all":
            field_list = colname
        else:
            field_list = fields
        record = {}
        for i in field_list:
            record[i] = info[colname.index(i)]

        if key_col is None:
            ID_tmp = prefix + str(num)
        else:
            ID_tmp = info[key_col]
        num = num + 1

        dict_output[ID_tmp] = {}
        for keys in record:
            values = record[keys]
            dict_output[ID_tmp][keys] = values
    return dict_output, colname


def read_matrix_file(matrix_file, delimiter="\t"):
    tsv_info = tsv_file_dict_parse(matrix_file, delimiter=delimiter)

    row_key = list(tsv_info['ID_0'].keys())[0]
    col_list = list(tsv_info['ID_0'].keys())[1:]
    row_list = []

    matrix = []
    for i in tsv_info:
        data = tsv_info[i]
        row_list.append(data[row_key])
        r = []
        for c in col_list:
            r.append(float(data[c]))
        matrix.append(r)

    return np.array(matrix), col_list, row_list


def write_matrix_file(matrix, col_list, row_list, output_file):
    with open(output_file, 'w') as f:
        f.write("\t"+"\t".join(col_list)+"\n")
        for i in range(len(row_list)):
            g_id = row_list[i]
            f.write(g_id + "\t" + "\t".join([str(j)
                                             for j in matrix[i]]) + "\n")


def get_file_md5(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()
