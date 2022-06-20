import argparse
import generator
import converter
import data_parser
import evaluator


DEFAULT_INIT_MR = "initial_mrs/initial_1.xml"
DEFAULT_DATA_FILE = "data/0.6_1.2_180_logs/log_0.6_1.2_180_all_2021_12_03_22_40_58_572206.csv"
DEFAULT_CONST_FILE = "data/constants.csv"
DEFAULT_OUTPUT_FILE = "output/2022-06-19_20_26/evaluation.csv"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MRGenerator')
    parser.add_argument('-i', '--initial', required=False)  # initial MR
    parser.add_argument('-d', '--data', required=False)  # field experiment data
    parser.add_argument('-c', '--constants', required=False)  # constants

    print('================================================================================')
    args = parser.parse_args()

    initial_mr_file = args.initial
    data_file = args.data
    constant_file = args.constants

    if args.initial is None:
        initial_mr_file = DEFAULT_INIT_MR

    if args.data is None:
        data_file = DEFAULT_DATA_FILE

    if args.constants is None:
        constant_file = DEFAULT_CONST_FILE

    i_mrs = converter.parse_mr_xml(initial_mr_file)
    field_data = data_parser.read_field_data(data_file)
    constants = data_parser.read_constants(constant_file)

    idx = 0
    for i in range(5):
        idx += 1
        out_file = "output/2022-06-19_20_26/evaluation_" + str(idx) + ".csv"
        for mr in i_mrs:
            (tp, tn, fp, fn, score) = evaluator.calculate_score(mr, field_data, constants, 0)
            initial_mr_score = (mr, tp, tn, fp, fn, score)

            gen_mr_scores = generator.evolve(mr, field_data, constants)
            converter.write_mr_to_csv(initial_mr_score, gen_mr_scores, field_data, constants, out_file)

    print('================================================================================')

