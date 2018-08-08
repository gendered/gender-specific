import urllib.request
from bs4 import BeautifulSoup
import nltk
import json
import ssl
import re
import inflect
import string

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
    'https://www.wordnik.com/lists/genetics',
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
    for site, i in enumerate(urls):
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
        except urllib.request.URLError:
            raise MyException("There was an error: %r" % e)
    return s

patternOne = r"""
\bhormone\b|\bsperm\b|\banimal\b|\borgan\b|\bmale or female\b|[\-]?cell[\-]?|
\bman or woman\b|\bmen or women\b|\banimals\b|\bplant\b|gamete|\begg\b|\bcell\b|
\bsyndrome\b|\bsexes\b|\b'male and female\b|mammal|nucleus|"""

patternTwo = getCollinsLists() + getWordnikLists()

f = open('pattern.txt','w')
f.write(patternOne + patternTwo)
f.close()
