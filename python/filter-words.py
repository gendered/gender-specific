import json
from gensim.models import KeyedVectors, word2vec
filename = 'models/GoogleNews-vectors-negative300.bin'
model = KeyedVectors.load_word2vec_format(filename, binary=True)

with open('words/unfiltered/all-unfiltered.json') as f:
    all_words = json.load(f)

def writeToJson(path, arr):
	with open(path + '.json', 'w') as outfile:
	    json.dump(arr, outfile)

not_strong = []
all = []

def filterWords(arr):

    def getMaxSim(terms, word):
        max = 0
        for term in terms:
            sim = model.similarity(word, term)
            if sim > max:
                max = sim
        return max

    def checkDistance(word):
        f_sim = getMaxSim(['woman', 'women', 'female'], word)
        m_sim = getMaxSim(['man','men', 'male'], word)
        return {
            'f_sim': f_sim,
            'm_sim': m_sim
        }

    for entry in arr:
        definition = entry['definition']
        if ('tags' in entry):
            tags = entry['tags']
            word = entry['word'].lower()
            if word in model.vocab:
                sims = checkDistance(word)
                f_sim = sims['f_sim']
                m_sim = sims['m_sim']
                if (f_sim < 0.1 and m_sim < 0.1):
                    not_strong.append(entry)
                    continue
                elif f_sim > 0.1 and f_sim > m_sim:
                    entry['gender'] = 'female'
                    all.append(entry)
                elif m_sim > f_sim and m_sim > 0.1:
                    entry['gender'] = 'male'
                    all.append(entry)
            else:
                all.append(entry)

filterWords(all_words)
writeToJson('words/not_strong', not_strong)
writeToJson('words/all', all)