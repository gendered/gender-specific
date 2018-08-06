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
# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

# wordnik api stuff
apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)

femaleTermsArr = ['woman', 'female', 'girl', 'lady', 'women', 'mother', 'daughter', 'wife']
femaleTerms = r"""\b[\w-]*woman\b[^'-]|\bfemale\b|\b[\w-]girl\b|\bgirls\b
|\b[\w-]*women\b[^'-]|\blady\b[^'-]|\b[\w-]*mother\b[^'-]|\b[\w-]*daughter\b|\bwife\b"""

femaleRegex = re.compile(femaleTerms)

maleTermsArr = ['man', 'male', 'boy', 'men', 'son', 'father', 'husband']
maleTerms = r"""\bman\b[^'-]|\bmale\b|\bboy\b|\bmen\b[^'-]|\bboys\b|\bson\b|\b[\w-]*father\b|\bhusband\b"""
maleRegex = re.compile(maleTerms)
wordSet = set(['woman', 'female', 'girl', 'lady', 'man', 'male', 'boy', 'mother', 'daughter', 'son', 'father', 'husband', 'wife'])

# writes to a json file
def writeToJson(path, set):
  with open(path + '.json', 'w') as outfile:
      json.dump(list(set), outfile)

# check if the word is one of these gendered words or has a mention of them
def getWordPattern(gender):
    if gender == 'female':
        return re.compile(r'\b[\w-]*woman\b|\b[\w-]girl\b|\bgirls\b|\b[\w-]*women\b|\blady\b|\b[\w-]*mother\b|\b[\w-]*daughter\b|\bwife\b')
    else:
        return re.compile(r'\b[\w-]*man\b|\b[\w-]*boy\b|\bmen\b|\bboys\b|\bson\b|\b[\w-]*father\b|\bhusband\b')

# get words from wordnik
def getWordnik():
  wordsApi = WordsApi.WordsApi(client)
  source = 'wordnik'
  def callApi(terms, pattern, gender):
    words = []
    for term in terms:
        reverseDictionary = wordsApi.reverseDictionary(term,  includePartOfSpeech='noun', limit=10000).results
        for result in reverseDictionary:
            word = result.word.lower()
            definition = result.text
            if (word not in wordSet and word not in discardSet and filterByWord(word)):
                termsInWord = getWordPattern(gender).search(word)
                # get index of term
                if termsInWord is not None:
                    wordSet.add(word)
                    words.append({
                      'word': word,
                      'definition': definition,
                      'gender': gender,
                      'tags': [source]
                    })
                    continue
                termsInString = pattern.search(definition)
                if termsInString is not None:
                    startIndex = termsInString.start(0)
                    endIndex = termsInString.end(0)
                    if filterWordByDefinition(definition, startIndex, endIndex):
                        wordSet.add(word)
                        words.append({
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
    allWords.extend(words)

  callApi(femaleTermsArr, femaleRegex, 'female')
  callApi(maleTermsArr, maleRegex, 'male')
  print ('wordnik done')

# datamuse
def getDatamuse():
  api = datamuse.Datamuse()
  source = 'datamuse'
  def callApi(terms, pattern, gender):
    words = []
    for term in terms:
      results = api.words(ml=term, max=1000, md='dp')
      for result in results:
        word = result['word'].lower()
        if (word not in wordSet and word not in discardSet and filterByWord(word)):
            # check if it's a noun
            if ('tags' in result):
                if ('n' in result['tags']):
                  if ('defs' in result):
                    definition = result['defs'][0]
                  else:
                      definition = getWordDefinition(word)
                      if (definition != ' '):
                        termsInWord = getWordPattern(gender).search(word)
                        # get index of term
                        if termsInWord is not None:
                            wordSet.add(word)
                            words.append({
                              'word': word,
                              'definition': definition,
                              'gender': gender,
                              'tags': [source]
                            })
                            continue
                        termsInString = pattern.search(definition)
                        if termsInString is not None:
                              startIndex = termsInString.start(0)
                              endIndex = termsInString.end(0)
                              if filterWordByDefinition(definition, startIndex, endIndex):
                                  wordSet.add(word)
                                  words.append({
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
    allWords.extend(words)

  callApi(femaleTermsArr, femaleRegex, 'female')
  callApi(maleTermsArr, maleRegex, 'male')
  print ('datamuse done')

def getWebster():
    with open('data/webster/dictionary.json', 'r') as f:
      results = json.load(f)
    source = 'webster'

    def bucket(pattern, gender):
        words = []
        for result in results:
            # to-do: strip definition if it's too long
            definition = results[result]
            termsInString = pattern.search(definition.lower())
            word = result.lower()
            termsInWord = getWordPattern(gender).search(word)
            if (word not in wordSet and word not in discardSet and filterByWord(word)):
                if termsInWord is not None:
                        wordSet.add(word)
                        words.append({
                            'word': word,
                            'definition': definition,
                            'gender': gender,
                            'tags': [source]
                        })
                        continue
                if termsInString is not None:
                    if (word not in wordSet and word not in discardSet):
                        startIndex = termsInString.start(0)
                        endIndex = termsInString.end(0)
                        if filterWordByDefinition(definition, startIndex, endIndex):
                            # get part of speech
                            for ss in wn.synsets(result):
                                pos = ss.pos()
                                if ('n' in pos):
                                    wordSet.add(result)
                                    words.append({
                                        'word': result,
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


    bucket(femaleRegex, 'female')
    bucket(maleRegex, 'male')
    print ('webster done')

def getGSFull():
  with open('data/gender_specific_full.json', 'r') as f:
    results = json.load(f)

  source = 'debiaswe'
  # all words in this file are gendered, so put the ones we can't get definitions for
  # in a separate file we will address later
  def bucket(pattern, gender):
    words = []
    for result in results:
      word = result.lower()
      if (word not in wordSet and word not in discardSet and filterByWord(word)):
        termsInWord = getWordPattern(gender).search(word)
        definition = getWordDefinition(result)
        if (definition is not None and definition != ' '):
          if termsInWord is not None:
            wordSet.add(word)
            words.append({
                'word': word,
                'definition': definition,
                'gender': gender,
                'tags': [source]
            })
            continue
          termsInString = pattern.search(definition)
          if termsInString is not None:
            startIndex = termsInString.start(0)
            endIndex = termsInString.end(0)
            if filterWordByDefinition(definition, startIndex, endIndex):
              words.append({
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
    allWords.extend(words)
  bucket(femaleRegex, 'female')
  bucket(maleRegex, 'male')
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

  # TODO: other ways to filter data?
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
  with open('words/unfiltered/all-unfiltered.json') as f:
    allWords = json.load(f)
    wordSet = set(entry['word'] for entry in allWords)

  with open('words/unfiltered/discard.json') as f:
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

  writeToJson('words/unfiltered/all-unfiltered', allWords)
  writeToJson('words/unfiltered/discard', discardSet)
