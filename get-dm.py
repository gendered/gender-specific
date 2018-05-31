from datamuse import datamuse
import json

api = datamuse.Datamuse()

terms = ['woman', 'man', 'female', 'male', 'boy', 'girl', 'women', 'men', 'girls', 'boys']
dict = dict.fromkeys(terms)

for term in dict:
	words = api.words(ml=term, max=1000, md='p')
	dict[term] = words

for term in dict:
	print (len(dict[term]))
	with open('words/datamuse/' + term + '.txt', 'w') as outfile:  
	    json.dump(dict[term], outfile)