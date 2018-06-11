import json
from nltk.corpus import wordnet as wn

femaleTerms = ['woman', 'female', 'girl', 'girls', 'women']
maleTerms = [' man ', ' male ', 'boy', ' men ', 'boys']

with open('data/webster/dictionary.json', 'r') as f:
	results = json.load(f)

def writeToJson(path, dictionary):
	with open(path + '.txt', 'w') as outfile:
	    json.dump(dictionary, outfile)

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

writeToJson('words/webster/female-all', femaleDict)
writeToJson('words/webster/male-all', maleDict)
