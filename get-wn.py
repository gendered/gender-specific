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
terms = ['woman', 'man', 'female', 'male', 'boy', 'girl', 'women', 'men', 'girls', 'boys']
dict = dict.fromkeys(terms)

for term in dict:
	results = wordsApi.reverseDictionary(term,  includePartOfSpeech='noun', limit=10000).results
	words = {}
	for result in results:
		words[result.word] = result.text
	dict[term] = words

for term in dict:
	print (len(dict[term]))
	with open('words/wordnik/' + term + '.txt', 'w') as outfile:  
	    json.dump(dict[term], outfile)