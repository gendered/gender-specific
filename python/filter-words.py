import json
from gensim.models import KeyedVectors
filename = 'GoogleNews-vectors-negative300-SLIM.bin'
model = KeyedVectors.load_word2vec_format(filename, binary=True)

with open('words/female-all-unfiltered.json') as f:
    female_all = json.load(f)

with open('words/male-all-unfiltered.json') as f:
    male_all = json.load(f)

with open('words/unknown.json') as f:
    unknown = json.load(f)

def writeToJson(path, arr):
	with open(path + '.json', 'w') as outfile:
	    json.dump(arr, outfile)

discard = set([])
not_strong = set([])
female_set = set([])
male_set = set([])

def checkDistance(arr):
    f_term = 'woman'
    m_term = 'man'
    for word in arr:
        if word in model.vocab:
            f_sim = model.similarity(word, f_term)
            m_sim = model.similarity(word, m_term)
            if (f_sim < 0.1 and m_sim < 0.1):
                not_strong.add(word)
            elif f_sim > 0.1 and f_sim > m_sim:
                female_set.add(word)
            elif m_sim > f_sim and m_sim > 0.1:
                male_set.add(word)
        else:
                discard.add(word)

# before we look for pairs, filter out some words that are not gendered
all = female_all + male_all
print(len(all))
# filter out words that are not close enough to gender terms
checkDistance(all)
checkDistance(unknown)

writeToJson('words/discard', list(discard))
writeToJson('words/not_strong', list(not_strong))
writeToJson('words/female-all', list(female_set))
writeToJson('words/male-all', list(male_set))
