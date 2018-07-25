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
femaleTerms = r'\b[\w-]*woman\b|\bfemale\b|\b[\w-]girl\b|\bgirls\b|\b[\w-]*women\b|\blady\b|\b[\w-]*mother\b|\b[\w-]*daughter\b|\bwife\b'
femaleRegex = re.compile(femaleTerms)

maleTermsArr = ['man', 'male', 'boy', 'men', 'son', 'father', 'husband']
maleTerms = r'\bman\b|\bmale\b|\bboy\b|\bmen\b|\bboys\b|\bson\b|\b[\w-]*father\b|\bhusband\b'
maleRegex = re.compile(maleTerms)
wordSet = set(['woman', 'female', 'girl', 'lady', 'man', 'male', 'boy', 'mother', 'daughter', 'son', 'father', 'husband', 'wife'])

# writes to a json file
def writeToJson(path, set):
  with open(path + '.json', 'w') as outfile:
      json.dump(list(set), outfile)

# tries to get word definition from a bunch of dictionary APIs
def getWordDefinition(word):
  def getDef(word):
    dictionary=PyDictionary()
    definition = dictionary.meaning(word)
    if isinstance(definition, dict) and 'Noun' in definition:
      defs = definition['Noun']
      if isinstance(defs, list) and len(defs) > 0:
        return defs[0]

    # wordnik dictionary
    wordApi = WordApi.WordApi(client)
    definition = (wordApi.getDefinitions(word, partOfSpeech='noun', limit=1))

    if definition is not None:
      return definition[0].text

    meaningsList = vb.meaning(word)
    if meaningsList != False:
      defs = json.loads(meaningsList)
      if (len(defs) > 0):
        definition = defs[0]['text']
        # some of the definitions have html tags
        return re.sub('<[^<]+?>', '', definition)

    try:
      # wiktionary
      parser = WiktionaryParser()
      result = parser.fetch(word)
      if (result):
        definitions = result[0].definitions[0]
        if definition.partOfSpeech == 'noun':
          return definition.text
    except:
      try:
        # owlbot api
        url = 'https://owlbot.info/api/v2/dictionary/' + word
        r = requests.get(url)
        result = (r.json())[0]
        if (result.type == 'noun' and result.definition):
          return result.definition
      except KeyboardInterrupt:
        raise
      except:
        return ' '

  searches = []
  # for example, look for beauty_queen, beauty-queen, beauty queen.
  if '_' in word:
    searches.extend([word, word.replace('_', ' '), word.replace('_', '-')])
  if (len(searches) != 0):
    for wordToSearch in searches:
      definition = getDef(wordToSearch)
      if definition is not None and definition != ' ':
        return definition
  else:
    definition = getDef(word)
  return definition

def filterWordByDefinition(definition, startIndex, endIndex):
    # remove word with any of these terms 
    def hasWordsToExclude():
        arr = r'\bhormone\b|\bsperm\b|\banimal\b|\borgan\b|\bmale or female\b|\bman or woman\b'
        rgex = re.compile(arr)
        termInDef = rgex.search(definition)
        if termInDef is not None:
            return True
        return False

    # remove entries with animals in definition
    def isThereAnimal():
        animalRegex = re.compile(animals)
        animalInDef = animalRegex.search(definition)
        if animalInDef is not None:
            return True
        return False
        
    def preprocess(sentence):
        sentence = sentence.lower()
        translator = str.maketrans('', '', string.punctuation)
        return sentence.translate(translator)

    # ignore 'the', 'a' and 'an'
    def filterTags(tags):
      new_tags = []
      for item in tags:
          word = item[0]
          if word != 'a' and word != 'an' and word != 'the':
              new_tags.append(item)
      return new_tags

    def anyExceptions(definition, tags):
        exceptions = 'name of|applied to|given to|term for'
        rgex = re.compile(exceptions)
        termInDef = rgex.search(definition)
        if termInDef is not None:
            return True
        return False

    def sentenceIsRightStructure():
        # trim
        trimmedDefinition = definition[0:endIndex]
        # remove a and an
        cleanDefinition = preprocess(trimmedDefinition)
        # part of speech tagger
        text = word_tokenize(cleanDefinition)
        tags = filterTags(nltk.pos_tag(text))

        # gendered term is the last in the string so it'll be the last in the array
        length = len(tags)
        # so the term before will be at this location
        # check if it's a preposition or verb before gendered term
        if length <= 1:
            return True
        else:
            if not anyExceptions(definition, tags):
                posOne = tags[length-2][1]
                termOne = tags[length-2][0]
                # gendered term should not be the object of a preposition
                if posOne == 'IN':
                    return False
                if termOne == 'being':
                    return False
                if length >= 2:
                    posTwo = tags[length-3][1]
                    if posTwo == 'IN':
                      return False
                return True
            else:
                return True

    if not isThereAnimal() and not hasWordsToExclude() and sentenceIsRightStructure():
        return True
    else:
        return False

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
            if (word not in wordSet and word not in discardSet):
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
        if (word not in wordSet and word not in discardSet):
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
            if (word not in wordSet and word not in discardSet):
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
      if (word not in wordSet and word not in discardSet):
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

  def addToArray(ub, pattern, gender):
    words = []
    for index, row in ub.iterrows():
      word = row['word']
      definition = row['definition']
      if (word not in wordSet and word not in discardSet):
        termsInString = pattern.search(definition)
        startIndex = termsInString.start(0)
        endIndex = termsInString.end(0)
        if filterWordByDefinition(definition, startIndex, endIndex):
          wordSet.add(word)
          words.append({
            'word': word,
            'definition': definition,
            'tags': [source],
            'gender': gender
          })
    allWords.extend(words)


  addToArray(ub[(ub['definition']).str.contains(femaleTerms, na=False)], femaleRegex, 'female')
  addToArray(ub[ub['definition'].str.contains(maleTerms, na=False)], maleRegex, 'male')
  print ('urban dic done')

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
  with open('data/animals.json') as f:
    animals = json.load(f)
    animals = ("|".join(r'\b' + animal.lower() + r'\b' for animal in animals))

  with open('words/unfiltered/all-unfiltered.json') as f:
    allWords = json.load(f)
    wordSet = set(entry['word'] for entry in allWords)
    discard = []

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
