# Importing all Pre-requisites:
from tqdm import tqdm
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import requests
# import wordninja
from google_patent_scraper_project.settings import BASE_URL
# from scraping.google_patent_scraper import scraper_class
from scraping.scrape_patent_links import ProjectPQ_Scraper
from scraping.models import *


class Google_Patent_Scraper():

    # Constructor to save website which we will pass while calling Scraper class:
    def __init__(self, search):
        # self.scraper = scraper_class()
        # self.search = "+".join(search.split())
        self.search = search
        self.pro_pq_obj = ProjectPQ_Scraper()
        # self.main_url = 'https://www.google.com/search?q={0}&tbm=pts&sxsrf=AJOqlzUNTt673TM7N19-yya2UM4oila_bg:1679480269775&ei=zdUaZKbsLrWAi-gP-9Sj2A8&start={1}&sa=N&ved=2ahUKEwjmhozHp-_9AhU1wAIHHXvqCPsQ8NMDegQIDhAW&biw=1408&bih=975&dpr=1'
    
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
            return 'None'
    
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
        headers = {'cookie': '__Secure-ENID=10.SE=hlDtQzEMJzWymOz3ezum_ZQS1Yjl7G40w1jeBYl-4B_feoDc36PoiHF_wl60fvW1ZcHqD5KOC3CCaX40XwUAq15FTfHvIbWtp1Zheae06V45XynIXKU3iGIt2OrcpBxpF6n-MSVHeuaefcrBgg-RaLEysAAvohKrUfIpONdDjBXVflsoOliTwQ6kMD6cS7sOsHAvzetwxl43de9o2scmn2a-Q_34NAqfwNlK0IgSI_Gn7GU0KqwWp5fD8mVgZs0sOgWnjyIvKoo; OTZ=6926995_36_36__36_; SID=UghsxYl0TwcnMtpEZZOsLho-joQFZWpzndDBPlj6orFuRJ62zKc0Wsq6O3ulJV1VdeZkTA.; __Secure-1PSID=UghsxYl0TwcnMtpEZZOsLho-joQFZWpzndDBPlj6orFuRJ62R0HKqhk0OxiMeVmcApCLvw.; __Secure-3PSID=UghsxYl0TwcnMtpEZZOsLho-joQFZWpzndDBPlj6orFuRJ62vuvyfK0O0k1QNRaFnPbraQ.; HSID=AIhtHsvsq0O8C9k_V; SSID=AVuPk60YQJCXG6zOV; APISID=T08G_TffT9UFBZpz/AN1S9wjtKgFeV20oU; SAPISID=-kOcgwr_Yp6faRrL/AZpqxTB3w6eMPKAnC; __Secure-1PAPISID=-kOcgwr_Yp6faRrL/AZpqxTB3w6eMPKAnC; __Secure-3PAPISID=-kOcgwr_Yp6faRrL/AZpqxTB3w6eMPKAnC; OGPC=19034156-1:; SEARCH_SAMESITE=CgQI9ZcB; AEC=AUEFqZc1Lw-MEXMzWhlo_Shj-uPl8yRR7OzQ7vLXjApLoEop6nz1c1JS09s; 1P_JAR=2023-03-30-10; DV=o5bJJsq5QGRXcC38Z5-bAliQTfUgc9iJV5getGLfKQEAAAAifm2YC1-e_QAAAAgH7s-UDNE6QAAAAIERQZTJUS0dEgAAAA; NID=511=JfJu5KYeObun-fVOq7n8Em7eBxXC-g6iRJTTOi_G06caudUtQrs1j7FRtdsEfLQbUieMz9dnFnGzyvaazJ4kN_1fk5sfNq_d_qkrf3l3kzhtfEd3Cbkkx4rXeosN_OvgFAq7fAnNV3kGnWn6p4T_p5ZeDCeOZugEnSkEXn6pUm45UoTZ_17r-4MpvJIhTS3IYY4z3cAIxLpL15-ed4VQjdxQv7MT1oDD99xMpWHHZ-Ko4nK-xu7Z3__HAUR36h2hjoCrdbyC5WIrpgQZk4tKo68xoNA7E4NcT-TnKXE6i8NEsGXos2nxbA; SIDCC=AFvIBn9lBi9yKbvAuE-K29u6CLwyj4xdIZHOOoEcGW-9Vv4hPdr6LSJfVwSHtWki2Gyr1dTJoivl; __Secure-1PSIDCC=AFvIBn_bnqYlbqQqCQrNXR4VmKFr0-HPwtTTSwNzblpor4gB5CVZGUjEJemQguE5gmU7mg8fs1lM; __Secure-3PSIDCC=AFvIBn-inOovvoNn3dBZeoGHLe5HV4-r_yBgislJkBmvka-rk8lMMt2VlzPturAx2meEnO4BbRU7'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    def get_text_by_tags(self, soup, tag):
        para_text = soup.find(tag).text
        return para_text
    
    # def get_all_ref_num(self, soup):
    #     patents_ls = soup.text.split('/patents/')
    #     ref_num = []
    #     for i in range(1, len(patents_ls)):
    #         mix_ref_num = patents_ls[i].split()[0]
    #         if '?' in mix_ref_num:
    #             ref_num.append(mix_ref_num.split('?')[0])
    #         else:
    #             word_ninja_ls = wordninja.split(mix_ref_num)
    #             if len(word_ninja_ls) > 2:
    #                 ref_num.append("".join(word_ninja_ls[:-1]))
    #             else:
    #                 ref_num.append("".join(word_ninja_ls))
    #     return ref_num
    
    def get_classification(self, soup):
        section = soup.find_all('section')
        classification = 'None'
        for s in section:
            s_text = s.find_next().text
            if 'Classifications' in s_text:
                classification = s.text
        return classification

    # def get_assignee_inventor_date(self, patent_num):
    #     err, soup, url = self.scraper.request_single_patent(patent_num)
        
    #     # ~ Parse results of scrape ~ #
    #     patent_parsed = self.scraper.get_scraped_data(soup, patent_num, url)

    #     inventor = eval(patent_parsed['inventor_name'])[0]['inventor_name']
    #     assignee = eval(patent_parsed['assignee_name_orig'])[0]['assignee_name']
    #     date = patent_parsed['pub_date']

    #     return assignee, inventor, date
    
    # def save_data(self, data_ls):

    #     scraped_data = pd.DataFrame(data_ls)
    #     scraped_data.to_excel('./Data/Google_Patents_Data.xlsx')

    # This is the main function that will scrape all data:
    def main(self):
        
        all_details = []

        date, c_time = str(datetime.now()).split()
        print('\nStart Time: ', c_time, '\n')
        
        # Delete old records before adding new one:
        # Google_Patent.objects.all().delete()
        self.pro_pq_obj.searching_links_from_projectpq(self.search)
        all_patents_url = self.pro_pq_obj.get_all_links()

        # count = 0
        # while len(all_details) < 50:
            # url = self.main_url.format(self.search, count)
            # soup = self.get_soup(url)
            # all_ref_num = self.get_all_ref_num(soup)
            
        for num in tqdm(range(len(all_patents_url))):
            if len(all_details) == 50:
                break
            
            # patent_url = 'https://patents.google.com/patent/{0}?oq={1}'.format(all_ref_num[num], self.search)
            patent_url, inventor, assignee, date = all_patents_url[num]
            soup = self.get_soup(patent_url)
            all_headings = self.get_all_headings(soup)
            title_text = soup.title.text
            if 'Error' not in title_text:
                # assignee, inventor, date = self.get_assignee_inventor_date(all_ref_num[num])
                header = title_text.split(' - ')
                try:
                    abstract = " ".join(soup.find('abstract').text.split())
                except:
                    abstract = 'None'
                try:
                    # patent_num = soup.find('h2').text
                    patent_num = header[0]
                except:
                    patent_num = 'None'
                try:
                    # title = " ".join(soup.find('h1', id = 'title').text.split())
                    title = " ".join(header[1].split())
                except:
                    title = 'None'
                try:
                    try:
                        classification = " ".join(soup.find('classification-viewer').text.split())
                    except:
                        classification = self.get_classification(soup)
                except:
                    classification = 'None'
                try:
                    # claims = " ".join(soup.find('section', id = 'claims').text.split())
                    claims = soup.find('section', itemprop = 'claims').text
                except:
                    claims = 'None'
                try:
                    # images = [i['src'] for i in soup.find('image-carousel').find_all('img')]
                    images = [i.find('img')['src'] for i in soup.find_all('li', itemprop = 'images')]
                except:
                    images = 'None'
                try:
                    try:
                        background = self.get_text_by_tags(soup, 'background-art')
                    except:
                        background = self.get_headings_paragraph('background', all_headings, 'summary', soup)
                except:
                    background = 'None'
                try:
                    try:
                        summary = self.get_text_by_tags(soup, 'summary-of-invention') # To be done
                    except:
                        summary = self.get_headings_paragraph('summary', all_headings, 'drawing', soup)
                except:
                    summary = 'None'
                try:
                    tech_field = self.get_text_by_tags(soup, 'technical-field')
                except:
                    tech_field = 'None'
                try:
                    try:
                        drawing = self.get_text_by_tags(soup, 'description-of-drawings')
                    except:
                        drawing = self.get_headings_paragraph('drawing', all_headings, 'detail', soup)
                except:
                    drawing = 'None'
                try:
                    try:
                        detail_desc = self.get_text_by_tags(soup, 'description-of-embodiments')
                    except:
                        try:
                            detail_desc = self.get_text_by_tags(soup, 'disclosure')
                        except:
                            detail_desc = self.get_headings_paragraph('detail', all_headings, None, soup)
                except:
                    detail_desc = 'None'
                try:
                    try:
                        description = self.get_text_by_tags(soup, 'description')
                    except:
                        description = self.get_description('background', all_headings, soup)
                except:
                    description = "{0}\n{1}\n{2}\n{3}\n{4}".format(background, summary, tech_field, drawing, detail_desc).replace('None', '')
                
                dic = {
                    "assignee": assignee,
                    "inventor": inventor,
                    "date": date,
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

                Google_Patent.objects.create(**dic)
                
                # print('\n----------Dic-----------\n', dic)

                # self.save_data(all_details)

                # with open('google_patent_results.json', 'w') as outfile:
                #     json.dump(all_details, outfile)
            
            # count += 10
        
        # Google_Patent.objects.bulk_create([Google_Patent(**item) for item in all_details])
        
        date, c_time = str(datetime.now()).split()
        print('\nEnd Time: ', c_time, '\n')

        print('\n-------------------- SCRAPING DONE --------------------\n')

        return all_details
