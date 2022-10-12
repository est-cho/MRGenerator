import csv
import glob

VAL_FIELD_TYPE = ['color', 'angle', 'distance', 'speed']


def get_filenames_from_path(data_path, config):
    return glob.glob(data_path + "log_" + config + "*.csv")


def read_field_data_path(data_path):
    field_data_dict = {}
    data_files = glob.glob(data_path + "log*.csv")
    for f in data_files:
        field_data_dict[f] = read_field_data_file(f)
    return field_data_dict


def read_field_data_file(data_file):
    file = open(data_file, 'r', encoding='utf-8-sig')
    data = csv.reader(file)

    var_header = []
    var_header_index = []

    for i, vh in enumerate(next(data)):
        if vh and vh.strip().lower() in VAL_FIELD_TYPE:
            var_header.append(vh.strip().lower())
            var_header_index.append(i)

    var_data = [[] for i in range(len(var_header))]

    for (j, line) in enumerate(data):
        cnt = 0
        for i in range(len(line)):
            if i in var_header_index:
                var_data[cnt].append(float(line[i]))
                cnt += 1

    field_data_dict = {}
    for (i, vh) in enumerate(var_header):
        field_data_dict[vh] = var_data[i]

    return field_data_dict


def read_constants(constant_file):
    file = open(constant_file, 'r', encoding='utf-8-sig')
    data = csv.reader(file)

    const_header = next(data)
    const_values = [float(c) for c in next(data)]

    const_dict = dict(zip(const_header, const_values))

    return const_dict
