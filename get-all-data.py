from dotenv import load_dotenv
from wordnik import *
from datamuse import datamuse
import json
import os
from nltk.corpus import wordnet as wn
import collections
import jsonpickle

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

femaleTerms = ['woman', 'female', 'girl', 'girls', 'women', 'lady']
maleTerms = [ 'man', 'male', 'boy', 'men', 'boys']

maleAll =  set(['woman', 'female', 'girl', 'girls', 'women', 'lady'])
femaleAll = set(['man', 'male', 'boy', 'men', 'boys'])

def writeToJson(path, set):
	with open(path + '.json', 'w') as outfile:
	    json.dump(jsonpickle.encode(set, unpicklable=False), outfile)

# wordnik
apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)
wordApi = WordApi.WordApi(client)

def getWordnik():
    wordsApi = WordsApi.WordsApi(client)

    def callApi(terms):
        words = []
        for term in terms:
            reverseDictionary = wordsApi.reverseDictionary(term,  includePartOfSpeech='noun', limit=10000).results
            for result in reverseDictionary:
                words.append(result.word)
        return words

    femaleSet = callApi(dict.fromkeys(femaleTerms))
    maleSet = callApi(dict.fromkeys(maleTerms))
    femaleAll.update(femaleSet)
    maleAll.update(maleSet)
    print ('wordnik done')

# datamuse

def getDatamuse():
    api = datamuse.Datamuse()

    def callApi(terms):
        words = []
        for term in terms:
            results = api.words(ml=term, max=1000, md='dp')
            for result in results:
                # check if it's a noun
                if ('tags' in result):
                    if ('n' in result['tags']):
                        word = result['word']
                        words.append(word)
        return words

    femaleSet = callApi(dict.fromkeys(femaleTerms))
    maleSet = callApi(dict.fromkeys(maleTerms))
    femaleAll.update(femaleSet)
    maleAll.update(maleSet)
    print ('datamuse done')

def getWebster():
    with open('data/webster/dictionary.json', 'r') as f:
        results = json.load(f)

    maleTerms = [' man ', ' male ', 'boy', ' men ', 'boys']

    def callApi(terms):
        words = []
        for term in terms:
            for result in results:
                if term in results[result]:
                    # get part of speech
                    for ss in wn.synsets(result):
                        pos = ss.pos()
                        if ('n' in pos):
                            words.append(result)
        return words

    femaleSet = callApi(dict.fromkeys(femaleTerms))
    maleSet = callApi(dict.fromkeys(maleTerms))
    femaleAll.update(femaleSet)
    maleAll.update(maleSet)
    print ('webster done')


getWebster()
getWordnik()
getDatamuse()

#
writeToJson('words/female-all', femaleAll)
writeToJson('words/male-all', maleAll)
