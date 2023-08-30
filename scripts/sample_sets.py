import argparse, os, json, random

ap = argparse.ArgumentParser()
ap.add_argument('-f', '--file', required=False, help="file containing data set")
ap.add_argument('-k', '--k', required=False, help="number of sets", type=int)
ap.add_argument('-n', '--n', required=False, help="number of reviews per set", type=int)
ap.add_argument('-o', '--output', required=False, help="output folder")

args = vars(ap.parse_args())
file_path = args['file']
k = args['k']
n = args['n']
output_path = args['output']

with open(file_path, 'r') as file:
    data = json.load(file)

    # Shuffle the array in-place
    random.shuffle(data)
    bins = [data[i:i + n] for i in range(0, k * n, n)]

    for i, bin in enumerate(bins):
        with open(os.path.join(output_path, 'eval-sets', 'reviews-' + str(i) + '.json'), 'w') as outfile:
            json.dump(bin, outfile)