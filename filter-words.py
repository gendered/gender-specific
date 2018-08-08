import json
import re

with open('words/unfiltered/all-unfiltered.json') as f:
    all_words = json.load(f)

def writeToJson(path, arr):
	with open(path + '.json', 'w') as outfile:
	    json.dump(arr, outfile)

not_strong = []
all = []
discard = []

def hasWordsToExclude(word, definition):
    f = open('utils/pattern.txt','r')
    terms = f.read().replace('\n', '')
    rgex = re.compile(terms)
    termInDef = rgex.search(definition)
    if termInDef is not None:
        start = termInDef.start(0)
        end = termInDef.end(0)
        print('found', word, definition[start:end])
    #     return True
    # return False

def isGendered(definition):
    terms = r"""\b[\w-]*woman\b[^'-]|\bfemale\b|\b[\w-]girl\b|\bgirls\b
    |\b[\w-]*women\b[^'-]|\blady\b[^'-]|\b[\w-]*mother\b[^'-]|\b[\w-]*daughter\b|\bwife\b|
    \bman\b[^'-]|\bmale\b|\bboy\b|\bmen\b[^'-]|\bboys\b|\bson\b|\b[\w-]*father\b|\bhusband\b"""
    pattern = re.compile(terms)
    termsInDef =  pattern.search(definition.lower())
    if termsInDef is not None:
        return True
    else:
        return False

for entry in all_words:
    word = entry['word']
    definition = entry['definition']
    if not hasWordsToExclude(word, definition):
        all.append(entry)
    else:
        discard.append(entry)

writeToJson('words/filtered/discard-2', discard)
writeToJson('words/filtered/all-2', all)
