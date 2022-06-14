import argparse
import generator
import converter


parser = argparse.ArgumentParser(description='MRGenerator')
parser.add_argument('-d', '--data', required=True)      # field experiment data
parser.add_argument('-i', '--initial', required=True)   # initial MR

args = parser.parse_args()

i_mr = converter.parse_mr_xml(args.initial)
gen_mr = generator.generate_mr(i_mr, args.data)
converter.write_mr_to_csv(gen_mr)

print('end of program')
