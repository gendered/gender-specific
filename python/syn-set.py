import json
import os
from dotenv import load_dotenv
from wordnik import *
from pprint import pprint
import jsonpickle

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

with open('words/unfiltered/all.json') as f:
    female_all = json.load(f)
    female_all = jsonpickle.decode(female_all)


with open('words/male-all.json') as f:
    male_all = json.load(f)
    male_all = jsonpickle.decode(male_all)

# wordnik
apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)
wordApi = WordApi.WordApi(client)

femaleAll = []
maleAll = []
wordsInSet = set()

def createSets(words, arr):
    for word in words:
        # check if it doesn't exist in a set already
        if (word in wordsInSet):
            continue
        else:
            wordsInSet.add(word)
            # create set with word
            synonyms_set = [word]
            # add it's synonyms to set
            results = wordApi.getRelatedWords(word, relationshipTypes='synonym')
            if (results):
                synonyms = results[0].words
                synonyms_set.extend(synonyms)
                # wordsInSet.update(synonyms)
                arr.append(synonyms_set)

def writeToJson(path, set):
	with open(path + '.json', 'w') as outfile:
	    json.dump(jsonpickle.encode(set, unpicklable=False), outfile)

createSets(female_all, femaleAll)
print (femaleAll)
createSets(male_all, maleAll)
print (maleAll)

writeToJson('words/female-set', femaleAll)
writeToJson('words/male-set', maleAll)
