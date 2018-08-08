from dotenv import load_dotenv
from wordnik import *
from PyDictionary import PyDictionary
import requests
from wiktionaryparser import WiktionaryParser
from vocabulary.vocabulary import Vocabulary as vb
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
        return defs[0]

    # wordnik dictionary
    wordApi = WordApi.WordApi(client)
    definition = (wordApi.getDefinitions(word, partOfSpeech='noun', limit=1))

    if definition is not None:
      return definition[0].text

    meaningsList = vb.meaning(word)
    if meaningsList != False:
      defs = json.loads(meaningsList)
      if (len(defs) > 0):
        definition = defs[0]['text']
        # some of the definitions have html tags
        return re.sub('<[^<]+?>', '', definition)

    try:
      # wiktionary
      parser = WiktionaryParser()
      result = parser.fetch(word)
      if (result):
        definitions = result[0].definitions[0]
        if definition.partOfSpeech == 'noun':
          return definition.text
    except:
      try:
        # owlbot api
        url = 'https://owlbot.info/api/v2/dictionary/' + word
        r = requests.get(url)
        result = (r.json())[0]
        if (result.type == 'noun' and result.definition):
          return result.definition
      except KeyboardInterrupt:
        raise
      except:
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
