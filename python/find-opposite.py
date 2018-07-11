import json
from gensim.models import KeyedVectors
filename = 'GoogleNews-vectors-negative300-SLIM.bin'
model = KeyedVectors.load_word2vec_format(filename, binary=True)

pairs = []
with open('words/filtered/all.json') as f:
    all = json.load(f)

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
            pairs.append([word, result])

findGenderOpposite(all)
writeToJson('words/female-pairs', female_pairs)
findGenderOpposite(male_all, 'male', pairs_two)
