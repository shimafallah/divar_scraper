import requests
import json
import re



URL = 'https://divar.ir'  # Main URL

def BackslashEscape(x):
    x = x.replace('\\"', '"')
    x = x.replace('\\\\', '\\')
    return x

def get_all_data():
    # response = requests.get(URL).text
   
    # get url from json file 
    f = open('a.json').read()
    response = json.loads(f)

    # json_str = re.search(r"window\.__PRELOADED_STATE__\s+=\s+\"(.*)\";", response)[1]
    # json_str = BackslashEscape(json_str)
    # json_data = json.loads(json_str)
    # return json_data
    return response

def get_cities():
    json_data = get_all_data()
    list_of_cities = json_data['city']['compressedData']
    return list_of_cities

def get_categories():
    json_data = get_all_data()
    categories = json_data['search']['rootCat']
    return categories


def ChildsToArray(TheArray):
    while True:
        for Category in TheArray:
            if 'children' in Category:
                if len(Category['children']) != 0:
                    TheArray += [*Category['children']]
                del Category['children']
    
        if not any('children' in x for x in TheArray):
            break
    return TheArray


def search_in_categories(category_name, categories):
    categories = [get_categories()]
    all_subcategories = ChildsToArray(categories)
    return all_subcategories