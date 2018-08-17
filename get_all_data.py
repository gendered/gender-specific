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
import requests
from wiktionaryparser import WiktionaryParser
import io
import re
import string
import sys
sys.path.insert(0, 'utils/')
from get_defs import getWordDefinition
from filter_word import isValidWord
from filter_word import isValidDefinition
from filter_word import searchWordForGenderedTerm
from filter_word import searchDefinitionForGenderedTerm

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

# wordnik api stuff
apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)

femaleTermsArr = ['woman', 'female', 'girl', 'lady', 'women', 'mother', 'daughter', 'wife']
maleTermsArr = ['man', 'male', 'boy', 'men', 'son', 'father', 'husband']

with open('words/discard.json') as f:
  discard = json.load(f)
  discardSet = set(entry['word'] for entry in discard)

allWords = []
wordSet = set()

# writes to a json file
def writeToJson(path, set):
  with open(path + '.json', 'w') as outfile:
      json.dump(list(set), outfile)

def addEntry(word, definition, gender, source, array):
  array.append({
    'word': word,
    'definition': definition,
    'gender': gender,
    'tags': [source]
  })

def findWordInArray(word, arr):
  for entry in arr:
    if entry['word'] == word:
      return entry
  return None

def addDefinition(entry, definition):
  defs = entry['definition']
  for d in defs:
    if d == definition:
      continue
  entry['definition'].append(definition)

def processDefinitions(definitions, gender=None):
  validDefinitions = []
  termsFound = False
  if len(definitions) > 0:
    for definition in definitions:
      termsInDef = searchDefinitionForGenderedTerm(definition, gender)
      if termsInDef is not None:
        gender = termsInDef[1]
        location = termsInDef[2]
        startIndex = location.start(0)
        endIndex = location.end(0)
        termsFound = True
        if isValidDefinition(definition, startIndex, endIndex):
          validDefinitions.append(definition)
  return (validDefinitions, termsFound)

def processWord(word, definition, source, words, gender=None):
  if isinstance(definition, str):
    definition = [definition]
  termInWord = searchWordForGenderedTerm(word)
  if termInWord is not None and termInWord[0]:
    wordSet.add(word)
    if gender is None:
      gender = termInWord[1]
    # add directly to allWords since we are not checking for multiple definitions
    addEntry(word, definition, gender, source, words)
    return
  validDefinitions = processDefinitions(definition, gender)
  if len(validDefinitions[0]) > 0:
    wordSet.add(word)
    addEntry(word, validDefinitions, gender, source, words)
  elif validDefinitions[1]:
    discardSet.add(word)
    addEntry(word, [definition], gender, source, discard)

# get words from wordnik
def getWordnik():
  wordsApi = WordsApi.WordsApi(client)
  source = 'wordnik'

  def callApi(terms, gender):
    # to store words from this source and check for multiple definitions of the same word
    words = []
    for term in terms:
      reverseDictionary = wordsApi.reverseDictionary(term,  includePartOfSpeech='noun', limit=10000).results
      for result in reverseDictionary:
        word = result.word.lower()
        definition = (result.text).lower()
        # if word is already in the set, add the new definition of the word
        if word in wordSet:
          entry = findWordInArray(word, words)
          if entry is not None:
            addDefinition(entry, definition)
          continue
        elif word not in wordSet and word not in discardSet and isValidWord(word):
          processWord(word, definition, source, words, gender)
    allWords.extend(words)
  callApi(femaleTermsArr, 'female')
  callApi(maleTermsArr, 'male')
  print ('wordnik done')

# datamuse
def getDatamuse():
  api = datamuse.Datamuse()
  source = 'datamuse'
  def callApi(terms, gender):
    # to store words from this source and check for multiple definitions of the same word
    words = []
    for term in terms:
      results = api.words(ml=term, max=1000, md='dp')
      for result in results:
        word = result['word'].lower()
        # check if it's a noun
        if ('tags' in result and 'n' in result['tags']):
          if ('defs' in result):
            definition = result['defs']
          else:
              definition = getWordDefinition(word)
          if (definition != ' '):
            if word in wordSet:
              entry = findWordInArray(word, words)
              if entry is not None:
                addDefinition(entry, definition)
              continue
            elif (word not in wordSet and word not in discardSet and isValidWord(word)):
              processWord(word, definition, source, words, gender)
    allWords.extend(words)

  callApi(femaleTermsArr, 'female')
  callApi(maleTermsArr, 'male')
  print ('datamuse done')

def getWebster():
  with open('data/webster/dictionary.json', 'r') as f:
    results = json.load(f)
  source = 'webster'
  for result in results:
    # to-do: strip definition if it's too long
    definition = [(results[result]).lower()]
    word = result.lower()
    if (word not in wordSet and word not in discardSet and isValidWord(word)):
      processWord(word, definition, source, allWords)
  print('webster done')

def getGSFull():
  with open('data/gender_specific_full.json', 'r') as f:
    results = json.load(f)

  source = 'debiaswe'
  # all words in this file are gendered, so put the ones we can't get definitions for
  # in a separate file we will address later
  words = []
  for result in results:
    word = result.lower()
    if (word not in wordSet and word not in discardSet and isValidWord(word)):
      definition = getWordDefinition(word)
      if (definition is not None and definition != ' '):
        processWord(word, definition, source, allWords)
  print ('gender specific done')

def addTerms(terms, gender):
  for word in terms:
    definition = getWordDefinition(word)
    if word not in wordSet and word not in discardSet:
      wordSet.add(word)
      addEntry(word, definition, gender, 'wordnik', allWords)

# stuff only to run when not called via 'import' here
addTerms(['woman', 'girl', 'lady', 'mother', 'daughter', 'wife'], 'female')
addTerms(['man', 'boy', 'son', 'father', 'husband'], 'male')
getWordnik()
getWebster()
getDatamuse()
getGSFull()

print(len(allWords))
writeToJson('words/all-2', allWords)
writeToJson('words/discard-2', discard)
