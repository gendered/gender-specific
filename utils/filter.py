import json
import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.stem import *
import io
import re
import string

def filterByWord(word):
    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)
    if hasNumbers(word) or len(word.split) > 2:
        return False
    return True

def stem(a):
    p = nltk.PorterStemmer()
    [p.stem(word) for word in a]
    return a

def getCollinsTerms():
    # collins dictionary
    urls = ['https://www.collinsdictionary.com/us/word-lists/clothing-articles-of-clothing',
    'https://www.collinsdictionary.com/us/word-lists/body-parts-of-the-body',
    'https://www.collinsdictionary.com/us/word-lists/animal-collective-animals',
    'https://www.collinsdictionary.com/us/word-lists/animal-female',
    'https://www.collinsdictionary.com/us/word-lists/animal-male']
    for site in urls:
        req = urllib2.Request(site, headers=hdr)
        page = urllib2.urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        words = soup.find_all('span', attrs={'class': 'td'})
        words = stem([word.get_text() for word in words])
    return listToRegexStr(words)

def getWordnikTerms():
    # wordnik lists
    urls = ['https://www.wordnik.com/lists/clothing-or-dress', 'https://www.wordnik.com/lists/clothing--5',
     'https://www.wordnik.com/lists/clothing-textiles', 'https://www.wordnik.com/lists/genetics',
     'https://www.wordnik.com/lists/biolorgy', 'https://www.wordnik.com/lists/biology-1-unit-2--cells']

    for site in urls:
        req = urllib2.Request(site, headers=hdr)
        page = urllib2.urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        words = soup.find_all('li', attrs={'class': 'word'})
        words = [word.get_text() for word in words]
    return listToRegexStr(words)


def filterWordByDefinition(definition, startIndex, endIndex):
    # remove word with any of these terms
    def hasWordsToExclude():
        terms = r"""\bhormone\b|\bsperm\b|\banimal\b|\borgan\b|\bmale or female\b|
         [\-]?cell[\-]?|\bman or woman\b|\bmen or women\b|\banimals\b|\bplant\b|
         gamete|\begg\b|\bcell\b|\bsyndrome\b|\bsexes\b|\b'male and female\b|mammal|nucleus|""" + getCollinsTerms() + getWordnikTerms()

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

with open('data/animals.json') as f:
    animals = json.load(f)
    animals = ("|".join(r'\b' + animal.lower() + r'\b' for animal in animals))
