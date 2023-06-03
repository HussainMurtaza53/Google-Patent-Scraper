from django.shortcuts import render
from scraping.thread import *
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
import json
import pandas as pd
import io
from scraping.models import *

    
def google_patent(request):
    if request.method == 'GET':
        Google_Patent.objects.all().delete()
        search = request.GET.get('search')
        if search:
            Google_Patent_Scraper_Thread(search).start()
            context = {'message': 'In progress'}

            return HttpResponse(json.dumps(context),
                content_type = 'application/json')
        
        return render(request, 'google_patent.html', {'patents_length': 0, 'style': "display: none;"})

def google_patent_results(request):
    # with open('google_patent_results.json') as f:
    #     patents_data = json.load(f)
    
    # data = pd.read_excel('./Data/Google_Patents_Data.xlsx')
    # print('\n----------Data-----------\n', data)
    data = Google_Patent.objects.values()
    patents_data = list(map(lambda i, d: {**d, 'id': i+1}, range(len(data)), data))
    # for d in range(len(data)):
    #     dic = {
    #         "S_No": d+1,
    #         "Title": data['Title'][d],
    #         "Patent_Number": data['Patent_Number'][d],
    #         "Abstract": data['Abstract'][d],
    #         "Classification": data['Classification'][d],
    #         "Claims": data['Claims'][d],
    #         "Images": data['Images'][d],
    #         "Description": data['Description'][d],
    #         "Background": data['Background'][d],
    #         "Summary": data['Summary'][d],
    #         "Technical_Field": data['Technical_Field'][d],
    #         "Description_Of_The_Drawings": data['Description_Of_The_Drawings'][d],
    #         "Description_Of_The_Embodiments": data['Description_Of_The_Embodiments'][d]
    #     }

    #     patents_data.append(dic)
    # print('\n----------Data LS-----------\n', patents_data)
    context = {
        'patents': patents_data,
        'length': len(patents_data),
        'style': "display: block;"
    }
    return render(request, 'google_patent.html', context)

def scraped_data(request):
    # Scrape the data and return it as a JSON response
    data = Google_Patent.objects.values()
    patents_data = list(map(lambda i, d: {**d, 'id': i+1}, range(len(data)), data))
    return JsonResponse(patents_data, safe=False)

def google_patent_results_download(request):
    try:
        data_name = 'Google_Patents_Data.xlsx'
        patents_data = Google_Patent.objects.values()
        data = pd.DataFrame(patents_data)

        try:
            del data['id']
        except:
            pass

        # writer.writerow(["Title", "Patent_Number", "Abstract", "Classification", "Claims", "Images", "Description", "Background", "Summary", "Technical_Field", "Description_Of_The_Drawings", "Description_Of_The_Embodiments"])
        
        # write the DataFrame to a BytesIO object
        excel_buffer = io.BytesIO()
        data.to_excel(excel_buffer, index=False)

        # create an HttpResponse object with the Excel file as the content
        response = HttpResponse(excel_buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(data_name)

        return response
    except:
        context = {'message': 'Fail'}
        return HttpResponse(json.dumps(context),
                content_type = 'application/json')


class Start_Patent_Scraper(APIView):

    def get(self, request, *args, **kwargs):
        
        Google_Patent.objects.all().delete()
        search = str(self.request).split('/')[-2].replace('%20', ' ')
        context = {'message': 'Enter a valid search'}
        if search:
            Google_Patent_Scraper_Thread(search).start()
            context = {'message': 'scraper started'}
        return Response(context)