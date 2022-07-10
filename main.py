import argparse
import generator
import converter
import data_parser
import evaluator

DEFAULT_INIT_MR = "initial_mrs/initial_1.xml"

CONFIG_1 = '0.6_1.2_180'
CONFIG_2 = '0.5_0.6_140'
CONFIG_3 = '0.8_1.8_200'

# DATA_FILES = {"log_0.6_1.2_180_all_2021_12_07_03_24_43_797777.csv": CONFIG_1 + '-1',
#               "log_0.6_1.2_180_all_2021_12_04_16_15_57_356080.csv": CONFIG_1 + '-2',
#               "log_0.6_1.2_180_all_2021_12_06_04_08_45_055724.csv": CONFIG_1 + '-3',
#               "log_0.6_1.2_180_all_2021_12_06_14_02_08_022647.csv": CONFIG_1 + '-4',
#               "log_0.6_1.2_180_all_2021_12_06_14_06_58_164313.csv": CONFIG_1 + '-5',
#               "log_0.5_0.6_140_all_2021_12_05_00_55_09_474130.csv": CONFIG_2 + '-1',
#               "log_0.5_0.6_140_all_2021_12_05_01_00_16_531837.csv": CONFIG_2 + '-2',
#               "log_0.5_0.6_140_all_2021_12_05_16_05_42_678940.csv": CONFIG_2 + '-3',
#               "log_0.5_0.6_140_all_2021_12_05_16_08_14_575245.csv": CONFIG_2 + '-4',
#               "log_0.5_0.6_140_all_2021_12_07_08_47_52_511099.csv": CONFIG_2 + '-5',
#               "log_0.8_1.8_200_all_2020_04_11_03_58_50_877981.csv": CONFIG_3 + '-1',
#               "log_0.8_1.8_200_all_2020_04_11_03_59_34_059029.csv": CONFIG_3 + '-2',
#               "log_0.8_1.8_200_all_2021_12_06_10_27_40_013711.csv": CONFIG_3 + '-3',
#               "log_0.8_1.8_200_all_2021_12_06_18_01_53_598053.csv": CONFIG_3 + '-4'
#               }

DEFAULT_CONST_FILE = "data/constants.csv"
DEFAULT_LOG_PATH = "data/"
DEFAULT_OUTPUT_PATH = "output/"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MRGenerator')
    parser.add_argument('-i', '--initial', required=False)  # initial MR
    parser.add_argument('-d', '--data-path', required=False)  # field experiment data
    parser.add_argument('-c', '--constants', required=False)  # constants

    # print('================================================================================')
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
    for i in range(1):
        print(i, ': Searching', end='')
        idx += 1
        out_file = DEFAULT_OUTPUT_PATH + str(idx) + ".csv"

        file_list = data_parser.get_filenames_from_path(DEFAULT_LOG_PATH)

        # sum_tp, sum_tn, score, scores_list
        initial_mr_analysis = evaluator.calculate_score(i_mr, file_list, constants, 0)
        gen_mrs_analyses = generator.evolve(i_mr, file_list, constants)
        print('done')
        # converter.write_mr_to_csv(initial_mr_score, gen_mr_scores, generator.get_ga_params(), field_data,
        #                           constants, out_file)


    # print('================================================================================')
