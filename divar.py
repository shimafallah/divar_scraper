from bs4 import BeautifulSoup as bs
import urllib.parse
import requests
import json
import re



URL = 'https://divar.ir'  # Main URL

# Unit By Milion Toomans
PRICE_RANGES = [
    [700, 1100],
    [1100, 2000],
    [2000, 'infinity']
]

def range_check(price,price_ranges):
    price = int(price)
    price /= 1000000
    price = int(price)
    for price_range in price_ranges:
        start_price = price_range[0]
        end_price = price_range[1]
        if end_price == 'infinity':
            end_price = 999**999
        if price >= start_price and price < end_price:
            return price_range
    return False


class DivarScraper:
    def __init__(self, city, category, custom_search = ""):
        """initialize divar scraper

        Args:
            city (str): name of city (persian)
            category (str): name of category (persian)
            custom_search (str, optional): searches in divar. Defaults to empty.
        """
        self.all_data = self.get_all_data()
        self.cities = self.get_cities()
        self.select_city(city)
        self.select_category(category)
        self.custom_search = custom_search

    def backslash_escape(self,escape_str):
        escape_str = escape_str.replace('\\"', '"')
        escape_str = escape_str.replace('\\\\', '\\')
        return escape_str

    def get_all_data(self):
        response = requests.get(URL+"/s/tehran").text
        json_str = re.search(r"window\.__PRELOADED_STATE__\s+=\s+\"(.*)\";", response)[1]
        json_str = self.backslash_escape(json_str)
        json_data = json.loads(json_str)
        return json_data

    def get_cities(self):
        json_data = self.all_data
        list_of_cities = json_data['city']['compressedData']
        return list_of_cities

    def select_city(self,city_name):
        selected_city = ""
        list_of_cities = self.cities
        for city in list_of_cities:
            if city[1] == city_name:
                selected_city = city[2]
                break
        if selected_city != "":
            self.city = selected_city
        else:
            print('City doesnt exist!')

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

    def select_category(self, category_name):
        specific_categories = self.child_to_array([self.get_categories()])
        found_category = list(filter(lambda cat: cat['name'] == category_name, specific_categories))
        if len(found_category) != 0:
            found_category[0]['url_slug'] = self.slug_to_url(found_category[0]['slug'])
            self.category = found_category[0]['url_slug']
        else:
            print('Category doesnt exist!')
    
    def get_products(self):
        divar_list = []
        all_pages = range(1, 2)
        for s_page in all_pages:
            if self.custom_search != "":
                custom_search = '&q='+ urllib.parse.quote(self.custom_search)
            else:
                custom_search = ""
            url = f"{URL}/s/{self.city}/{self.category}/?page={s_page}{custom_search}"
            print(f'Openning {self.city} Page #{s_page}')
            r = requests.get(url)
            soup = bs(r.text, "html.parser")
            products = soup.select(".post-card-item a")
            for product in products:
                divar_id = re.search(r"([^\/]+$)", product['href'])[0]
                if product.select(".kt-post-card__description")[0].text != 'توافقی':
                    divar_list.append(divar_id)
        return divar_list

    def get_product_detail(self,divar_id):
        url = f"{URL}/v/{divar_id}"
        r = requests.get(url)

        # data
        json_str = re.search(r"window\.__PRELOADED_STATE__\s+=\s+\"(.*)\";", r.text)[1]
        json_str = self.backslash_escape(json_str)
        json_data = json.loads(json_str)
        
        # Title
        title = json_data['currentPost']['post']['data']['share']['title']

        # Price
        price = json_data['currentPost']['post']['data']['webengage']['price']

        # Description
        description = json_data['currentPost']['post']['data']['description']

        collected_data = {'Id': divar_id, 'Title': title, 'Price': price, 'Description': description}
        return collected_data
       
        

# d_scrape = DivarScraper(city='تهران', category='خانه و ویلا', custom_search="دوبلکس")
d_scrape = DivarScraper(city='تهران', category='خانه و ویلا')

divar_list = d_scrape.get_products()
divar_products = []
for divar_id in divar_list:
    divar_detail = d_scrape.get_product_detail(divar_id)
    divar_products.append(divar_detail)

result = {}
divar_products = sorted(divar_products, key=lambda m: m['Price'])
for divar_item in divar_products:
    price = divar_item['Price']
    price_range = range_check(price,PRICE_RANGES)
    if not price_range:
        continue
    range_key = f"{price_range[0]}-{price_range[1]}"
    if range_key not in result:
        result[range_key] = []
    result[range_key].append(divar_item)

result = json.dumps(result)
print(result)