from datamuse import datamuse
from wordnik import *
import json

api = datamuse.Datamuse()

femaleTerms = ['woman', 'female', 'girl', 'girls', 'women']
maleTerms = [ 'man', 'male', 'boy', 'men', 'boys']

def writeToJson(path, dictionary):
	with open(path + '.txt', 'w') as outfile:
	    json.dump(dictionary, outfile)

api = datamuse.Datamuse()

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
						words[word] = 'no def for now'
	return words

femaleDict = callApi(dict.fromkeys(femaleTerms))
maleDict = callApi(dict.fromkeys(maleTerms))

writeToJson('words/datamuse/female-all', femaleDict)
writeToJson('words/datamuse/male-all', maleDict)
