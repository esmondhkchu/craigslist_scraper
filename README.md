# Craigslist Scraper

Test missing, in progress...

## usuage
``` python
# initiate the search
>>> case = CraigslistExtractor(browser_path='./chromdriver', seller_type='cto', search_term='tesla model s')
# to extract the search item info, example shows get 2 from random, if n is None, then will extract all
>>> info = case.get_all_item_info(n=2, random=True, seed=1234)
```