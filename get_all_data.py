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
from filter_word import isValidWord
from filter_word import isValidDefinition
from filter_word import searchTextForGenderedTerm

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
wordSet = set(['woman', 'female', 'girl', 'lady', 'man', 'male', 'boy', 'mother', 'daughter', 'son', 'father', 'husband', 'wife'])

# writes to a json file
def writeToJson(path, set):
  with open(path + '.json', 'w') as outfile:
      json.dump(list(set), outfile)

# get words from wordnik
def getWordnik():
  wordsApi = WordsApi.WordsApi(client)
  source = 'wordnik'
  def callApi(terms, gender):
    print('in wordnik')
    words = []
    for term in terms:
      reverseDictionary = wordsApi.reverseDictionary(term,  includePartOfSpeech='noun', limit=10000).results
      for result in reverseDictionary:
        word = result.word.lower()
        definition = (result.text).lower()
        if (word not in wordSet and word not in discardSet and isValidWord(word)):
          termInWord = searchTextForGenderedTerm(word, gender)
          if termInWord is not None and termInWord[0]:
            wordSet.add(word)
            allWords.append({
              'word': word,
              'definition': definition,
              'gender': gender,
              'tags': [source]
            })
            continue
          termsInString = searchTextForGenderedTerm(definition, gender)
          if termsInString is not None:
            location = termsInString[2]
            startIndex = location.start(0)
            endIndex = location.end(0)
            if isValidDefinition(definition, startIndex, endIndex):
              wordSet.add(word)
              allWords.append({
                'word': word,
                'definition': definition,
                'gender': gender,
                'tags': [source]
              })
            else:
              discardSet.add(word)
              discard.append({
                'word': word,
                'definition': definition,
                'gender': gender,
                'tags': [source]
              })

  callApi(femaleTermsArr, 'female')
  callApi(maleTermsArr, 'male')
  print ('wordnik done')

# datamuse
def getDatamuse():
  api = datamuse.Datamuse()
  source = 'datamuse'
  def callApi(terms, gender):
    words = []
    for term in terms:
      results = api.words(ml=term, max=1000, md='dp')
      for result in results:
        word = result['word'].lower()
        if (word not in wordSet and word not in discardSet and isValidWord(word)):
          # check if it's a noun
          if ('tags' in result and 'n' in result['tags']):
            if ('defs' in result):
              definition = result['defs'][0]
            else:
                definition = getWordDefinition(word)
            if (definition != ' '):
              termInWord = searchTextForGenderedTerm(word, gender)
              if termInWord is not None and termInWord[0]:
                wordSet.add(word)
                allWords.append({
                  'word': word,
                  'definition': definition,
                  'gender': gender,
                  'tags': [source]
                })
                continue
              termsInString = searchTextForGenderedTerm(definition, gender)
              if termsInString is not None:
                location = termsInString[2]
                startIndex = location.start(0)
                endIndex = location.end(0)
                if isValidDefinition(definition, startIndex, endIndex):
                    wordSet.add(word)
                    allWords.append({
                      'word': word,
                      'definition': definition,
                      'gender': gender,
                      'tags': [source]
                    })
                else:
                  discardSet.add(word)
                  discard.append({
                    'word': word,
                    'definition': definition,
                    'gender': gender,
                    'tags': [source]
                  })

  callApi(femaleTermsArr, 'female')
  callApi(maleTermsArr, 'male')
  print ('datamuse done')

