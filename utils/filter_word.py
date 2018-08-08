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

def isValidWord(word):
    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)
    if hasNumbers(word) or len(word.split) > 2:
        return False
    return True

def preprocess(sentence):
    sentence = sentence.lower()
    translator = str.maketrans('', '', string.punctuation)
    return sentence.translate(translator)

def isValidDefinition(definition, startIndex, endIndex):
    # remove word with any of these terms
    def hasWordsToExclude():
        f = open('pattern.txt','r')
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

    if not hasWordsToExclude() and sentenceIsRightStructure():
        return True
    else:
        return False
