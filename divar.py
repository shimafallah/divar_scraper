import requests
import json
import re



URL = 'https://divar.ir'  # Main URL

def BackslashEscape(x):
    x = x.replace('\\"', '"')
    x = x.replace('\\\\', '\\')
    return x

def get_all_data():
    response = requests.get(URL).text
    json_str = re.search(r"window\.__PRELOADED_STATE__\s+=\s+\"(.*)\";", response)[1]
    json_str = BackslashEscape(json_str)
    json_data = json.loads(json_str)
    return json_data

def get_cities():
    json_data = get_all_data()
    list_of_cities = json_data['city']['compressedData']
    return list_of_cities

def get_categories():
    json_data = get_all_data()
    categories = json_data['search']['rootCat']
    return categories

def search_in_categories(category_name, categories):
    x = []