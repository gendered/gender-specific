import json
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.stem import *
import io
import re
import string
import exclude_words
import os 

def searchTextForGenderedTerm(text, gender=None):
    fs = r"""\b[\w]*?woman\b|\bfemale\b|\b[\w]*?girl\b|\bgirls\b|\b[\w]*?women\b|\blady\b|\b[\w-]*?mother\b|\b[\w]*?daughter\b|\bwife\b"""
    ms = r"""\bman\b|\b[\w]*?boy\b|\bmen\b|\b[\w]*?son\b|\b[\w-]*?father\b|\b[\w]*?husband\b|\bmale\b|\bboys\b"""
    f_pattern = re.compile(fs)
    m_pattern = re.compile(ms)
    femalePosition = f_pattern.search(text)
    malePosition = m_pattern.search(text)
    if gender is None or (femalePosition is not None and malePosition is not None):
        gender = getEarlierIndex(femalePosition, malePosition)
    if gender == 'female' and femalePosition is not None:
        return (True, gender, femalePosition)
    elif gender == 'male' and malePosition is not None:
        return (True, gender, malePosition)
    return None

def getEarlierIndex(femalePosition, malePosition):
    if femalePosition is None and malePosition is None:
        return None
    if femalePosition is not None and malePosition is not None:
        femaleStart = femalePosition.start(0)
        maleStart = malePosition.start(0)
        if femaleStart < maleStart:
            return 'female'
        return 'male'
    elif malePosition is None:
        return 'female'
    elif femalePosition is None:
        return 'male'


def isValidWord(word):
    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)
    if hasNumbers(word) or not word[0].isalpha():
        return False
    return True

def preprocess(sentence):
    sentence = sentence.lower()
    translator = str.maketrans('', '', string.punctuation)
    return sentence.translate(translator)

def isValidDefinition(definitions, startIndex, endIndex):

    # remove word with any of these terms
    def hasWordsToExclude(definition):
        path = os.getcwd() + '/utils/pattern.txt'
        f = open(path, 'r')
        terms = f.read().replace('\n', '')
        rgex = re.compile(terms)
        termInDef = rgex.search(definition)
        if termInDef is not None:
            return True
        return False

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

    def sentenceIsRightStructure(definition):
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

    def isTermPossessive(definition):
        if len(definition) != endIndex:
            last = definition[endIndex]
            if last == "'" or last == '-':
                return True
        return False
    
    def checkValidity(definition):        
        if not hasWordsToExclude(definition) and not isTermPossessive(definition) and sentenceIsRightStructure(definition):
            return True
        else:
            return False

   if isinstance(definition, list) and len(defs) > 0:
    validDefinitions = []
    for definition in definitions:
        if checkValidity(definition):
            validDefinitions.append(definition)
    if len(validDefinitions) > 0:
        return (True, validDefinitions)
    else:
        return (False, None)

