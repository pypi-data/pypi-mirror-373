import argparse

from biolib.sdk import Runtime

parser = argparse.ArgumentParser(description='Process some biological sequences.')
parser.add_argument('--input', type=str, required=True, help='Input protein sequences')
args = parser.parse_args()

# update the BioLib result name based on the provided file
Runtime.set_result_name_from_file(args.input)

print(f'Processing input file {args.input}...')
