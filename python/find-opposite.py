import json
from gensim.models import KeyedVectors
filename = 'GoogleNews-vectors-negative300.bin'
model = KeyedVectors.load_word2vec_format(filename, binary=True)

with open('words/all.json') as f:
    all = json.load(f)

all_words_only = [entry.word for entry in all]

def writeToJson(path, arr):
	with open(path + '.json', 'w') as outfile:
	    json.dump(arr, outfile)

def findGenderOpposite(words):
    for entry in words:
        word = entry['word']
        gender = entry['gender']
        if word in model.vocab:
            if (gender == 'female'):
                pos = 'man'
                neg = 'woman'
            else:
                pos = 'woman'
                neg = 'man'
            result = model.most_similar(positive=[pos, word], negative=[neg], topn=1)
            if result is not None:
                result = result[0]
                opp_word = result[0]
                score = result[1]
                if opp_word in all_words_only and score > 0.5:
                    entry['opposite'] = opp_word



findGenderOpposite(all)
writeToJson('words/all-pairs.json', pairs)
