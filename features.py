import numpy as np
from collections import defaultdict
import csv

# Warriner et. al. affect score import
lines = [line.rstrip('\n').split(",") for line in open('Ratings_Warriner_et_al.csv')]
WARRINER_AFFECT = defaultdict(float)
for line in lines[1:]:
    WARRINER_AFFECT[line[1].lower()] = float(line[2])

# Feature functions

'''
Pointedness
'''
# Capitalization counter
# https://github.com/MathieuCliche/Sarcasm_detector
def cap_feature(yak):
    counter = 0
    thresh = 4 # for alternative feature below
    for j in range(len(yak[2])):
        features['Capitalization'] += int(yak[2][j].isupper())
#     features['Capitalization'] = int(counter >= thresh)
    return features
    
# Punctuation
punc_marks = ['.', '...', ';', ':', '?', '!', '\'', '\"']

def punc_feature(yak):
    features = defaultdict(float)
    for i in punc_marks:
        features[('Punctuation ' + i)] += float(i in yak[2])
    return features

'''
Delta affect and delta sentiment
'''

def affect_feature(yak):
    features = defaultdict(float)
    words = yak[2].split(" ")
    scores = np.zeros((len(words)))
    for ind, word in enumerate(words):
        scores[ind] = WARRINER_AFFECT[word.lower()]
    features["Delta Affect"] = (np.amax(scores) - np.amin(scores))
    return features
    
def sentiment_feature(yak):
    features = defaultdict(float)
    features["Delta Sentiment"] = 0.0
    return features

# "section leader" and "section leaders"
# punctuation cutting off yaks.
def bigram_feature(yak):
    words = yak[2].lower().split()
    school = yak[0]
    for ind in xrange(len(words) - 1):
        features[(school, words[ind], words[ind + 1])] += 1.0
    return features