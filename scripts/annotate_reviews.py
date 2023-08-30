import argparse, os, json, random

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--input-folder', required=False, help="folder containing the input data sets")
ap.add_argument('-o', '--output-folder', required=False, help="output folder")

args = vars(ap.parse_args())
file_path = args['file']
k = args['k']
n = args['n']
output_path = args['output']

with open(file_path, 'r') as file:
    data = json.load(file)