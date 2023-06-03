from django.contrib import admin
from django.urls import path, re_path
from scraping.views import *


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', google_patent, name = 'google_patent'),
    # path('google_patent_results', google_patent_results, name = 'google_patent_results'),
    path('google_patent_results_download', google_patent_results_download, name = 'google_patent_results_download'),
    path('scraped_data', scraped_data, name = 'scraped_data'),
    re_path('^start_scraper/(?P<search>.+)/$', Start_Patent_Scraper.as_view()),
]