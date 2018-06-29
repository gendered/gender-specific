from dotenv import load_dotenv
from wordnik import *
import json
import os

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)
wordsApi = WordsApi.WordsApi(client)
femaleTerms = ['woman', 'female', 'girl', 'girls', 'women']
maleTerms = [ 'man', 'male', 'boy', 'men', 'boys']

def writeToJson(path, dictionary):
	with open(path + '.txt', 'w') as outfile:
	    json.dump(dictionary, outfile)

def callApi(terms):
	words = {}
	for term in terms:
		results = wordsApi.reverseDictionary(term,  includePartOfSpeech='noun', limit=10000).results
		for result in results:
			words[result.word] = result.text
	return words

femaleDict = callApi(dict.fromkeys(femaleTerms))
print (len(femaleDict))
maleDict = callApi(dict.fromkeys(maleTerms))
print (len(maleDict))
writeToJson('words/wordnik/female-all', femaleDict)
writeToJson('words/wordnik/male-all', maleDict)
