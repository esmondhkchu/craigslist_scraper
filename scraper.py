from selenium import webdriver
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd
from tqdm import tqdm

def unlist(in_list):
    return [j for i in in_list for j in i]

class CraigslistExtractor:
    def __init__(self, browser_path, seller_type, search_term):
        self.browser_path = browser_path
        self.seller_type = seller_type
        self.search_term = search_term

        self.all_item_url = self.get_all_item_url(self.browser_path, self.seller_type, self.search_term)
        self.total_extracted_item = len(self.all_item_url)

    def get_all_item_info(self, n=None, random=False, seed=None):
        """ extract all or n search result info

        arg: n (int) - extract how many result
             random (boolean) - if result should be drawn random or not, optional, default is False
             seed (int) - seed number, only when random is True

        return: (dataframe) - a dataframe with all the info
        """
        if n is None:
            all_info = [self.extract_page_info(i) for i in tqdm(self.all_item_url)]
        elif (n is not None) and (random is True):
            if seed is None:
                seed = 123
            else:
                seed = seed
            np.random.seed(seed)
            random_idx = np.random.choice(range(self.total_extracted_item), size=n)
            all_info = [self.extract_page_info(i) for i in tqdm(np.array(self.all_item_url)[random_idx])]
        elif (n is not None) and (random is False):
            all_info = [self.extract_page_info(i) for i in tqdm(self.all_item_url[:n])]

        return self.list_to_df(all_info)

    @staticmethod
    def get_page_source(browser_path, url):
        """ get the input page source code

        arg: browser_path (str) - the path where browser is located
            url (str) - the target page url

        return: soup (bs4 object) - bs4 object contains page source
        """
        browser = webdriver.Chrome(executable_path=browser_path)
        browser.get(url)
        soup = BeautifulSoup(browser.page_source, 'html5lib')
        browser.close()

        return soup

    # get total page number
    @staticmethod
    def get_total_item(soup):
        """ input the first page of the search result, return the total items from this search
            use to get total page number

        arg: soup (bs4 object) - first page page source

        return: (int) - total page number
        """
        total_count = soup.find_all('span', class_='totalcount')[0].text
        return int(total_count)

    # get all content url
    @staticmethod
    def get_page_item_url(soup):
        """ get all item's url in a single page

        arg: soup (bs4 object) - the input page source

        return: all_item_url (list) - a list of all item links from the page source
        """
        all_item = soup.find_all('ul', class_='rows')[0].find_all('li', class_='result-row')
        all_item_url = [i.find_all('a', href=True)[0]['href'] for i in all_item]

        return all_item_url

    @staticmethod
    def composite_url(seller_type, search_term, page_num):
        search_path = '%20'.join(search_term.split())
        base_path = "https://sfbay.craigslist.org/search/{}?s={}&query={}"
        url = base_path.format(seller_type, page_num, search_path)
        return url

    def get_all_item_url(self, browser_path, seller_type, search_term):
        """ get all item url from a search term

        arg: browser_path (str) - the path where browser is located
            seller_type (str) - seller type
                                all -> 'cta'
                                owner -> 'cto'
                                dealer -> 'ctd'
            search_term (str) - search key words

        return: all_item_url (list) - all item's link from the search
        """
        first_page_url = self.composite_url(seller_type, search_term, 0)
        first_page_soup = self.get_page_source(browser_path, first_page_url)

        total_item = self.get_total_item(first_page_soup)
        page_source_num = [i+1 for i in range(0, total_item, 120) if i != 0]

        # first page url
        first_page_url = self.get_page_item_url(first_page_soup)

        if len(page_source_num) > 0:
            # all page link
            all_but_one_link = [self.composite_url(seller_type, search_term, i) for i in page_source_num]
            # all item url but page one
            all_item_url_but_one = [self.get_page_item_url(self.get_page_source(browser_path, i)) for i in all_but_one_link]
            all_item_url = first_page_url + [j for i in all_item_url_but_one for j in i]
        else:
            all_item_url = first_page_url

        return all_item_url

    @staticmethod
    def list_to_df(in_list):
        """ transform a list of dicionary to dataframe

        arg: in_list (list) - a list of dictionary

        return: (dataframe) - a dataframe from the input list
        """
        all_col = list(set(unlist([list(i) for i in in_list])))
        info_by_col = [[j.get(i) for i in all_col] for j in in_list]

        return pd.DataFrame(info_by_col, columns=all_col)

    def extract_page_info(self, url):
        """ extract all info within an input url

        arg: url (str) - the page link

        return: all_info (dict) - a dictionary of all info
        """
        try:
            soup = self.get_page_source(self.browser_path, url)

            # title
            title_soup = soup.find_all('span', class_='postingtitletext')[0]

            title = title_soup.find_all('span', id='titletextonly')[0].text
            price = title_soup.find_all('span', class_='price')[0].text
            location = title_soup.find_all('small')[0].text.replace(' (','').replace(')','')
            title_box = {'title':title, 'price':price, 'location':location}

            # infobox
            infobox_soup = soup.find_all('div', class_='mapAndAttrs')[0].find_all('p', class_='attrgroup')[1]

            info_box_text = [i.text for i in infobox_soup.find_all('span')]
            splited_info_box_text = [i.split(':') for i in info_box_text]
            info_box = {i[0] if len(i) == 2 else 'info': i[1][1:] if len(i) == 2 else i[0] for i in splited_info_box_text}

            # content
            content_soup = soup.find('section', id='postingbody')

            content_text = content_soup.text.replace('QR Code Link to This Post','')
            content = {'content':content_text}

            keys = ['url'] + list(title_box) + list(info_box) + list(content)
            values = [url] + list(title_box.values()) + list(info_box.values()) + list(content.values())
            all_info = {i:j for i,j in zip(keys, values)}

            return all_info

        except:
            return url
