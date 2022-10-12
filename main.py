import argparse
import generator
import converter
import data_parser
import evaluator
import time
import os

USE_SINGLE_CONFIG = True
TRAINING_DATA_SIZE = 35

# NUM_INIT_MR = 1
INIT_MRS = [1, 2, 3, 4]

# TRAINING_CONFIG = 1
# CONFIG_1 = '0.6_1.2_180'
# CONFIG_2 = '0.5_0.6_140'
# CONFIG_3 = '0.8_1.8_200'
# CONFIGS = [CONFIG_1, CONFIG_2, CONFIG_3]

DEFAULT_INIT_MR_PATH = "initial_mrs/"
# DEFAULT_CONFIG = CONFIGS[TRAINING_CONFIG-1]

DEFAULT_CONST_FILE = "data/constants.csv"
DEFAULT_LOG_PATH = "data/"
DEFAULT_OUTPUT_PATH = "output/"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MRGenerator')
    # parser.add_argument('-i', '--initial', required=False)  # initial MR
    parser.add_argument('-d', '--data-path', required=False)  # field experiment data
    parser.add_argument('-c', '--constants', required=False)  # constants

    args = parser.parse_args()

    # initial_mr_file = args.initial
    data_path = args.data_path
    constant_file = args.constants

    # if args.initial is None:
    #     initial_mr_file = DEFAULT_INIT_MR_PATH + "initial_" + str(NUM_INIT_MR) + ".xml"

    if args.data_path is None:
        data_path = DEFAULT_LOG_PATH
        # data_path = DEFAULT_LOG_PATH + DEFAULT_CONFIG + "/"

    if args.constants is None:
        constant_file = DEFAULT_CONST_FILE

    constants = data_parser.read_constants(constant_file)

    x_config = [0.4, 0.5, 0.6, 0.7, 0.8]
    y_config = [0.6, 0.9, 1.2, 1.5, 1.8]
    z_config = [140, 160, 180, 200, 220]

    configs = []
    for x in x_config:
        for y in y_config:
            for z in z_config:
                configs.append(str(x) + "_" + str(y) + "_" + str(z))

    for config in configs:
        file_list = data_parser.get_filenames_from_path(data_path, config)
        fdd = data_parser.read_field_data_file(file_list[0])     # for retrieving data headers

        output_path = DEFAULT_OUTPUT_PATH + "config_" + config
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        training_data = file_list[:TRAINING_DATA_SIZE]
        test_data = file_list[TRAINING_DATA_SIZE:]
        # if USE_SINGLE_CONFIG:
        #     # Separate training and test data for one configuration
        #
        # else:
        #     # Use a different configs as the target system
        #     training_data = file_list
        #     test_data_list = {}
        #     for i, c in enumerate(CONFIGS):
        #         if i == TRAINING_CONFIG-1:
        #             continue
        #         else:
        #             test_data_list[c] = data_parser.get_filenames_from_path(DEFAULT_LOG_PATH + c + "/")
        #
        # print('training_data_len: ', len(training_data))

        print('Configuration: ', config)
        for i, mr in enumerate(INIT_MRS):
            initial_mr_file = DEFAULT_INIT_MR_PATH + "initial_" + str(mr) + ".xml"
            i_mr = converter.parse_mr_xml(initial_mr_file)[0]

            start_time = time.time()
            print(mr, ': Searching', end='')
            out_file = output_path + '/init_' + str(mr) + "_tr_" + time.strftime('%m-%d_%H-%M-%S', time.localtime(start_time)) + ".csv"

            sum_tp, sum_tn, all_score, score_dict = evaluator.calculate_score(i_mr, training_data, constants, 0, True)
            initial_mr_analysis = i_mr, sum_tp, sum_tn, all_score, score_dict

            gen_mrs = generator.evolve(i_mr, training_data, constants)

            end_time = time.time()
            print('Duration: ', end_time-start_time)

            gen_mrs_analyses = evaluator.get_pop_detail(gen_mrs, training_data, constants, 1)
            converter.write_mr_to_csv(initial_mr_analysis, gen_mrs_analyses, generator.get_ga_params(), fdd, constants,
                                      out_file)

            # Evaluate against test data
            test_out_file = output_path + '/init_' + str(mr) + "_test_" + time.strftime('%m-%d_%H-%M-%S', time.localtime(start_time)) + ".csv"
            test_sum_tp, test_sum_tn, test_all_score, test_score_dict = evaluator.calculate_score(i_mr, test_data,
                                                                                                  constants, 0, True)
            test_initial_mr_analysis = i_mr, test_sum_tp, test_sum_tn, test_all_score, test_score_dict
            test_gen_mrs_analyses = evaluator.get_pop_detail(gen_mrs, test_data, constants, 1)
            converter.write_mr_to_csv(test_initial_mr_analysis, test_gen_mrs_analyses, generator.get_ga_params(), fdd,
                                      constants, test_out_file)
            # if USE_SINGLE_CONFIG:
            #     test_out_file = output_path + '/init_' + str(mr) + "_test_" + \
            #                     time.strftime('%m-%d_%H-%M-%S', time.localtime(start_time)) + ".csv"
            #     test_sum_tp, test_sum_tn, test_all_score, test_score_dict = evaluator.calculate_score(i_mr, test_data,
            #                                                                                           constants, 0, True)
            #     test_initial_mr_analysis = i_mr, test_sum_tp, test_sum_tn, test_all_score, test_score_dict
            #     test_gen_mrs_analyses = evaluator.get_pop_detail(gen_mrs, test_data, constants, 1)
            #     converter.write_mr_to_csv(test_initial_mr_analysis, test_gen_mrs_analyses, generator.get_ga_params(), fdd,
            #                               constants, test_out_file)
            # else:
            #     for config, test_data in test_data_list.items():
            #         test_out_file = output_path + '/init_' + str(mr) + "_test_" + config + "_" +\
            #                         time.strftime('%m-%d_%H-%M-%S', time.localtime(start_time)) + ".csv"
            #         test_sum_tp, test_sum_tn, test_all_score, test_score_dict = evaluator.calculate_score(i_mr, test_data,
            #                                                                                               constants, 0, True)
            #         test_initial_mr_analysis = i_mr, test_sum_tp, test_sum_tn, test_all_score, test_score_dict
            #         test_gen_mrs_analyses = evaluator.get_pop_detail(gen_mrs, test_data, constants, 1)
            #         converter.write_mr_to_csv(test_initial_mr_analysis, test_gen_mrs_analyses, generator.get_ga_params(), fdd,
            #                                   constants, test_out_file)
        break
