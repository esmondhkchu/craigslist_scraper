from scraper import *

browser_path = './chromedriver'

test = CraigslistExtractor(browser_path, seller_type='cto', search_term='tesla model s')

print(test.get_all_item_info(n=2))
