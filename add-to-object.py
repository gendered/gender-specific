import json

with open('words/filtered/female-all.json') as f:
    female_all = json.load(f)

with open('words/filtered/male-all.json') as f:
    male_all = json.load(f)

with open('data/urban/urban-female.json') as f:
    urban_female_all = json.load(f)

with open('data/urban/urban-male.json') as f:
    urban_male_all = json.load(f)

def defineObj(data, gender, tag=''):
    arr = []
    for word in data:
        if tag != '':
            arr.append({
                'word': word,
                'gender': gender,
                'tags': [tag]
            })
        else:
            arr.append({
                'word': word,
                'gender': gender
            })
    return arr


def writeToJson(path, arr):
	with open(path + '.json', 'w') as outfile:
	    json.dump(arr, outfile)

writeToJson('api-data/female-all', defineObj(female_all, 'female'))
writeToJson('api-data/male-all', defineObj(male_all, 'male'))
writeToJson('api-data/urban-female-all', defineObj(urban_female_all, 'female', 'urban'))
writeToJson('api-data/urban-male-all', defineObj(urban_male_all, 'male', 'urban'))
