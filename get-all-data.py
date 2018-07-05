from dotenv import load_dotenv
from wordnik import *
from datamuse import datamuse
import json
import os
from nltk.corpus import wordnet as wn
import collections
from PyDictionary import PyDictionary
import pandas as pd
import urbandictionary as ud

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

femaleTerms = ['woman', 'female', 'girl', 'girls', 'women', 'lady']
maleTerms = [ 'man', 'male', 'boy', 'men', 'boys']

femaleAll =  set(['woman', 'female', 'girl', 'girls', 'women', 'lady'])
maleAll = set(['man', 'male', 'boy', 'men', 'boys'])

def writeToJson(path, set):
	with open(path + '.json', 'w') as outfile:
	    json.dump(list(set), outfile)

# wordnik
apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)
wordApi = WordApi.WordApi(client)

def getWordnik():
	wordsApi = WordsApi.WordsApi(client)

	def callApi(terms, set):
		words = []
		for term in terms:
			reverseDictionary = wordsApi.reverseDictionary(term,  includePartOfSpeech='noun', limit=10000).results
			for result in reverseDictionary:
				if (result not in set):
					word = result.word
					words.append((result.word).lower())
		return words

	female = callApi(dict.fromkeys(femaleTerms), femaleAll)
	male = callApi(dict.fromkeys(maleTerms), maleAll)
	femaleAll.update(female)
	maleAll.update(male)
	print ('wordnik done')

# datamuse

def getDatamuse():
	api = datamuse.Datamuse()

	def callApi(terms, set):
		words = []
		for term in terms:
			results = api.words(ml=term, max=1000, md='dp')
			for result in results:
				# check if it's a noun
				if ('tags' in result):
					if ('n' in result['tags']):
						word = result['word'].lower()
						if (word not in set):
							words.append(word)
		return words

	female = callApi(dict.fromkeys(femaleTerms), femaleAll)
	male = callApi(dict.fromkeys(maleTerms), maleAll)
	femaleAll.update(female)
	maleAll.update(male)
	print ('datamuse done')

def getWebster():
	with open('data/webster/dictionary.json', 'r') as f:
		results = json.load(f)
	maleTerms = [' man ', ' male ', 'boy', ' men ', 'boys']

	def bucket(terms, set):
		words = []
		for term in terms:
			for result in results:
				if term in results[result]:
					result = result.lower()
					if (result not in set):
						# get part of speech
						for ss in wn.synsets(result):
							pos = ss.pos()
							if ('n' in pos):
								words.append(result)
								break
		return words

	female = bucket(dict.fromkeys(femaleTerms), femaleAll)
	male = bucket(dict.fromkeys(maleTerms), maleAll)
	femaleAll.update(female)
	maleAll.update(male)
	print ('webster done')

def getGSFull():
	with open('data/gender_specific_full.json', 'r') as f:
			results = json.load(f)
			for n, i in enumerate(results):
				results[n] = (i.replace('_', ' ').lower())
	dictionary=PyDictionary()

	with open('data/gender_specific_full.json', 'r') as f:
		results = json.load(f)

	# all words in this file are gendered, so put the ones we can't get definitions for
	# in a separate file we will address later
	unknown_gender = set([])
	def bucket(terms, set):
		words = []
		for result in results:
			result = result.lower()
			if (result not in set):
				definition = dictionary.meaning(result.replace('_', ' '))
				if (isinstance(definition, dict) and 'Noun' in definition):
					definition = definition['Noun']
				else:
					dictionary.meaning(result.replace('_', '-'))
					if (isinstance(definition, dict) and 'Noun' in definition):
						definition = definition['Noun']
					else:
						definition = (wordApi.getDefinitions(result.replace('_', ' '), partOfSpeech='noun', limit=1))
						if (definition is not None):
							definition = definition[0].text
						else:
							definition = (wordApi.getDefinitions(result.replace('_', '-'), partOfSpeech='noun', limit=1))
							if (definition is not None):
								definition = definition[0].text
							else:
								unknown_gender.add(result)
								continue
				for term in terms:
					if (definition is not None and term in definition):
						words.append(result)
						break
		return words

	female = bucket(dict.fromkeys(femaleTerms), femaleAll)
	male = bucket(dict.fromkeys(maleTerms), maleAll)
	femaleAll.update(female)
	maleAll.update(male)
	writeToJson('words/unknown', unknown_gender)

	print ('gender specific done')

def getUrbanDictionary():
	with open('data/urban/urban-female.json', 'r') as f:
		male = json.load(f)
	with open('data/urban/urban-male.json', 'r') as f:
		female = json.load(f)

	femaleAll.update(female)
	maleAll.update(male)

	print ('urban dic done')

getWebster()
getWordnik()
getDatamuse()
getUrbanDictionary()
getGSFull()

writeToJson('words/female-all', femaleAll)
writeToJson('words/male-all', maleAll)
