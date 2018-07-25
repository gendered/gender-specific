import json
import os
from pprint import pprint
from vocabulary.vocabulary import Vocabulary as vb
from wordnik import *
from nltk.corpus import wordnet
from dotenv import load_dotenv
import os
from get_all_data import getWordDefinition

with open('words/filtered/all.json') as f:
    all = json.load(f)

allSets = []
wordsInSet = set([])
synonyms = []

def writeToJson(path, set):
	with open(path + '.json', 'w') as outfile:
	    json.dump(jsonpickle.encode(set, unpicklable=False), outfile)
        all_words_only = [entry['word'] for entry in all]

def getSynonyms(word):
    synonymsOne = vb.synonym(word)
    synonymsTwo = []
    if isinstance(synonymsOne, list):
        synonymsOne = json.loads(synonyms)
        synonymsOne = [synonym['text'] for synonym in synonyms]
    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            synonymsTwo.append(l.name())

    if isinstance(synonymsTwo, list) and isinstance(synonymsOne, list):
        return list(set().union(synonymsOne, synonymsTwo))
    elif isinstance(synonymsTwo, list):
        return synonymsTwo
    elif isinstance(synonymsOne, list):
        return synonymsOne
    return ' '

def isNoun(word):
    for ss in wn.synsets(word):
        pos = ss.pos()
        if ('n' in pos):
            return True
    return False

def isGendered(word, gender):
    definition = getWordDefinition(word)
    if gender == 'female':
        pattern = re.compile(r'\b[\w-]*woman\b|\bfemale\b|\b[\w-]girl\b|\bgirls\b|\b[\w-]*women\b|\blady\b|\b[\w-]*mother\b|\b[\w-]*daughter\b|\bwife\b')
    elif gender == 'male':
        pattern = re.compile(r'\bman\b|\bmale\b|\bboy\b|\bmen\b|\bboys\b|\bson\b|\b[\w-]*father\b|\bhusband\b')
    termsInString = pattern.search(definition)
    if termsInString is not None:
        all.append({
            'word': word,
            'definition': definition,
            'gender': gender
        })
        all_words_only.append(word)
        return True

def createSets(words):
    for entry in words:
        word = entry['word']
        gender = entry['gender']
        # create set with word
        synonyms_set = set([word])
        synonyms = getSynonyms(word)
        # add it's synonyms to set
        if (synonyms != ' '):
            final_synonyms = []
            for word in synonyms:
                if word in all_words_only:
                    final_synonyms.append(word)
                else:
                    if isNoun(word) and isGendered(word, gender):
                        final_synonyms.append(word)
            synonyms_set.extend(final_synonyms)
            allSets.append(list(synonyms_set))
            
if __name__ == "__main__":
    createSets(all)
    writeToJson('words/sets', allSets)
