import json
import os
from pprint import pprint
from vocabulary.vocabulary import Vocabulary as vb
from nltk.corpus import wordnet
import os
import re
import sys
sys.path.insert(0, 'utils/')
from get_defs import getWordDefinition
from filter_word import isValidWord
from filter_word import isValidDefinition
import pandas as pd


with open('words/all.json') as f:
	all = json.load(f)
	wordObj = {}
	for entry in all:
		word = entry['word']
		wordObj[word] = entry

allSets = {}
wordsInSet = set()
wordsInSet |= set([entry['word'] for entry in all])

def writeToJson(path, set):
	with open(path + '.json', 'w') as outfile:
		json.dump(set, outfile)

def getSynonyms(word):
	synonymsOne = vb.synonym(word)
	synonymsTwo = []
	if isinstance(synonymsOne, list):
		synonymsOne = json.loads(synonyms)
		synonymsOne = [synonym['text'] for synonym in synonyms]
	for syn in wordnet.synsets(word):
		for l in syn.lemmas():
			synonymsTwo.append(l.name())
	if isinstance(synonymsTwo, list) and isinstance(synonymsOne, list):
		return list(set().union(synonymsOne, synonymsTwo))
	elif isinstance(synonymsTwo, list):
		return synonymsTwo
	elif isinstance(synonymsOne, list):
		return synonymsOne
	return ' '

def isNoun(word):
	for ss in wordnet.synsets(word):
		pos = ss.pos()
		if ('n' in pos):
			return True
		return False


def isGendered(word, gender):
	if isValidWord(word):
		definition = getWordDefinition(word)
		if gender == 'female':
			pattern = re.compile(r'\b[\w]*?woman\b|\bfemale\b|\b[\w]*?girl\b|\bgirls\b|\b[\w]*?women\b|\blady\b|\b[\w]*?mother\b|\b[\w]*?daughter\b|\bwife\b')
		elif gender == 'male':
			pattern = re.compile(r'\bman\b|\bmale\b|\bboy\b|\bmen\b|\bboys\b|\bson\b|\b[\w]*?father\b|\bhusband\b')
		termsInString = pattern.search(definition)
		if termsInString is not None:
			if isValidDefinition(definition, termsInString.start(0), termsInString.end(0)):
				all.append({
					'word': word,
					'definition': definition,
					'gender': gender
				})
				wordsInSet.add(word)
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
					return syn_gender == gender
				except KeyError:
					continue
	return wordObj[syn]['gender'] == gender


def createSets(words):
	end = len(words)
	i = 0
	for count, entry in enumerate(words[index:end]):
		word = entry['word']
		gender = entry['gender']
		# create set with word
		synonyms_set = set([word])
		synonyms = getSynonyms(word)
		# add it's synonyms to set
		if (synonyms != ' ' and synonyms != []):
			for syn in synonyms:
				syn = syn.lower()
				if syn in wordsInSet and isSameGender(word, gender, syn):
					synonyms_set.add(syn)
				elif syn not in wordsInSet:
					if isNoun(syn) and isGendered(syn, gender):
						synonyms_set.add(syn)
			if len(synonyms_set) > 1:
				print(synonyms_set)
				allSets[str(i)] = (list(synonyms_set))
				i += 1

if __name__ == "__main__":
	createSets(all)
	writeToJson('words/word-sets', allSets)
	writeToJson('words/all', all)