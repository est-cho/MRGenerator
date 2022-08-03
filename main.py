import argparse
import generator
import converter
import data_parser
import evaluator
import time

DEFAULT_INIT_MR = "initial_mrs/initial_1.xml"

CONFIG_1 = '0.6_1.2_180'
CONFIG_2 = '0.5_0.6_140'
CONFIG_3 = '0.8_1.8_200'


DEFAULT_CONST_FILE = "data/constants.csv"
DEFAULT_LOG_PATH = "data/"
DEFAULT_OUTPUT_PATH = "output/"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MRGenerator')
    parser.add_argument('-i', '--initial', required=False)  # initial MR
    parser.add_argument('-d', '--data-path', required=False)  # field experiment data
    parser.add_argument('-c', '--constants', required=False)  # constants

    args = parser.parse_args()

    initial_mr_file = args.initial
    data_path = args.data_path
    constant_file = args.constants

    if args.initial is None:
        initial_mr_file = DEFAULT_INIT_MR

    if args.data_path is None:
        data_path = DEFAULT_LOG_PATH

    if args.constants is None:
        constant_file = DEFAULT_CONST_FILE

    i_mr = converter.parse_mr_xml(initial_mr_file)[0]

    constants = data_parser.read_constants(constant_file)

    idx = 0
    for i in range(5):
        start_time = time.time()
        print(i, ': Searching', end='')
        idx += 1
        out_file = DEFAULT_OUTPUT_PATH + 'init_5-1_' + str(idx) + ".csv"

        file_list = data_parser.get_filenames_from_path(DEFAULT_LOG_PATH)
        fd = data_parser.read_field_data_file(file_list[0])

        sum_tp, sum_tn, all_score, score_dict = evaluator.calculate_score(i_mr, file_list, constants, 0, True)
        initial_mr_analysis = i_mr, sum_tp, sum_tn, all_score, score_dict

        gen_mrs_analyses = generator.evolve(i_mr, file_list, constants)
        end_time = time.time()
        print('Duration: ', end_time-start_time)
        converter.write_mr_to_csv(initial_mr_analysis, gen_mrs_analyses, generator.get_ga_params(), fd, constants, out_file)
