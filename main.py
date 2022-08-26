import argparse
import generator
import converter
import data_parser
import evaluator
import time
import os

NUM_INIT_MR = 1
CONFIG_1 = '0.6_1.2_180'
CONFIG_2 = '0.5_0.6_140'
CONFIG_3 = '0.8_1.8_200'
CONFIGS = [CONFIG_1, CONFIG_2, CONFIG_3]

DEFAULT_INIT_MR = "initial_mrs/initial_" + str(NUM_INIT_MR) + ".xml"
DEFAULT_CONFIG = CONFIGS[NUM_INIT_MR-1]

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
        data_path = DEFAULT_LOG_PATH + DEFAULT_CONFIG + "/"

    if args.constants is None:
        constant_file = DEFAULT_CONST_FILE

    i_mr = converter.parse_mr_xml(initial_mr_file)[0]

    constants = data_parser.read_constants(constant_file)
    file_list = data_parser.get_filenames_from_path(data_path)
    fdd = data_parser.read_field_data_file(file_list[0])     # for retrieving data headers

    output_path = DEFAULT_OUTPUT_PATH + "config_" + DEFAULT_CONFIG
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    # Separate training and test data for one conifg
    training_data = file_list[:30]
    test_data = file_list[30:]

    idx = 0
    for i in range(1):
        start_time = time.time()
        print(i, ': Searching', end='')
        idx += 1
        out_file = output_path + '/init_' + str(NUM_INIT_MR) + "_tr_" + \
                   time.strftime('%m-%d_%H:%M:%S', time.localtime(start_time)) + ".csv"
        test_out_file = output_path + '/init_' + str(NUM_INIT_MR) + "_test_" + \
                        time.strftime('%m-%d_%H:%M:%S', time.localtime(start_time)) + ".csv"

        sum_tp, sum_tn, all_score, score_dict = evaluator.calculate_score(i_mr, training_data, constants, 0, True)
        initial_mr_analysis = i_mr, sum_tp, sum_tn, all_score, score_dict

        gen_mrs = generator.evolve(i_mr, training_data, constants)

        end_time = time.time()
        print('Duration: ', end_time-start_time)
        gen_mrs_analyses = evaluator.get_pop_detail(gen_mrs, training_data, constants, 1)
        converter.write_mr_to_csv(initial_mr_analysis, gen_mrs_analyses, generator.get_ga_params(), fdd, constants,
                                  out_file)

        # Evaluate against test data
        test_sum_tp, test_sum_tn, test_all_score, test_score_dict = evaluator.calculate_score(i_mr, test_data,
                                                                                              constants, 0, True)
        test_initial_mr_analysis = i_mr, test_sum_tp, test_sum_tn, test_all_score, test_score_dict
        test_gen_mrs_analyses = evaluator.get_pop_detail(gen_mrs, test_data, constants, 1)
        converter.write_mr_to_csv(test_initial_mr_analysis, test_gen_mrs_analyses, generator.get_ga_params(), fdd,
                                  constants, test_out_file)
