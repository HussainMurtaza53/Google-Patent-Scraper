from threading import Thread
from scraping.google_patent_scraper import Google_Patent_Scraper


class Google_Patent_Scraper_Thread(Thread):

    # Constructor to save website which we will pass while calling Scraper class:
    def __init__(self, search):

        self.search = search
        
        Thread.__init__(self)

    def run(self):

        self.scrape(self.search)

    def scrape(self, search):
        gp_scraper = Google_Patent_Scraper(search)
        patents = gp_scraper.main()