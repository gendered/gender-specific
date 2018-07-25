import json
import os
from pprint import pprint
from vocabulary.vocabulary import Vocabulary as vb
from wordnik import *
from dotenv import load_dotenv
import os

# wordnik api stuff
apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)

with open('words/filtered/all.json') as f:
    all = json.load(f)

allSets = []
wordsInSet = set([])
def writeToJson(path, set):
	with open(path + '.json', 'w') as outfile:
	    json.dump(jsonpickle.encode(set, unpicklable=False), outfile)

def getSynonyms(word):
    synonyms = vb.synonym(word)
    if isinstance(synonyms, list):
        synonyms = json.loads(synonyms)
        return [synonym['text'] for synonym in synonyms]
    wordApi = WordApi.WordApi(client)
    synonyms = wordApi.getRelatedWords(word, relationshipTypes='synonym')
    if isinstance(synonyms, list):
        return synonyms[0].words
    return ' '


def createSets(words):
    for entry in words:
        word = entry['word']
        # create set with word
        synonyms_set = set([word])
        synonyms = getSynonyms(word)
        # add it's synonyms to set
        if (synonyms != ' '):
            synonyms_set.extend(synonyms)
            # wordsInSet.update(synonyms)
            allSets.append(list(synonyms_set))


createSets(all)
writeToJson('words/sets', allSets)
