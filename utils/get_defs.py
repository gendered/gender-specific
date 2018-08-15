from dotenv import load_dotenv
from wordnik import *
from PyDictionary import PyDictionary
import requests
from wiktionaryparser import WiktionaryParser
from vocabulary.vocabulary import Vocabulary as vocabulary
import os
import json
import re

# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '../')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

# wordnik api stuff
apiUrl = 'http://api.wordnik.com/v4'
apiKey = os.getenv('API_KEY')
client = swagger.ApiClient(apiKey, apiUrl)


# tries to get word definition from a bunch of dictionary APIs
def getWordDefinition(word):
  def getDef(word):
    dictionary=PyDictionary()
    definition = dictionary.meaning(word)
    if isinstance(definition, dict) and 'Noun' in definition:
      defs = definition['Noun']
      if isinstance(defs, list) and len(defs) > 0:
        return defs

    # wordnik dictionary
    wordApi = WordApi.WordApi(client)
    try:
      definition = (wordApi.getDefinitions(word, partOfSpeech='noun', limit=1))
      if definition is not None:
        return [(definition[0].text).lower()]
    except:
      meaningsList = vocabulary.meaning(word)
      if meaningsList != False:
        defs = json.loads(meaningsList)
        if (len(defs) > 0):
          definitions = []
          for definition in defs:
            d = re.sub('<[^<]+?>', '', definition.text)
            definitions.append(d.lower())
          return definitions
    try:
      # owlbot api
      url = 'https://owlbot.info/api/v2/dictionary/' + word
      r = requests.get(url)
      result = (r.json())
      definitions = []
      for item in result:
        if (item['type'] == 'noun' and item['definition']):
          definitions.append(item['definition'].lower())
      return definitions
    except:
      # wiktionary
      parser = WiktionaryParser()
      result = parser.fetch(word)
      if (result):
        definition = result[0]['definitions'][0]
        if definition['partOfSpeech'] == 'noun':
          defs = definition['text'].lower().split('\n')
          if len(defs) > 1:
            return defs[0:2]
          return defs
    return ' '

  searches = []
  # for example, look for beauty_queen, beauty-queen, beauty queen.
  if '_' in word:
    searches.extend([word, word.replace('_', ' '), word.replace('_', '-')])
  if (len(searches) != 0):
    for wordToSearch in searches:
      definition = getDef(wordToSearch)
      if definition is not None and definition != ' ':
        return definition
  else:
    definition = getDef(word)
  return definition
