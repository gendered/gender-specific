import pandas as pd
import json

# get gendered words from urban PyDictionary
# gendered words = words with any of the below terms in their definition
femaleTerms = [' woman ', ' female ', ' girl ', ' girls ', ' women ', ' lady ']
maleTerms = [ ' man ', ' male ', ' boy ', ' men ', ' boys ']
urban_female = []
urban_male = []
unique_words = set([])

def writeToJson(path, list):
	with open(path + '.json', 'w') as outfile:
	    json.dump(list, outfile)

def getUrbanDictionary():
	# only these columns are needed
    fields = ['word', 'definition', 'thumbs_up']
    # open csv files
    ub_1 = pd.read_csv("data/urban/urban-dic-1.csv", encoding="ISO-8859-1", skipinitialspace=True, usecols=fields)
    ub_2 = pd.read_csv("data/urban/urban-dic-2.csv", encoding="ISO-8859-1", skipinitialspace=True, usecols=fields)
    ub_3 = pd.read_csv("data/urban/urban-dic-3.csv", encoding="ISO-8859-1", skipinitialspace=True, usecols=fields)
    ub_4 = pd.read_csv("data/urban/urban-dic-4.csv", encoding="ISO-8859-1", skipinitialspace=True, usecols=fields)

    frames = [ub_1, ub_2, ub_3, ub_4]
    # add the two csvs together and remove nan values
    ub = (pd.concat(frames)).dropna()

    # only include entries with more than 1000 upvotes
    ub = ub[ub['thumbs_up'] >= 1000]

    # TODO: other ways to filter data?
    # remove duplicates
    ub = ub[~ub[['word']].apply(lambda x: x.str.lower().str.replace(" ","")).duplicated()]

    f_terms = '|'.join([str(x) for x in femaleTerms])
    m_terms = '|'.join([str(x) for x in maleTerms])

    femaleArr = ub[(ub['definition']).str.contains(f_terms, na=False)]
    maleArr = ub[ub['definition'].str.contains(m_terms, na=False)]
    urban_female.extend(femaleArr['word'].tolist())
    urban_male.extend(maleArr['word'].tolist())

    print ('urban dic done')

writeToJson('data/urban/urban-female', urban_female)
writeToJson('data/urban/urban-male', urban_male)
