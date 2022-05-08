import requests
import json
import re



URL = 'https://divar.ir'  # Main URL

class DivarScraper:
    def __init__(self) -> None:
        self.all_data = self.get_all_data()

    def BackslashEscape(self,x):
        x = x.replace('\\"', '"')
        x = x.replace('\\\\', '\\')
        return x

    def get_all_data(self):
        response = requests.get(URL+"/s/tehran").text
        # get url from json file 
        # f = open('a.json').read()
        # response = json.loads(f)
        json_str = re.search(r"window\.__PRELOADED_STATE__\s+=\s+\"(.*)\";", response)[1]
        json_str = self.BackslashEscape(json_str)
        json_data = json.loads(json_str)
        return json_data

    def get_cities(self):
        json_data = self.all_data
        list_of_cities = json_data['city']['compressedData']
        return list_of_cities

    def get_categories(self):
        json_data = self.all_data
        categories = json_data['search']['rootCat']
        return categories

    def slug_to_url(self, slug):
        json_data = self.all_data
        slug_list = json_data['search']['schema']['ui_schema']['category']['urischema']['display']
        return slug_list[slug][0]
    

    def child_to_array(self, array):
        while True:
            for category in array:
                if 'children' in category:
                    if len(category['children']) != 0:
                        array += [*category['children']]
                    del category['children']
        
            if not any('children' in x for x in array):
                break
        return array


    def search_in_categories(self, category_name):
        specific_categories = self.child_to_array([self.get_categories()])
        found_category = list(filter(lambda cat: cat['name'] == category_name, specific_categories))
        if len(found_category) != 0:
            found_category[0]['url_slug'] = self.slug_to_url(found_category[0]['slug'])
        return found_category