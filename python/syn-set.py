import json
import os
from pprint import pprint
from vocabulary.vocabulary import Vocabulary as vb

with open('words/all-1.json') as f:
    all = json.load(f)

allSets = []
wordsInSet = set([])
def writeToJson(path, set):
	with open(path + '.json', 'w') as outfile:
	    json.dump(jsonpickle.encode(set, unpicklable=False), outfile)

def getSynonyms(word):
    synonyms = vb.synonym(word)
    if isinstance(synonyms, list):
        synonyms = json.loads(synonyms)
        return [synonym['text'] for synonym in synonyms]
    return ' '


def createSets(words):
    for entry in words:
        word = entry['word']
        print(word)
        # create set with word
        synonyms_set = set([word])
        synonyms = getSynonyms(word)
        # add it's synonyms to set
        if (synonyms != ' '):
            synonyms_set.extend(synonyms)
            # wordsInSet.update(synonyms)
            allSets.append(list(synonyms_set))


createSets(all)
writeToJson('words/sets', allSets)
