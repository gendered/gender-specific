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
import requests
from wiktionaryparser import WiktionaryParser
import io
from nltk.stem import *
import re

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

# wordnik api stuff
apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)

femaleTermsArr = ['woman', 'female', 'girl', 'lady', 'women', 'mother', 'daughter', 'wife']
femaleTerms = '\bwoman\b|\bfemale\b|\bgirl\b|\bgirls\b|\bwomen\b|\blady\b|\bmother\b|\bdaughter\b|\bwife\b'
femaleRegex = re.compile(femaleTerms)

maleTermsArr = ['man', 'male', 'boy', 'men', 'son', 'father', 'husband']
maleTerms = '\bman\b|\bmale\b|\bboy\b|\bmen\b|\bboys\b|\bson\b|\bfather\b|\bhusband\b'
maleRegex = re.compile(maleTerms)
allWords = []
wordSet = set(['woman', 'female', 'girl', 'lady', 'man', 'male', 'boy', 'mother', 'daughter', 'son', 'father', 'husband', 'wife'])

def writeToJson(path, set):
	with open(path + '.json', 'w') as outfile:
	    json.dump(list(set), outfile)

def getWordDefinition(word):

	def getDef(word):
		dictionary=PyDictionary()
		definition = dictionary.meaning(word)
		if isinstance(definition, dict) and 'Noun' in definition:
			return definition['Noun'][0]

		# wordnik dictionary
		wordApi = WordApi.WordApi(client)
		definition = (wordApi.getDefinitions(word, partOfSpeech='noun', limit=1))

		if definition is not None:
			return definition[0].text

		try:
			# owlbot api
			url = 'https://owlbot.info/api/v2/dictionary/' + word
			r = requests.get(url)
			result = (r.json())[0]
			if (result.type == 'noun' and result.definition):
				return result.definition
		except:
			try:
				# wiktionary
				parser = WiktionaryParser()
				result = parser.fetch(word)
				if (result):
					definitions = result[0].definitions[0]
					if definition.partOfSpeech == 'noun':
						return definition.text
			except KeyboardInterrupt:
				raise
			except:
				return ' '

	searches = []
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
				if (word not in wordSet):
					termsInString = pattern.search(definition)
					if termsInString is not None:
						wordSet.add(word)
						words.append(
						{
							'word': word,
							'definition': definition,
							'gender': gender,
							'tags': [source],
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
				if (word not in wordSet):
					# check if it's a noun
					if ('tags' in result):
						if ('n' in result['tags']):
							if ('defs' in result):
								definition = result['defs']
							else:
								definition = getWordDefinition(word)
							if (definition != ' '):
								termsInString = pattern.search(definition)
								if termsInString is not None:
									wordSet.add(word)
									words.append({
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
			termsInString = pattern.search(definition)
			if termsInString is not None:
				result = result.lower()
				if (result not in wordSet):
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
							break

		allWords.extend(words)

	bucket(femaleRegex, 'female')
	bucket(maleRegex, 'male')
	print ('webster done')

def getGSFull():
	with open('data/gender_specific_full.json', 'r') as f:
		results = json.load(f)

	# all words in this file are gendered, so put the ones we can't get definitions for
	# in a separate file we will address later
	def bucket(pattern, gender):
		words = []
		for result in results:
			result = result.lower()
			if (result not in wordSet):
				definition = getWordDefinition(result)
				if (definition is not None and definition != ' '):
					termsInString = pattern.search(definition)
					if termsInString is not None:
						words.append({
							'word': result,
							'definition': definition,
							'gender': gender
						})
						wordSet.add(result)
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

	def addToArray(ub, gender):
		words = []
		for index, row in ub.iterrows():
			word = row['word']
			if (word not in wordSet):
				wordSet.add(word)
				words.append({
					'word': word,
					'definition': row['definition'],
					'tags': [source],
					'gender': gender
				})
		allWords.extend(words)


	addToArray(ub[(ub['definition']).str.contains(femaleTerms, na=False)], 'female')
	addToArray(ub[ub['definition'].str.contains(maleTerms, na=False)], 'male')
	print ('urban dic done')

def addTerms(terms, gender):
	for word in terms:
		definition = getWordDefinition(word)
		wordSet.add(word)
		allWords.append({
			'word': word,
			'definition': definition,
			'gender': gender,
			'source': 'wordnik'
		})

addTerms(['woman', 'girl', 'lady', 'mother', 'daughter', 'wife'], 'female')
addTerms(['man', 'boy', 'son', 'father', 'husband'], 'male')
getWebster()
getWordnik()
getDatamuse()
getGSFull()
# getUrbanDictionary()

writeToJson('words/unfiltered/all-unfiltered', allWords)
