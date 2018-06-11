from dotenv import load_dotenv
from wordnik import *
from datamuse import datamuse
import json
import os
from nltk.corpus import wordnet as wn
import collections

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

femaleTerms = ['woman', 'female', 'girl', 'girls', 'women']
maleTerms = [ 'man', 'male', 'boy', 'men', 'boys']

maleAll =  {}
femaleAll = {}

def writeToJson(path, dictionary):
	with open(path + '.txt', 'w') as outfile:
	    json.dump(dictionary, outfile)

def appendToDictionary(d, super_dict):
	for k, v in d.items():
		if (k not in super_dict):
			super_dict[k] = v

# wordnik
apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)

def getWordnik():
	wordsApi = WordsApi.WordsApi(client)

	def callApi(terms):
		words = {}
		for term in terms:
			results = wordsApi.reverseDictionary(term,  includePartOfSpeech='noun', limit=10000).results
			for result in results:
				words[result.word] = result.text
		return words

	femaleDict = callApi(dict.fromkeys(femaleTerms))
	maleDict = callApi(dict.fromkeys(maleTerms))

	appendToDictionary(maleDict, maleAll)
	appendToDictionary(femaleDict, femaleAll)

	writeToJson('words/wordnik/female-all', femaleDict)
	writeToJson('words/wordnik/male-all', maleDict)
	print ('wordnik done')

# datamuse

def getDatamuse():

	api = datamuse.Datamuse()
	wordApi = WordApi.WordApi(client)

	def callApi(terms):
		words = {}
		for term in terms:
			results = api.words(ml=term, max=1000, md='dp')
			for result in results:
				# check if it's a noun
				if ('tags' in result):
					if ('n' in result['tags']):
						word = result['word']
						if ('defs' in result):
							definition = result['defs']
							words[word] = definition
						else:
							# to-do: get definition if it's not there
							definition = wordApi.getDefinitions(word, partOfSpeech='noun', limit=1)
							if (definition is not None):
								words[word] = definition[0].text
							else:
								syns = wn.synsets(word)
								if syns:
									words[word] = syns[0].definition()
								else:
									continue
		return words

	femaleDict = callApi(dict.fromkeys(femaleTerms))
	maleDict = callApi(dict.fromkeys(maleTerms))

	appendToDictionary(maleDict, maleAll)
	appendToDictionary(femaleDict, femaleAll)

	writeToJson('words/datamuse/female-all', femaleDict)
	writeToJson('words/datamuse/male-all', maleDict)

	print ('datamuse done')

def getWebster():
	with open('data/webster/dictionary.json', 'r') as f:
		results = json.load(f)

	maleTerms = [' man ', ' male ', 'boy', ' men ', 'boys']

	def callApi(terms):
		words = {}
		for term in terms:
			for result in results:
				if term in results[result]:
					# get part of speech
					for ss in wn.synsets(result):
						pos = ss.pos()
						if ('n' in pos):
							words[result] = results[result]
		return words

	femaleDict = callApi(dict.fromkeys(femaleTerms))
	maleDict = callApi(dict.fromkeys(maleTerms))

	appendToDictionary(maleDict, maleAll)
	appendToDictionary(femaleDict, femaleAll)

	print ('webster done')
	writeToJson('words/webster/female-all', femaleDict)
	writeToJson('words/webster/male-all', maleDict)
#
getWebster()
getWordnik()
getDatamuse()

#
writeToJson('words/female-all', femaleAll)
writeToJson('words/male-all', maleAll)
