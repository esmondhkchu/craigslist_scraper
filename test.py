from scraper import *

browser_path = './chromedriver'

tesla = CraigslistExtractor(browser_path, 'cto', 'tesla model s')

tesla_result = tesla.get_all_item_info(n=2, random=True, seed=234)

tesla_result