import json
import os
from pprint import pprint
from vocabulary.vocabulary import Vocabulary as vb
from thesaurus import Word
from nltk.corpus import wordnet
import os
import re
import sys
sys.path.insert(0, 'utils/')
from get_defs import getWordDefinition
from filter_word import isValidWord
from filter_word import isValidDefinition
from filter_word import getGender
from filter_word import findPattern
import pandas as pd


with open('words/all.json') as f:
	all = json.load(f)
	wordObj = {}
	for entry in all:
		word = entry['word']
		wordObj[word] = entry
	
def writeToJson(path, set):
	with open(path + '.json', 'w') as outfile:
		json.dump(set, outfile)

def getSynonyms(word):
	syns = set()
	result = vb.synonym(word)
	if isinstance(result, list):
		result = json.loads(result)
		syns.update([synonym['text'] for synonym in result])
	result = []
	for syn in wordnet.synsets(word):
		for l in syn.lemmas():
			syns.add(l.name())
	w = Word(word)
	syns.update(w.synonyms())
	return syns

def isNoun(word):
	for ss in wordnet.synsets(word):
		pos = ss.pos()
		if ('n' in pos):
			return True
		return False


def isGendered(word, gender, definition):
	if gender == 'female':
		pattern = re.compile(r'\b[\w]*?woman\b|\bfemale\b|\b[\w]*?girl\b|\bgirls\b|\b[\w]*?women\b|\blady\b|\b[\w]*?mother\b|\b[\w]*?daughter\b|\bwife\b')
	elif gender == 'male':
		pattern = re.compile(r'\bman\b|\bmale\b|\bboy\b|\bmen\b|\bboys\b|\bson\b|\b[\w]*?father\b|\bhusband\b')
	termsInString = pattern.search(definition)
	if termsInString is not None:
		if isValidDefinition(definition, termsInString.start(0), termsInString.end(0)):
			return True
	return False


def isSameGender(word, gender, syn):
	searches = []
	if '_' in syn or '-' in syn:
		searches.extend([syn, re.sub(r'[_-]', ' ', syn)])
		if (len(searches) != 0):
			for wordToSearch in searches:
				try:
					syn_gender = wordObj[wordToSearch]['gender']
					return (wordToSearch, syn_gender == gender)
				except KeyError:
					continue
	return (syn, wordObj[syn]['gender'] == gender)


def createSets(words):
	allSets = []
	wordsInSet = set()
	wordsInSet |= set([entry['word'] for entry in all])
	end = len(words)
	for count, entry in enumerate(words):
		word = entry['word']
		gender = entry['gender']
		# create set with word
		synonyms_set = set([word])
		synonyms = getSynonyms(word)
		# add it's synonyms to set
		if (synonyms):
			for syn in synonyms:
				syn = syn.lower()
				if isValidWord(syn):
					if syn in wordsInSet:
						result = isSameGender(word, gender, syn)
						sameGender = result[1]
						syn = result[0]
						if sameGender:
							synonyms_set.add(syn)
							continue
					elif syn not in wordsInSet:
						if not isNoun(syn):
							continue
						definition = getWordDefinition(word)
						if definition != ' ':
							result = getGender(word)
							if result is not None:
								isGenderedTerm = result[0]
								if isGenderedTerm:
									all.append({
										'word': word,
										'definition': definition,
										'gender': result[1]
									})
									wordsInSet.add(word)
									continue
							if isNoun(syn) and isGendered(syn, gender, definition):
								synonyms_set.add(syn)

			if len(synonyms_set) > 1:
				allSets.append(list(synonyms_set))
	return allSets

def addSetsToWords(words, wordSets):
	for entry in words:
		word = [entry['word']]
		wordSyns = set()
		for wordSet in wordSets:
			syns = wordSet
			# check if there's a match 
			matches = set(word).intersection(set(syns))
			if len(matches) > 0:
				wordSyns |= set(syns)
		entry['syns'] = list(wordSyns)

if __name__ == "__main__":
	createSets(all)
	writeToJson('words/all', all)