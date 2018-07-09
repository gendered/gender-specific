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

# wordnik api stuff
apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)


femaleTerms = ['woman', 'female', 'girl', 'girls', 'women', 'lady']
maleTerms = [ 'man', 'male', 'boy', 'men', 'boys']
allWords = set(['woman', 'female', 'girl', 'lady', 'man', 'male', 'boy'])

def writeToJson(path, set):
	with open(path + '.json', 'w') as outfile:
	    json.dump(list(set), outfile)

def getWordDefinition(word):
	dictionary=PyDictionary()
	wordApi = WordApi.WordApi(client)
	def checkIfValid(def):
		if isinstance(def, dict) and 'Noun' in definition:
			return True
		elif def is not None:
			return True
		else:
			return False

	def getDef(word):
		definition = dictionary.meaning(word)
		if (checkIfValid(definition)):
			return definition['Noun']
		else:
			definition = (wordApi.getDefinitions(word, partOfSpeech='noun', limit=1))
			if checkIfValid(def):
				return definition[0].text
			else:
				return ' '

	searches = []
	if '_' in word:
		searches.extend(word, word.replace('_', ' '), word.replace('_', '-'))
	if (len(searches) != 0):
		for (wordToSearch in searches):
			def = getDef(wordToSearch)
			if (def is not None and def != ' ')
				return def
	else:
		def = getDef(word)
	return def

def getWordnik():
	wordsApi = WordsApi.WordsApi(client)
	source = 'wordnik'
	def callApi(terms, gender):
		words = []
		for term in terms:
			reverseDictionary = wordsApi.reverseDictionary(term,  includePartOfSpeech='noun', limit=10000).results
			for result in reverseDictionary:
				if (result not in allWords):
					word = result.word.lower()
					definition = result.text
					words.append(
					{
						'word': word,
						'definition': definition,
						'gender': gender,
						'source': source
					})
		allWords.update(words)

	callApi(dict.fromkeys(femaleTerms), 'female')
	callApi(dict.fromkeys(maleTerms), 'male')
	print ('wordnik done')

# datamuse

def getDatamuse():
	api = datamuse.Datamuse()
	source = 'datamuse'
	def callApi(terms, gender):
		words = []
		for term in terms:
			results = api.words(ml=term, max=1000, md='dp')
			for result in results:
				word = result['word'].lower()
				if (word not in allWords):
					# check if it's a noun
					if ('tags' in result):
						if ('n' in result['tags']):
							if ('defs' in result):
								definition = result['defs']
							else:
								definition = getWordDefinition(word)
							words.append({
								'word': word,
								'definition': definition,
								'gender': gender,
								'source': source
							})
		allWords.update(words)

	callApi(dict.fromkeys(femaleTerms), 'female')
	callApi(dict.fromkeys(maleTerms), 'male')
	print ('datamuse done')

def getWebster():
	with open('data/webster/dictionary.json', 'r') as f:
		results = json.load(f)
	maleTerms = [' man ', ' male ', 'boy', ' men ', 'boys']
	source = 'webster'
	def bucket(terms, gender):
		words = []
		for term in terms:
			for result in results:
				definition = results[result]
				if term in definition:
					result = result.lower()
					if (result not in allWords):
						# get part of speech
						for ss in wn.synsets(result):
							pos = ss.pos()
							if ('n' in pos):
								words.append({
									'word': word,
									'definition': definition,
									'gender': gender,
									'source': source
								})
								break
		allWords.update(words)


	bucket(dict.fromkeys(femaleTerms), 'female')
	bucket(dict.fromkeys(maleTerms), 'male')
	print ('webster done')

def getGSFull():
	with open('data/gender_specific_full.json', 'r') as f:
		results = json.load(f)

	# all words in this file are gendered, so put the ones we can't get definitions for
	# in a separate file we will address later
	def bucket(terms, gender):
		words = []
		for result in results:
			result = result.lower()
			if (result not in allWords):
				definition = getWordDefinition(result)
				if (definition is not None and definition != ' '):
					hasGenderedTerm = False
					for term in terms:
						if (term in definition):
							hasGenderedTerm = True
							words.append({
								'word': word,
								'definition': definition,
								'gender': gender
							})
							break
					if (hasGenderedTerm == False):
						words.append({
							'word': word,
							'definition': definition,
							'gender': 'unknown'
						})
				else:
					words.append({
						'word': word,
						'definition': '',
						'gender': 'unknown'
					})
		allWords.update(words)

	bucket(dict.fromkeys(femaleTerms), 'female')
	bucket(dict.fromkeys(maleTerms), 'male')
	print ('gender specific done')

getWebster()
getWordnik()
getDatamuse()
getGSFull()

writeToJson('words/filtered/all-unfiltered', allWords)
