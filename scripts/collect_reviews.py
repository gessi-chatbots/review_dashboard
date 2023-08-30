from CoNLL_dict import convert_reviews_to_dict
from CoNLL_dict import read_doc

import argparse, os, json

ap = argparse.ArgumentParser()
ap.add_argument('-f', '--folder', required=False, help="folder containing data sets")

args = vars(ap.parse_args())
folder = args['folder']

review_keys = []

for file in os.listdir(folder):
    d = os.path.join(folder, file)
    if os.path.isdir(d):
       for file in os.listdir(d):
            set_file = read_doc(os.path.join(d, file))
            set_dict = convert_reviews_to_dict(set_file)
            for key in set_dict.keys():
                review_keys.append(key.split('_')[0])

review_keys = set(review_keys)

# Opening JSON file
f = open(os.path.join(folder, 'MApp-KG-scan.json'))
apps = json.load(f)

reviews = []
for key in review_keys:
    for app in apps:
        for review in app['reviews']:
            if review['reviewId'] == key:
                reviews.append(review['review'])

with open(os.path.join(folder, 'reviews.json'), 'w') as outfile:
    json.dump(reviews, outfile)