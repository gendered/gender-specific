import json
from gensim.models import KeyedVectors, word2vec
filename = 'GoogleNews-vectors-negative300.bin'
model = KeyedVectors.load_word2vec_format(filename, binary=True)
import nltk

with open('words/unfiltered/all-unfiltered.json') as f:
    all_words = json.load(f)

with open('data/animals.json') as f:
    animals = json.load(f)

def writeToJson(path, arr):
	with open(path + '.json', 'w') as outfile:
	    json.dump(arr, outfile)

discard = []
not_strong = []
all = []

def filterWords(arr):
    newArr = []
    for entry in arr:
        definition = entry['definition']
        if ('tags' in entry):
            tags = entry['tags']
        if not isThereAnimal(definition):
            if isRightStructure(definition):
                if word in model.vocab:
                    sims = checkDistance(entry)
                    f_sim = sims['f_sim']
                    f_sim = sims['m_sim']

                    if (f_sim < 0.1 and m_sim < 0.1):
                        not_strong.append(entry)
                        continue
                    elif f_sim > 0.1 and f_sim > m_sim:
                        entry['gender'] = 'female'
                        newArr.append(entry)
                    elif m_sim > f_sim and m_sim > 0.1:
                        entry['gender'] = 'male'
                        newArr.append(entry)
                else:
                    if tags and 'urban-dic' not in tags:
                        discard.append(entry)
                    else:
                        newArr.append(entry)

    # remove entries with animals in definition
    def isThereAnimal(definition):
        foundAnimal = False
        for animal in animals:
            animal = animal.lower()
            if animal in definition:
                return True
        return False

    def checkSentenceStructure():


    def checkDistance(entry):
        f_term = 'woman'
        m_term = 'man'
        word = entry['word']
        gender = entry['gender']
        f_sim = model.similarity(word, f_term)
        m_sim = model.similarity(word, m_term)
        return {
            'f_sim': f_sim,
            'm_sim': m_sim
        }

# mentions of animal in definition
# any animal in definition
femaleTerms = ['woman', 'female', 'girl', 'girls', 'women', 'lady']
maleTerms = [ 'man', 'male', 'boy', 'men', 'boys', 'son', 'father', 'husband']


filterWords(all_words)
writeToJson('words/discard', list(discard))
writeToJson('words/not_strong', list(not_strong))
writeToJson('words/all', all)
