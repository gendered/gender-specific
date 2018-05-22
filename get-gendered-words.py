from wordnik import *
import json

apiUrl = 'http://api.wordnik.com/v4'
apiKey = 'c0706d70c102054fb6a56bb8f070f1895ba309b3140771469'
client = swagger.ApiClient(apiKey, apiUrl)

wordsApi = WordsApi.WordsApi(client)

terms = ['woman', 'man', 'female', 'male', 'boy', 'girl']
dict = dict.fromkeys(terms)

for term in dict:
	results = wordsApi.reverseDictionary(term,  includePartOfSpeech='noun').results
	words = {}
	for result in results:
		words[result.word] = result.text
	dict[term] = words

for term in dict:
	print term
	print len(dict[term])
	with open('words/' + term + '.txt', 'w') as outfile:  
	    json.dump(dict[term], outfile)