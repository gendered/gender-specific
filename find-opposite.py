import json
from gensim.models import KeyedVectors
filename = 'GoogleNews-vectors-negative300-SLIM.bin'
model = KeyedVectors.load_word2vec_format(filename, binary=True)

with open('words/female-all.json') as f:
    female_all = json.load(f)

with open('words/male-all.json') as f:
    male_all = json.load(f)

with open('words/unknown.json') as f:
    unknown = json.load(f)

pairs_one = []
pairs_two = []

def writeToJson(path, arr):
	with open(path + '.json', 'w') as outfile:
	    json.dump(arr, outfile)

# def findGenderOpposite(words, gender, arr):
#     for word in words:
#         if word in model.wv.vocab:
#             if (gender == 'female'):
#                 pos = 'man'
#                 neg = 'woman'
#             else:
#                 pos = 'woman'
#                 neg = 'man'
#             result = model.most_similar(positive=[pos, word], negative=[neg], topn=1)
#             print (word)
#             print (result)
#             arr.append([word, result])

discard = set([])
# filter out words that are not close enough to gender terms
def checkDistance(arr, terms):
    new_set = set([])
    for word in arr:
        for term in terms:
            if word in model.vocab:
                sim = model.similarity(word, term)
                if (sim > 0.1):
                    new_set.add(word)
                    break
            else:
                print(word)
    return new_set

# before we look for pairs, filter out some words that are not gendered
female_all = checkDistance(female_all, ['female', 'woman'])
male_all = checkDistance(male_all, ['male', 'man'])
male_all.update(checkDistance(unknown, ['male', 'man']))
female_all.update(checkDistance(unknown, ['female', 'woman']))

writeToJson('words/female-all', list(female_all))
writeToJson('words/male-all', list(male_all))
# findGenderOpposite(female_all, 'female', pairs_one)
# writeToJson('words/female-pairs', female_pairs)
# # findGenderOpposite(male_all, 'male', pairs_two)
