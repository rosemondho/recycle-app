from urllib.request import urlopen
import os
import simplejson


API_KEY = os.environ['EARTH911_KEY']
 
base_url = 'http://api.earth911.com/'
 
def query(url):
    text = urlopen(url).read()
    result = simplejson.loads(text)
    if 'error' in result:
        raise Exception(result['error'])
    else:
        return result['result']
 
def get_materials():
    return query(base_url + 'earth911.getMaterials?api_key=' + API_KEY)
 
for material in get_materials():
    print (f"{material['description']} ({material['material_id']})")