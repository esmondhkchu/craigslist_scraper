# Craigslist Scraper

Test missing, in progress...

## usuage
``` python
# initiate the search of tesla model s
>>> case = CraigslistExtractor(browser_path='./geckodriver', \
                               location='sfbay', \
                               seller_type='cto', \
                               search_term='tesla')
# to extract the search item info, example shows get 2 from random, if n is None, then will extract all
>>> result = case.get_all_item_info(n=None, \
                                    random=False, \
                                    seed=None, \
                                    save_data=False, \
                                    file_name=None, \
                                    return_=True)
```
