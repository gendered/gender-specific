import urllib.request
from bs4 import BeautifulSoup
import nltk
import json
import ssl
import re
import inflect
import string
import os

context = ssl._create_unverified_context()
terms = []
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def listToRegexStr(list):
    return ('|'.join(r'\b' + item.lower() + r'\b' for item in list))

def preprocess(sentence):
    sentence = sentence.lower()
    sentence = re.sub('[\(].*?[\)]', '', sentence)
    translator = str.maketrans('', '', string.punctuation)
    return sentence.translate(translator)

def findSingularWord(word):
    p = inflect.engine()
    return p.singular_noun(word)

def getWordnikLists():
    # wordnik dictionary
    urls = ['https://www.wordnik.com/lists/biology-1-unit-2--cells',
    'https://www.wordnik.com/lists/biolorgy',
    'https://www.wordnik.com/lists/genetics']
    return scrapePage(urls, 'li.word > a')

def getCollinsLists():
    # collins dictionary
    urls = ['https://www.collinsdictionary.com/us/word-lists/clothing-articles-of-clothing',
    'https://www.collinsdictionary.com/us/word-lists/body-parts-of-the-body',
    'https://www.collinsdictionary.com/us/word-lists/animal-female',
    'https://www.collinsdictionary.com/us/word-lists/animal-male']
    return scrapePage(urls, 'span.td > a')

def scrapePage(urls, selector):
    s = ''
    for site in urls:
        try:
            req = urllib.request.Request(site, headers=hdr)
            page = urllib.request.urlopen(req, context=context)
            soup = BeautifulSoup(page, 'html.parser')
            words = soup.select(selector)
            for index, word in enumerate(words):
                word = word.get_text()
                if ' ' in word:
                    arr = word.split('or')
                    word = arr[0]
                word = preprocess(word)
                words[index] = word
            s += listToRegexStr(words)
        except urllib.request.HTTPError as e:
            print('HTTPError = ' + str(e.code))
        except urllib.request.URLError as e:
            print('URLError = ' + str(e.reason))
    return s

pattern = r"""
\bhormone\b|\bsperm\b|\banimal\b|\borgan\b|\bmale or female\b|[\-]?cell[\-]?|
\bman or woman\b|\bmen or women\b|\banimals\b|\bplant\b|gamete|
\bsyndrome\b|\bsexes\b|\bmale and female\b|mammal|nucleus|"""

#
# with open('../data/animals.json') as f:
#     animals = json.load(f)
#     pattern += listToRegexStr(animals)
#
# pattern += getCollinsLists() + getWordnikLists()
#
# f = open('pattern.txt','w')
# f.write(pattern)
# f.close()
