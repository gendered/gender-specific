import json
import jsonpickle
from gensim.models import KeyedVectors
filename = 'GoogleNews-vectors-negative300.bin'
model = KeyedVectors.load_word2vec_format(filename, binary=True)

with open('words/female-all.json') as f:
    female_all = json.load(f)
    female_all = jsonpickle.decode(female_all)

with open('words/male-all.json') as f:
    male_all = json.load(f)
    male_all = jsonpickle.decode(male_all)

def findGenderOpposite(words, gender):
    # for word in words:
    word = 'congresswoman'
    if (gender == 'female'):
        pos = 'man'
        neg = 'woman'
    else:
        pos = 'woman'
        neg = 'man'
    result = model.most_similar(positive=[pos, word], negative=[neg], topn=1)
    print (word)
    print (result)



findGenderOpposite(female_all, 'female')
# findGenderOpposite(male_all, 'male')
