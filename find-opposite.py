import json
from gensim.models import KeyedVectors
filename = 'GoogleNews-vectors-negative300-SLIM.bin'
model = KeyedVectors.load_word2vec_format(filename, binary=True)

pairs_one = []
pairs_two = []

with open('words/female-all.json') as f:
    female_all = json.load(f)

with open('words/male-all.json') as f:
    male_all = json.load(f)

def writeToJson(path, arr):
	with open(path + '.json', 'w') as outfile:
	    json.dump(arr, outfile)

def findGenderOpposite(words, gender, arr):
    for word in words:
        if word in model.wv.vocab:
            if (gender == 'female'):
                pos = 'man'
                neg = 'woman'
            else:
                pos = 'woman'
                neg = 'man'
            result = model.most_similar(positive=[pos, word], negative=[neg], topn=1)
            print (word)
            print (result)
            arr.append([word, result])

findGenderOpposite(female_all, 'female', pairs_one)
writeToJson('words/female-pairs', female_pairs)
findGenderOpposite(male_all, 'male', pairs_two)
