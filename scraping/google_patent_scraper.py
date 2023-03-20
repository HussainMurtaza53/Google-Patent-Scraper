# Importing all Pre-requisites:
from tqdm import tqdm
from datetime import datetime
import time
import json
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import pandas as pd
import os


class Google_Patent_Scraper():

    # Constructor to save website which we will pass while calling Scraper class:
    def __init__(self, search):
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        
        options = Options()
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--headless")
#         self.options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        # self.options.binary_location = '/app/.apt/opt/google/chrome/chrome'
        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        options.add_argument("--disable-dev-shm-usage")
#         self.options.add_argument("--no-sandbox")
        
        # self.driver = webdriver.Chrome(executable_path = '/app/.chromedriver/bin/chromedriver', chrome_options = self.options)
        self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=options)
#         self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=self.options)
        self.search = "+".join(search.split())
        self.url = 'https://patents.google.com/?q=({0})&oq={0}&page={1}'

    # def get_all_links(self):
    #     all_links = []
    #     count = 0
    #     while count <= 4:
    #         url = self.url.format(self.search, count)
    #         self.driver.get(url)
    #         time.sleep(3)
    #         breakpoint()
    #         elements = self.driver.find_elements(by = 'tag name', value = 'search-result-item')
    #         page_links = [e.find_element(by = 'tag name', value = 'a').get_attribute('href') for e in elements]
    #         all_links += page_links
    #         count += 1
    #     return all_links
    
    def index_containing_substring(self, the_list, substring):
        for i, s in enumerate(the_list):
            if substring in s.lower():
                return i
        return -1
    
    def get_all_paragraphs(self, index, n_heading, soup):
        siblings = soup.find_all('heading')[index].find_next_siblings()
        all_para = []
        # iterate through the siblings until you find the next heading element
        for sibling in siblings:
            if n_heading:
                if n_heading in sibling.text.lower():  # check if the sibling is a heading element
                    break  # stop iterating if you found the next heading element
                else:
                    all_para.append(sibling)
            else:
                # do something with the current sibling element
                all_para.append(sibling)
        return all_para
    
    def get_headings_paragraph(self, title, headings, n_heading, soup):
        index = self.index_containing_substring(headings, title)
        if index != -1:
            para_ls = self.get_all_paragraphs(index, n_heading, soup)
            paragraph = "\n".join([p.text for p in para_ls])
            return paragraph
        else:
            print('Heading not present', title)
            return None
    
    def get_description(self, title, headings, soup):
        index = self.index_containing_substring(headings, title)
        previous_siblings = soup.find_all('heading')[index].find_previous_siblings()
        desc = []
        if previous_siblings:
            for prev in range(len(previous_siblings) - 1, -1, -1):
                desc.append(previous_siblings[prev])
            paragraph = "\n".join([d.text for d in desc])
        else:
            paragraph = " ".join(soup.find('patent-text', id = 'descriptionText').text.split())
        return paragraph
    
    def get_all_headings(self, soup):
        all_headings = [h.text for h in soup.find_all('heading')]
        return all_headings
    
    def get_soup(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        return soup
    
    def new_tab(self, element):
        p_element = element.find_element(by = 'tag name', value = 'state-modifier')
        ActionChains(self.driver).key_down(Keys.CONTROL).click(p_element).key_up(Keys.CONTROL).perform()
        self.driver.switch_to.window(self.driver.window_handles[1])
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        # time.sleep(2)
        try:
            self.driver.page_source
        except:
            try:
                print('Page Source not found 1')
                time.sleep(2)
                self.driver.page_source
            except:
                try:
                    print('Page Source not found 2')
                    time.sleep(2)
                    self.driver.page_source
                except:
                    try:
                        print('Page Source not found 3')
                        time.sleep(2)
                        self.driver.page_source
                    except:
                        try:
                            print('Page Source not found 4')
                            time.sleep(2)
                            self.driver.page_source
                        except:
                            print('Page Source not found 5')
                            time.sleep(3)
    
    def close_new_tab(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def get_text_by_tags(self, soup, tag):
        para_text = soup.find(tag).text
        return para_text
    
    def save_data(self, data_ls):

        scraped_data = pd.DataFrame(data_ls)
        scraped_data.to_excel('./Data/Google_Patents_Data.xlsx')

    # This is the main function that will scrape all data:
    def main(self):
        
        all_details = []

        date, c_time = str(datetime.now()).split()
        print('\nStart Time: ', c_time, '\n')

        count = 0
        while count <= 4:
            url = self.url.format(self.search, count)
            self.driver.get(url)
            print('\n--------Current URL--------\n', self.driver.current_url)
            time.sleep(3)
            elements = self.driver.find_elements(by = 'tag name', value = 'search-result-item')
            
            for e in tqdm(range(len(elements))):
                self.new_tab(elements[e])
                try:
                    soup = self.get_soup(self.driver.page_source)
                except:
                    time.sleep(2)
                    soup = self.get_soup(self.driver.page_source)
                all_headings = self.get_all_headings(soup)
                print('\n---------Page Source-----------\n', self.driver.page_source)
                print('\n---------Soup-----------\n', soup)
                try:
                    abstract = " ".join(soup.find('abstract').text.split())
                except:
                    abstract = None
                try:
                    patent_num = soup.find('h2').text
                except:
                    patent_num = None
                try:
                    title = " ".join(soup.find('h1', id = 'title').text.split())
                except:
                    title = None
                try:
                    classification = " ".join(soup.find('classification-viewer').text.split())
                except:
                    classification = None
                try:
                    claims = " ".join(soup.find('section', id = 'claims').text.split())
                except:
                    claims = None
                try:
                    images = [i['src'] for i in soup.find('image-carousel').find_all('img')]
                except:
                    images = None
                try:
                    try:
                        description = self.get_text_by_tags(soup, 'description')
                    except:
                        description = self.get_description('background', all_headings, soup)
                except:
                    description = None
                try:
                    try:
                        background = self.get_text_by_tags(soup, 'background-art')
                    except:
                        background = self.get_headings_paragraph('background', all_headings, 'summary', soup)
                except:
                    background = None
                try:
                    try:
                        summary = self.get_text_by_tags(soup, 'summary-of-invention') # To be done
                    except:
                        summary = self.get_headings_paragraph('summary', all_headings, 'drawing', soup)
                except:
                    summary = None
                try:
                    tech_field = self.get_text_by_tags(soup, 'technical-field')
                except:
                    tech_field = None
                try:
                    try:
                        drawing = self.get_text_by_tags(soup, 'description-of-drawings')
                    except:
                        drawing = self.get_headings_paragraph('drawing', all_headings, 'detail', soup)
                except:
                    drawing = None
                try:
                    try:
                        detail_desc = self.get_text_by_tags(soup, 'description-of-embodiments')
                    except:
                        try:
                            detail_desc = self.get_text_by_tags(soup, 'disclosure')
                        except:
                            detail_desc = self.get_headings_paragraph('detail', all_headings, None, soup)
                except:
                    detail_desc = None
                
                dic = {
                    "Title": title,
                    "Patent_Number": patent_num,
                    "Abstract": abstract,
                    "Classification": classification,
                    "Claims": claims,
                    "Images": images,
                    "Description": description,
                    "Background": background,
                    "Summary": summary,
                    "Technical_Field": tech_field,
                    "Description_Of_The_Drawings": drawing,
                    "Description_Of_The_Embodiments": detail_desc
                }

                self.close_new_tab()

                all_details.append(dic)
                
                print('\n----------Dic-----------\n', dic)

                self.save_data(all_details)
                
                print('\n------Done-------\n')
#                 breakpoint()
                # with open('google_patent_results.json', 'w') as outfile:
                #     json.dump(all_details, outfile)
            
            count += 1
        
        date, c_time = str(datetime.now()).split()
        print('\nEnd Time: ', c_time, '\n')

        print('\n-------------------- SCRAPING DONE --------------------\n')

        return all_details
