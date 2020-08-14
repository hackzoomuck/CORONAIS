from django.shortcuts import render
import requests
import django_pandas as dpd
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import unquote

'''
확진자 수 : decidecnt
격리해제 수 : clearcnt
검사진행 수 : examcnt
사망자 수 : deathcnt
'''
def coIs_home(request):
    # 수녕, 서율, 지은
    sido_serviceKey = ['0',
                       'hFxBvUwCFBcRvWK6wJdgZXgFmjnogBAgCMQ%2BWfZmCQngtc%2FkNb%2FvVqfS2ouV%2BxKMAbEbE94ZYhW3m6A3hxKyig%3D%3D',
                       '2']
    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson'
    SERVICE_KEY = unquote(sido_serviceKey[1])
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': 100,
        'numOfRows': 1,
        'startCreateDt': 20200811,
        'endCreateDt': 20200814
    }
    res = requests.get(url, params=params)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    item_list = soup.select('item')
    item_list_result = []
    for idx, item in enumerate(item_list, 1):
        item_dict = {}
        item_dict['gubun'] = item.find('gubun').string
        item_dict['gubuncn'] = item.find('gubuncn').string
        item_dict['gubunen'] = item.find('gubunen').string
        item_dict['incdec'] = item.find('incdec').string
        item_dict['isolclearcnt'] = item.find('isolclearcnt').string
        item_dict['qurrate'] = item.find('qurrate').string

        item_dict['deathcnt'] = item.find('deathcnt').string
        # 격리중 환자수
        item_dict['isolingcnt'] = item.find('isolingcnt').string
        # 해외유입 수
        item_dict['overflowcnt'] = item.find('overflowcnt').string
        # 지역발생 수
        item_dict['localocccnt'] = item.find('localocccnt').string

        item_list_result.append(item_dict)

    item_df = pd.DataFrame(columns=['decidecnt', 'clearcnt', 'examcnt', 'deathcnt'])
    for a in item_list_result:
        a_object = pd.Series(a)
        item_df = item_df.append(a_object, ignore_index=True)

    return render(request, 'corona_map/coIs_home.html', {'soup_data': item_list})


def chart_bar(request):
    serviceKey = '67xjSd3vhpWMN4oQ3DztMgLyq4Aa1ugw1ssq%2FHeJAeniNIwyPspLp7XpNoa8mBbTJQPc3dAxqvtFm57fJIfq8w%3D%3D'
    numOfRows = 1000
    pageNo = 10
    startCreateDt = '20200310'
    endCreateDt = '20200814'  # datetime.datetime.now()

    url = f'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson?serviceKey={serviceKey}&numOfRows={numOfRows}&pageNo={pageNo}&startCreateDt={startCreateDt}&endCreateDt={endCreateDt}'

    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    item_list = soup.select('item')
    item_list_result = []
    for idx, item in enumerate(item_list, 1):
        item_dict = {}
        item_dict['decidecnt'] = item.find('decidecnt').string
        item_dict['clearcnt'] = item.find('clearcnt').string
        item_dict['examcnt'] = item.find('examcnt').string
        item_dict['deathcnt'] = item.find('deathcnt').string
        item_list_result.append(item_dict)

    item_df = pd.DataFrame(columns=['decidecnt', 'clearcnt', 'examcnt', 'deathcnt'])
    for a in item_list_result:
        a_object = pd.Series(a)
        item_df = item_df.append(a_object, ignore_index=True)
    # f = plt.figure(figsize=(10, 5))
    # gr = sns.barplot(data=item_df.sort_values(by='examcnt'))
    # FigureCanvasAgg(f)
    # buf = BytesIO()
    # gr.savefig(buf, format='png')
    # plt.close(f)
    #
    # response = HttpResponse(buf.getvalue(), content_type='image/png')
    #
    # return response
    totalCount = item_df[item_df.columns[-1]].sum()
    barPlotData = item_df[['']]
    context = {'totalCount': totalCount}
    return render(request, 'corona_map/chart_bar.html', context)
