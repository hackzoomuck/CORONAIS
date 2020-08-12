from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote

# Create your views here.
# 수녕, 서율, 지은
sido_serviceKey = ['0','hFxBvUwCFBcRvWK6wJdgZXgFmjnogBAgCMQ%2BWfZmCQngtc%2FkNb%2FvVqfS2ouV%2BxKMAbEbE94ZYhW3m6A3hxKyig%3D%3D','2']

def coIs_home(request):
    return render(request, 'corona_map/coIs_home.html')

def sidoinfo_state(request):
    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson'
    SERVICE_KEY = unquote(sido_serviceKey[1])

    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': 1,
        'numOfRows': 1,
        'startCreateDt': 20200811,
        'endCreateDt': 20200811
    }


    res = requests.get(url, params=params)
    if res.status_code == 200:
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        print('#################################')
        print(soup)
        return render(request, 'corona_map/sidoinfo_state.html')

    else:
        return render(request, 'corona_map/coIs_home.html')