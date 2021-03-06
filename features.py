import numpy as np
from collections import defaultdict
import csv
import nltk

# Warriner et. al. affect score import
lines = [line.rstrip('\n').split(",") for line in open('Ratings_Warriner_et_al.csv')]
WARRINER_AFFECT = {}
for line in lines[1:]:
    WARRINER_AFFECT[line[1].lower()] = float(line[2])
    
# SentiStrength score importing
lines = [line.rstrip('\n') for line in open('SentStrength_Data_Sept2011/EmotionLookupTable.txt')]
line_splits = [line.split() for line in lines]
SENTI_STRENGTH = {}
for line in line_splits:
    SENTI_STRENGTH[line[0].rstrip('*')] =  float(line[1])
    
# Booster word list
lines = [line.rstrip('\n') for line in open('SentStrength_Data_Sept2011/BoosterWordList.txt')]
line_splits = [line.split() for line in lines]
SENTI_STRENGTH = {}
for line in line_splits:
    SENTI_STRENGTH[line[0].rstrip('*')] =  float(line[1])
    
''' FEATURE FUNCTIONS
'''

# Capitalization counter
# https://github.com/MathieuCliche/Sarcasm_detector
def cap_feature(yak):
    features = defaultdict(float)
    counter = 0
    thresh = 4 # for alternative feature below
    for j in range(len(yak[2])):
        counter += int(yak[2][j].isupper())
        #features['Capitalization'] += int(yak[2][j].isupper())
    features['Capitalization'] = int(counter >= thresh)
    return features

def cap_propor_feature(yak):
    features = defaultdict(float)
    counter = 0
    for j in range(len(yak[2])):
        counter += int(yak[2][j].isupper())
    features["Caps Proportion"] = float(counter / len(yak[2]))
    return features
    
# Punctuation
punc_marks = ['.', '...', ';', ':', '?', '!', '\'', '\"']
def punc_feature(yak):
    features = defaultdict(float)
    for i in punc_marks:
        features[('Punctuation ' + i)] += float(i in yak[2])
    return features

# Delta affect
def imbalance_feature(yak):
    features = defaultdict(float)
    words = yak[2].split(" ")
    affect = np.array([])
    senti = np.array([])

    for word in words:
        if word.lower() in WARRINER_AFFECT:
            affect = np.append(affect, WARRINER_AFFECT[word.lower()])
        if word.lower() in SENTI_STRENGTH:
            senti = np.append(senti, SENTI_STRENGTH[word.lower()])  
    
    if affect.size > 0:
        features["Delta Affect"] = float(np.amax(affect) - np.amin(affect)) 
    if senti.size > 0:
        features["Delta Sentiment"] = float(np.amax(senti) - np.amin(senti)) 
    
    return features
    
# Is the sentence interrogative?
def interrogative_feature(yak):
    features = defaultdict(float)
    model_words = ['what', 'where', 'when', 'why', 'who']
    auxiliary_verbs = ['am', 'is', 'are', 'was', 'were', 'am', 'do', 'did', 'does']
    words = yak[2].split(" ")
    
    is_interrogative = ((words[0] in model_words) and 
                        (words[1] in auxiliary_verbs) and ('?' in yak[2]))
    features["Interrogative"] = float(is_interrogative)
    return features

# "section leader" and "section leaders"
# punctuation cutting off yaks.
def bigram_feature(yak):
    features = defaultdict(float)
    words = yak[2].lower().split()
    school = yak[0]
    for ind in xrange(len(words) - 1):
        features[(school, words[ind], words[ind + 1])] += 1.0
    return features

# does the yak contain a handle?
def handle_feature(yak):
    features = defaultdict(float)
    features["Handle"] = float(yak[1] != '')
    return features

def handle_school_feature(yak):
    features = defaultdict(float)
    features[(yak[0],yak[1].lower())] += 1.0
    return features

# PRITHVI'S NEW STUFF

def trigram_feature(yak):
    features = defaultdict(float)
    words = yak[2].lower().split()
    school = yak[0]
    for ind in xrange(len(words) - 2):
        features[(school, words[ind], words[ind + 1], words[ind + 2])] += 1.0
    return features

def unigram_feature(yak):
    features = defaultdict(float)
    text = yak[2]
    tokens = [word for sent in nltk.tokenize.sent_tokenize(text) for word in nltk.tokenize.word_tokenize(sent)]
    words = filter(lambda word: word not in ',-', tokens)
    for word in words:
        features[word] += 1.0
    return features

def word_count_feature(yak):
    features = defaultdict(float)
    text = yak[2].lower()
    tokens = [word for sent in nltk.tokenize.sent_tokenize(text) for word in nltk.tokenize.word_tokenize(sent)]
    words = filter(lambda word: word not in ',-', tokens)
    counts = [word_counts[word] for word in words]
    features["num_zero_count_words"] = counts.count(0) if len(counts) > 0 else 0
    features["max_count_word"] = max(counts) if len(counts) > 0 else 0
    nonzeros = [count for count in counts if count > 0]
    features["min_count_word"] = min(nonzeros) if len(nonzeros) > 0 else 0
    return features
    