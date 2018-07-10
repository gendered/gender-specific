import json
from gensim.models import KeyedVectors
filename = 'GoogleNews-vectors-negative300-SLIM.bin'
model = KeyedVectors.load_word2vec_format(filename, binary=True)

with open('words/unfiltered/all-unfiltered.json') as f:
    all_words = json.load(f)

with open('words/discard.json') as f:
    discard = json.load(f)

def writeToJson(path, arr):
	with open(path + '.json', 'w') as outfile:
	    json.dump(arr, outfile)

discard = set([])
not_strong = set([])
all = []

def checkDistance(arr):
    f_term = 'woman'
    m_term = 'man'
    newArr = []
    for entry in arr:
        word = entry['word']
        tags = entry['tags']
        gender = entry['gender']
        if word in model.vocab:
            f_sim = model.similarity(word, f_term)
            m_sim = model.similarity(word, m_term)
            if (f_sim < 0.1 and m_sim < 0.1):
                not_strong.add(word)
                break
            elif f_sim > 0.1 and f_sim > m_sim:
                entry['gender'] = 'female'
            elif m_sim > f_sim and m_sim > 0.1:
                entry['gender'] = 'male'
            newArr.append(entry)
        else:
            if 'urban' not in tags:
                discard.add(word)
                print(word)
            else:
                newArr.append(entry)
    all.extend(newArr)

checkDistance(all_words)
writeToJson('words/discard', list(discard))
writeToJson('words/not_strong', list(not_strong))
writeToJson('words/all', all)
