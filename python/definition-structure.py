import json
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import re
import string

with open('words/unfiltered/discard.json') as f:
    discard_words = json.load(f)

with open('data/animals.json') as f:
    animals = json.load(f)
    animals = ("|".join(r'\b' + animal.lower() + r'\b' for animal in animals))

with open('words/unfiltered/all-unfiltered.json') as f:
    all_words = json.load(f)

def writeToJson(path, set):
  with open(path + '.json', 'w') as outfile:
      json.dump(list(set), outfile)


def filterWordByDefinition(definition, endIndex):
    def hasWordsToExclude():
        arr = r'\bhormone\b|\bsperm\b|\banimal\b|\borgan\b|\bmale or female\b|\bman or woman\b'
        rgex = re.compile(arr)
        termInDef = rgex.search(definition)
        if termInDef is not None:
            return True
        return False

    # remove entries with animals in definition
    def isThereAnimal():
        animalRegex = re.compile(animals)
        animalInDef = animalRegex.search(definition)
        if animalInDef is not None:
            return True
        return False

    def preprocess(sentence):
        sentence = sentence.lower()
        translator = str.maketrans('', '', string.punctuation)
        return sentence.translate(translator)

    def filterTags(tags):
        new_tags = []
        for item in tags:
            word = item[0]
            if word != 'a' and word != 'an' and word != 'the':
                new_tags.append(item)
        return new_tags

    def anyExceptions(definition, tags):
        exceptions = 'name of|applied to|given to|term for'
        rgex = re.compile(exceptions)
        termInDef = rgex.search(definition)
        if termInDef is not None:
            return True
        return False

    def sentenceIsRightStructure():
        # trim
        trimmedDefinition = definition[0:endIndex]
        # remove a and an
        cleanDefinition = preprocess(trimmedDefinition)
        # part of speech tagger
        text = word_tokenize(cleanDefinition)
        tags = filterTags(nltk.pos_tag(text))

        # gendered term is the last in the string so it'll be the last in the array
        length = len(tags)
        # so the term before will be at this location
        # check if it's a preposition or verb before gendered term
        if length <= 1:
            return True
        else:
            if not anyExceptions(definition, tags):
                posOne = tags[length-2][1]
                termOne = tags[length-2][0]
                if posOne == 'IN':
                    return False
                if termOne == 'being':
                    return False
                if length >= 3:
                    posTwo = tags[length-3][1]
                    if posTwo == 'IN':
                        return False
                return True
            else:
                return True


    if isThereAnimal() or hasWordsToExclude() or not sentenceIsRightStructure():
        return False
    return True

terms = r'\b[\w-]*woman\b|\bfemale\b|\b[\w-]girl\b|\bgirls\b|\b[\w-]*women\b|\blady\b|\b[\w-]*mother\b|\b[\w-]*daughter\b|\bwife\b|\bman\b|\bmale\b|\bboy\b|\bmen\b|\bboys\b|\bson\b|\b[\w-]*father\b|\bhusband\b'
pattern = re.compile(terms)

discard_two = []
for entry in discard_words:
    word = entry['word']
    definition = entry['definition']
    termsInString = pattern.search(definition)
    if termsInString is not None:
        startIndex = termsInString.start(0)
        endIndex = termsInString.end(0)
        if filterWordByDefinition(definition, endIndex):
            all_words.append(entry)
        else:
            discard_two.append(entry)

writeToJson('words/unfiltered/all-unfiltered', all_words)
writeToJson('words/unfiltered/discard', discard_two)
