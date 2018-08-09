from dotenv import load_dotenv
from wordnik import *
from datamuse import datamuse
import json
import os
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.stem import *
import collections
from PyDictionary import PyDictionary
import pandas as pd
import urbandictionary as ud
import requests
from wiktionaryparser import WiktionaryParser
from vocabulary.vocabulary import Vocabulary as vb
import io
import re
import string
import sys
sys.path.insert(0, 'utils/')
from get_defs import getWordDefinition

with open('words/all.json') as f:
    all_words = json.load(f)

def writeToJson(path, arr):
	with open(path + '.json', 'w') as outfile:
	    json.dump(arr, outfile)

all = []
discard = []

def hasWordsToExclude(word, definition):
    f = open('utils/pattern.txt','r')
    terms = f.read().replace('\n', '')
    rgex = re.compile(terms)
    termInDef = rgex.search(definition)
    if termInDef is not None:
        start = termInDef.start(0)
        end = termInDef.end(0)
        return True
    return False

def isValidWord(word):
    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)
    if hasNumbers(word):
        return False
    return True

def isGendered(word, definition):
    s = r"""\b[\w]*?woman\b|\bfemale\b|\b[\w]*?girl\b|\bgirls\b|\b[\w]*?women\b|\blady\b|\b[\w]*?mother\b|\b[\w]*?daughter\b|\bwife\b|\bman\b|\bmale\b|\bboy\b|\bmen\b|\bboys\b|\bson\b|\b[\w]*?father\b|\bhusband\b"""
    pattern = re.compile(s)
    termsInDef = pattern.search(definition.lower())
    s = r"""\b[\w]*?woman\b|\b[\w]*?girl|\b[\w]*?women\b|\b[\w]*?mother\b|\b[\w]*?daughter\b|\bwife\b|\b[\w]*?man\b|\b[\w]*?boy\b|\b[\w]*?men\b|\b[\w]*?son\b|\b[\w]*?father\b|\b[\w]*?husband\b"""
    pattern = re.compile(s)
    termsInWord = pattern.search(word)
    if termsInDef is not None and termsInWord is None:
        endIndex = termsInDef.end(0)
        if len(definition) != endIndex:
            last = definition[endIndex]
            if last == "'" or last == '-':
                return False
        return True
    elif termsInDef is not None or termsInWord is not None:
        return True
    return False


for entry in all_words:
    word = entry['word']
    if isValidWord(word):
        definition = entry['definition']
        if isGendered(word, definition) and not hasWordsToExclude(word, definition):
            all.append(entry)
        else:
            discard.append(entry)

# print(len(all))
writeToJson('words/all-2', all)
writeToJson('words/discard-2', discard)
