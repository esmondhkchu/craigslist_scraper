from craigslist_scraper import *
import pandas as pd

browser_path = './chromedriver'

test = CraigslistExtractor(browser_path, location='sfbay', seller_type='cto', search_term='tesla model s')

df = test.get_all_item_info(n=3)
print(df)

df.to_csv('test.csv', index=False)
