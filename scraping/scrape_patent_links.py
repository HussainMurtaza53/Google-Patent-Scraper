# Importing all Pre-requisites:
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import os


class ProjectPQ_Scraper():

    # Constructor to save website which we will pass while calling Scraper class:
    def __init__(self):
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        # self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def searching_links_from_projectpq(self, search):
        self.driver.get("https://search.projectpq.ai/")
        textarea = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.TAG_NAME, "textarea")))
        textarea.send_keys(search)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "search-btn"))).click()

    def get_more_links(self):
        WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "btn-primary")))[-2].click()

    def get_all_links(self):
        all_patent_links = []
        page_count = 1
        Condition = True
        while Condition:
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "svelte-srmes2")))
            ibox_contents = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ibox-title")))
            patent_info_elements = self.driver.find_elements(by='class name', value='ibox-content')
            if len(ibox_contents)!= 1:
                if page_count != 6:
                    for ibox_content in range(1, len(ibox_contents)):
                        try:
                            data_id = ibox_contents[ibox_content].get_attribute("data-id")
                            main_url = "https://patents.google.com/patent/{}/en".format(data_id)
                            inventor, assignee, date, *_ = patent_info_elements[ibox_content].text.split('\n')
                            all_patent_links.append((main_url, inventor, assignee, date))
                        except:
                            pass
                    self.get_more_links()
                    print("Page No: "+str(page_count)+" links scraped")
                    page_count +=1
                    Condition = True
                else:
                    return all_patent_links
            else:
                time.sleep(2)
                ibox_contents = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ibox-title")))
                if len(ibox_contents)== 1:
                    return all_patent_links
                else:
                    Condition = True


# search = 'flexible folding phone'
# pro_scraper = ProjectPQ_Scraper()
# pro_scraper.searching_links_from_projectpq(search)
# links = pro_scraper.get_all_links()