def getWebster():
  with open('data/webster/dictionary.json', 'r') as f:
    results = json.load(f)
  source = 'webster'
  words = []
  for result in results:
    # to-do: strip definition if it's too long
    definition = (results[result]).lower()
    word = result.lower()
    if (word not in wordSet and word not in discardSet and isValidWord(word)):
      termInWord = searchTextForGenderedTerm(word)
      if termInWord is not None and termInWord[0]:
        wordSet.add(word)
        allWords.append({
            'word': word,
            'definition': definition,
            'gender': termInWord[1],
            'tags': [source]
        })
        continue
      termsInString = searchTextForGenderedTerm(definition)
      if termsInString is not None:
        gender = termsInString[1]
        location = termsInString[2]
        startIndex = location.start(0)
        endIndex = location.end(0)
        if isValidDefinition(definition, startIndex, endIndex):
          # get part of speech
          for ss in wn.synsets(result):
            pos = ss.pos()
            if ('n' in pos):
              wordSet.add(result)
              allWords.append({
                'word': result,
                'definition': definition,
                'gender': gender,
                'tags': [source]
              })
              continue
        else:
          discardSet.add(word)
          discard.append({
            'word': word,
            'definition': definition,
            'gender': gender,
            'tags': [source]
          })
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
      definition = getWordDefinition(result)
      if (definition is not None and definition != ' '):
        definition = definition.lower()
        termInWord = searchTextForGenderedTerm(word)
        if termInWord is not None and termInWord[0]:
          wordSet.add(word)
          allWords.append({
              'word': word,
              'definition': definition,
              'gender': termInWord[1],
              'tags': [source]
          })
          continue
        termsInString = searchTextForGenderedTerm(definition)
        if termsInString is not None:
          gender = termsInString[1]
          location = termsInString[2]
          startIndex = location.start(0)
          endIndex = location.end(0)
          if isValidDefinition(definition, startIndex, endIndex):
            allWords.append({
              'word': result,
              'definition': definition,
              'gender': gender,
              'tags': [source]
            })
            wordSet.add(result)
          else:
            discardSet.add(word)
            discard.append({
              'word': word,
              'definition': definition,
              'gender': gender,
              'tags': [source]
            })
  print ('gender specific done')

def getUrbanDictionary():
  source = 'urban-dic'
  # only these columns are needed
  fields = ['word', 'definition', 'thumbs_up']
  # open csv files
  ub_1 = pd.read_csv("data/urban/urban-dic-1.csv", encoding="ISO-8859-1", skipinitialspace=True, usecols=fields)
  ub_2 = pd.read_csv("data/urban/urban-dic-2.csv", encoding="ISO-8859-1", skipinitialspace=True, usecols=fields)
  ub_3 = pd.read_csv("data/urban/urban-dic-3.csv", encoding="ISO-8859-1", skipinitialspace=True, usecols=fields)
  ub_4 = pd.read_csv("data/urban/urban-dic-4.csv", encoding="ISO-8859-1", skipinitialspace=True, usecols=fields)

  frames = [ub_1, ub_2, ub_3, ub_4]
  # add the two csvs together and remove nan values
  ub = (pd.concat(frames)).dropna()

  # only include entries with more than 1000 upvotes
  ub = ub[ub['thumbs_up'] >= 1000]
  # remove duplicates
  ub = ub[~ub[['word']].apply(lambda x: x.str.lower().str.replace(" ","")).duplicated()]

def addTerms(terms, gender):
  for word in terms:
    definition = getWordDefinition(word)
    if word not in wordSet and word not in discardSet:
      wordSet.add(word)
      allWords.append({
        'word': word,
        'definition': definition,
        'gender': gender,
        'source': 'wordnik'
      })


if __name__ == "__main__":
  with open('words/all.json') as f:
    allWords = json.load(f)
    print(len(allWords))
    wordSet = set(entry['word'] for entry in allWords)

  with open('words/discard.json') as f:
    discard = json.load(f)
    discardSet = set(entry['word'] for entry in discard)

  # stuff only to run when not called via 'import' here
  addTerms(['woman', 'girl', 'lady', 'mother', 'daughter', 'wife'], 'female')
  addTerms(['man', 'boy', 'son', 'father', 'husband'], 'male')
  getWordnik()
  getWebster()
  getDatamuse()
  getGSFull()
  # getUrbanDictionary()
  print(len(allWords))
  writeToJson('words/all-2', allWords)
  writeToJson('words/discard', discardSet)
