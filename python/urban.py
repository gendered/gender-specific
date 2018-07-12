import json
from gensim.models import KeyedVectors, word2vec
import csv
import numpy as np
import pandas as pd

# open csv files
ub = pd.read_csv("urban_dictionary.csv", na_values=None, keep_default_na=False)

def loadModel(gloveFile):
    model = {}
    for index, row in ub.iterrows():
        word = row[0]
        splitLine = line.split()
        word = splitLine[0]
        embedding = np.array([float(val) for val in splitLine[1:]])
        model[word] = embedding
    print "Done.",len(model)," words loaded!"
    return model

loadModel()
