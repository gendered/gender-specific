import json
from gensim.models import KeyedVectors
filename = 'models/GoogleNews-vectors-negative300.bin'
model = KeyedVectors.load_word2vec_format(filename, binary=True)
import re
from dotenv import load_dotenv
from wordnik import *
import collections
from PyDictionary import PyDictionary
import requests
import os
from wiktionaryparser import WiktionaryParser
import sys

sys.path.insert(0, 'utils/')
from get_defs import getWordDefinition
from vocabulary.vocabulary import Vocabulary as vb

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

# wordnik api stuff
apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)

# open files
with open('words/all.json') as f:
    all = json.load(f)

all_words_only = [entry['word'] for entry in all]
wordOpposites = {}

def writeToJson(path, arr):
	with open(path + '.json', 'w') as outfile:
	    json.dump(arr, outfile)


def defineWordEquivalent():
    obj = {
        'male': 'female',
        'man': 'woman',
        'father': 'mother',
        'wife': 'husband',
        'boy': 'girl',
        'maternal': 'paternal'
    }

    for term in obj:
        equiv = obj[term]
        wordOpposites[term] = equiv
        wordOpposites[equiv] = term

def findGenderEquivalent(word, gender):
    def checkEquivalent(equivalent):
        definition = getWordDefinition(equivalent)
        if definition != ' ' and definition is not None:
            if gender == 'female':
                opp_gender = 'male'
                maleTerms = r'\bman\b|\bmale\b|\bboy\b|\bmen\b|\bboys\b|\bson\b|\b[\w-]*father\b|\bhusband\b'
                maleRegex = re.compile(maleTerms)
                termsInString = maleRegex.search(definition)
            else:
                opp_gender = 'female'
                femaleTerms = r'\b[\w-]*woman\b|\bfemale\b|\b[\w-]girl\b|\bgirls\b|\b[\w-]*women\b|\blady\b|\b[\w-]*mother\b|\b[\w-]*daughter\b|\bwife\b'
                femaleRegex = re.compile(femaleTerms)
                termsInString = femaleRegex.search(definition)
            if termsInString is not None:
                all.append({
                    'word': equivalent,
                    'definition': definition,
                    'gender': opp_gender
                })
                all_words_only.append(equivalent)
                return equivalent
        return ' '

    # Check if opposite of word can be found using the word itself.
    # E.g words like grandfather, grandmother
    def checkWordForEquivalent():
        gendered = r'woman|man|father|mother|wife|husband|boy|girl|maternal|paternal'
        rgex = re.compile(gendered)
        termsInString = rgex.search(word)
        if termsInString is not None:
            word_copy = word
            startIndex = termsInString.start(0)
            endIndex = termsInString.end(0)
            toReplace = word[startIndex:endIndex]
            equivalent = word_copy.replace(toReplace, wordOpposites[toReplace])
            if equivalent in all_words_only:
                return equivalent
            return checkEquivalent(equivalent)

        # handle 'ess', 'ette' differently
        gendered = r'ette|ess'
        rgex = re.compile(gendered)
        termsInString = rgex.search(word)
        if termsInString is not None:
            word_copy = word
            startIndex = termsInString.start(0)
            endIndex = termsInString.end(0)
            equivalent = word[0:startIndex]
            if equivalent in all_words_only:
                return equivalent
        return ' '

    def getGoogleNews():
        if word in model.vocab:
            if (gender == 'female'):
                pos = 'man'
                neg = 'woman'
            else:
                pos = 'woman'
                neg = 'man'
            result = model.most_similar(positive=[pos, word], negative=[neg], topn=1)
            if result is not None:
                result = result[0]
                equivalent = result[0]
                score = result[1]
                if score > 0.6:
                    if equivalent in all_words_only:
                        return equivalent
                    else:
                        return checkEquivalent(equivalent)
        return ' '


    for term in wordOpposites:
        if term == 'word':
            return wordOpposites[term]
    equiv = checkWordForEquivalent()
    if equiv != ' ':
        return equiv
    equiv = getGoogleNews()
    if equiv != ' ':
        return equiv

if __name__ == "__main__":
    defineWordEquivalent()
    for entry in all:
        if 'equivalent' not in entry:
            word = entry['word']
            gender = entry['gender']
            equiv = findGenderEquivalent(word, gender)
            if equiv != ' ' and equiv is not None:
                entry['equivalent'] = equiv

    writeToJson('words/all', all)
