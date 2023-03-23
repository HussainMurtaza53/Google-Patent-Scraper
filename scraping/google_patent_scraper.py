# Importing all Pre-requisites:
from tqdm import tqdm
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import requests
import wordninja
from google_patent_scraper.settings import BASE_URL
from scraping.models import *


class Google_Patent_Scraper():

    # Constructor to save website which we will pass while calling Scraper class:
    def __init__(self, search):
        self.search = "+".join(search.split())
        self.main_url = 'https://www.google.com/search?q={0}&tbm=pts&sxsrf=AJOqlzUNTt673TM7N19-yya2UM4oila_bg:1679480269775&ei=zdUaZKbsLrWAi-gP-9Sj2A8&start={1}&sa=N&ved=2ahUKEwjmhozHp-_9AhU1wAIHHXvqCPsQ8NMDegQIDhAW&biw=1408&bih=975&dpr=1'
    
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
    
    def get_soup(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    def get_text_by_tags(self, soup, tag):
        para_text = soup.find(tag).text
        return para_text
    
    def get_all_ref_num(self, soup):
        patents_ls = soup.text.split('/patents/')
        ref_num = []
        for i in range(1, len(patents_ls)):
            mix_ref_num = patents_ls[i].split()[0]
            if '?' in mix_ref_num:
                ref_num.append(mix_ref_num.split('?')[0])
            else:
                word_ninja_ls = wordninja.split(mix_ref_num)
                if len(word_ninja_ls) > 2:
                    ref_num.append("".join(word_ninja_ls[:-1]))
                else:
                    ref_num.append("".join(word_ninja_ls))
        return ref_num
    
    def get_classification(self, soup):
        section = soup.find_all('section')
        classification = None
        for s in section:
            s_text = s.find_next().text
            if 'Classifications' in s_text:
                classification = s.text
        return classification
    
    def save_data(self, data_ls):

        scraped_data = pd.DataFrame(data_ls)
        scraped_data.to_excel('./Data/Google_Patents_Data.xlsx')

    # This is the main function that will scrape all data:
    def main(self):
        
        all_details = []

        date, c_time = str(datetime.now()).split()
        print('\nStart Time: ', c_time, '\n')

        # Delete old records before adding new one:
        Google_Patent.objects.all().delete()

        count = 0
        while len(all_details) <= 50:
            url = self.main_url.format(self.search, count)
            soup = self.get_soup(url)
            all_ref_num = self.get_all_ref_num(soup)
            
            for num in tqdm(range(len(all_ref_num))):
                patent_url = 'https://patents.google.com/patent/{0}?oq={1}'.format(all_ref_num[num], self.search)
                soup = self.get_soup(patent_url)
                all_headings = self.get_all_headings(soup)
                title_text = soup.title.text
                if 'Error' not in title_text:
                    header = title_text.split(' - ')
                    try:
                        abstract = " ".join(soup.find('abstract').text.split())
                    except:
                        abstract = None
                    try:
                        # patent_num = soup.find('h2').text
                        patent_num = header[0]
                    except:
                        patent_num = None
                    try:
                        # title = " ".join(soup.find('h1', id = 'title').text.split())
                        title = " ".join(header[1].split())
                    except:
                        title = None
                    try:
                        try:
                            classification = " ".join(soup.find('classification-viewer').text.split())
                        except:
                            classification = self.get_classification(soup)
                    except:
                        classification = None
                    try:
                        # claims = " ".join(soup.find('section', id = 'claims').text.split())
                        claims = soup.find('section', itemprop = 'claims').text
                    except:
                        claims = None
                    try:
                        # images = [i['src'] for i in soup.find('image-carousel').find_all('img')]
                        images = [i.find('img')['src'] for i in soup.find_all('li', itemprop = 'images')]
                    except:
                        images = None
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
                    try:
                        try:
                            description = self.get_text_by_tags(soup, 'description')
                        except:
                            description = self.get_description('background', all_headings, soup)
                    except:
                        description = "{0}\n{1}\n{2}\n{3}\n{4}".format(background, summary, tech_field, drawing, detail_desc).replace('None', '')
                    
                    dic = {
                        "title": title,
                        "patent_num": patent_num,
                        "abstract": abstract,
                        "classification": classification,
                        "claims": claims,
                        "images": images,
                        "description": description,
                        "background": background,
                        "summary": summary,
                        "tech_field": tech_field,
                        "drawing": drawing,
                        "detail_desc": detail_desc
                    }

                    all_details.append(dic)
                    
                    # print('\n----------Dic-----------\n', dic)

                    # self.save_data(all_details)

                    # with open('google_patent_results.json', 'w') as outfile:
                    #     json.dump(all_details, outfile)
            
            count += 10
        
        Google_Patent.objects.bulk_create([Google_Patent(**item) for item in all_details])
        
        date, c_time = str(datetime.now()).split()
        print('\nEnd Time: ', c_time, '\n')

        print('\n-------------------- SCRAPING DONE --------------------\n')

        return all_details
