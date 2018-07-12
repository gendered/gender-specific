import json
import os
from dotenv import load_dotenv
from wordnik import *
from pprint import pprint
from vocabulary.vocabulary import Vocabulary as vb

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '.')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

with open('words/all.json') as f:
    all = json.load(f)

# wordnik
apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)
wordApi = WordApi.WordApi(client)
allSets = []
wordsInSet = set([])
def writeToJson(path, set):
	with open(path + '.json', 'w') as outfile:
	    json.dump(jsonpickle.encode(set, unpicklable=False), outfile)

def getSynonyms(word):
    synonyms = vb.synonym(word)
    if (synonyms):
        return [synonym.text for synonym in synonyms]
    return ' '


def createSets(words):
    for entry in words:
        word = entry['word']
        # create set with word
        synonyms_set = set([word])
        synonyms = getSynonyms()
        # add it's synonyms to set
        if (synonyms != ' '):
            synonyms_set.extend(synonyms)
            # wordsInSet.update(synonyms)
            allSets.append(list(synonyms_set))


createSets(all)
writeToJson('words/sets', allSets)
