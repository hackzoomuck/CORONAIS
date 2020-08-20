from django.shortcuts import render
from urllib.parse import unquote
from bs4 import BeautifulSoup
import pandas as pd
import folium
import json
import requests
import corona_map.MongoDbManager as comong
from corona_map.Api.Infection_city import infection_city
import pymongo
# 현재날짜를 사용하기 위한 모듈
import datetime
# import matplotlib.pyplot as plt
# plt.rc("font", family="Malgun Gothic")


# 템플릿 적용
def cois_main(request):
    # 수녕, 서율, 지은
    sido_serviceKey = ['0',
                       'hFxBvUwCFBcRvWK6wJdgZXgFmjnogBAgCMQ%2BWfZmCQngtc%2FkNb%2FvVqfS2ouV%2BxKMAbEbE94ZYhW3m6A3hxKyig%3D%3D',
                       '2']
    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson'
    SERVICE_KEY = unquote(sido_serviceKey[1])
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': 100,
        'numOfRows': 100,
        'startCreateDt': 20200811,
        'endCreateDt': 20200818
    }
    res = requests.get(url, params=params)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    item_list = soup.select('item')
    item_list_result = []
    for idx, item in enumerate(item_list, 1):
        item_dict = {}
        # 등록일시분초 2020-08-14 10:36:59.393
        item_dict['createdt'] = item.find('createdt').string
        # 기준일시2020년 08월 14일 00시
        item_dict['stdday'] = item.find('stdday').string
        # 시도명(한글)
        item_dict['gubun'] = item.find('gubun').string
        # 시도명(영어)
        item_dict['gubunen'] = item.find('gubunen').string
        # 전일대비 증감 수
        item_dict['incdec'] = item.find('incdec').string
        # 격리 해제 수
        item_dict['isolclearcnt'] = item.find('isolclearcnt').string
        # 10만명당 발생률
        item_dict['qurrate'] = item.find('qurrate').string
        # 사망자 수
        item_dict['deathcnt'] = int(item.find('deathcnt').string)
        # 격리중 환자수
        item_dict['isolingcnt'] = item.find('isolingcnt').string
        # 해외유입 수
        item_dict['overflowcnt'] = item.find('overflowcnt').string
        # 지역발생 수
        item_dict['localocccnt'] = int(item.find('localocccnt').string)
        item_list_result.append(item_dict)
    item_df = pd.DataFrame(
        columns=['createdt', 'stdday', 'gubun', 'gubunen', 'incdec', 'isolclearcnt', 'qurrate', 'deathcnt',
                 'isolingcnt', 'overflowcnt',
                 'localocccnt'])
    for a in item_list_result:
        a_object = pd.Series(a)
        item_df = item_df.append(a_object, ignore_index=True)

    totalCount = item_df['deathcnt'].sum()

    # 지역별 확진자 현황
    barPlotData = item_df[['gubun', 'localocccnt']].groupby('gubun').sum()
    barPlotData = barPlotData.reset_index()
    barPlotData = barPlotData.loc[barPlotData['gubun'] != '합계']
    barPlotData.columns = ['gubun', 'localocccnt']
    barPlotData = barPlotData.sort_values(by='localocccnt', ascending=False)
    barPlotVals = barPlotData['localocccnt'].values.tolist()
    gubunNames = barPlotData['gubun'].values.tolist()

    # 날자별 코로나 현황
    lineChartData = item_df[['stdday', item_df.columns[-1]]].groupby('stdday').sum()
    lineChartData = lineChartData.reset_index()
    lineChartData.columns = ['stdday', 'localocccnt']
    lineChartData = lineChartData.sort_values(by='localocccnt', ascending=True)
    lineChartVals = lineChartData['localocccnt'].values.tolist()
    dateTimes = lineChartData['stdday'].values.tolist()

    context = {'totalCount': totalCount, 'barPlotVals': barPlotVals, 'gubunNames': gubunNames,
               'lineChartVals': lineChartVals, 'dateTimes': dateTimes}
    return render(request, 'corona_map/index.html', context)




# 서울 지도
def seoul(request):
    m = folium.Map([37.562600, 126.991732], zoom_start=11)

    with open('corona_map/static/json_data/seoul_line.json', mode='rt', encoding='utf-8') as sl:
        geo = json.loads(sl.read())
        sl.close()

    folium.Marker(
        location=[37.5838699, 127.0565831],
        popup='한국',
        icon=folium.Icon(color='red', icon='star')
    ).add_to(m)
    folium.GeoJson(
        geo,
        name='seoul_line'
    ).add_to(m)

    m = m._repr_html_()  # updated
    context = {'my_map': m}
    return render(request, 'corona_map/seoul.html', context)


# 시도별 api 에서 {시도, 확진자 수} 데이터 전처리 함수
def sidoinfo_state():
    # 수녕, 서율, 지은
    sido_serviceKey = ['0',
                       'hFxBvUwCFBcRvWK6wJdgZXgFmjnogBAgCMQ%2BWfZmCQngtc%2FkNb%2FvVqfS2ouV%2BxKMAbEbE94ZYhW3m6A3hxKyig%3D%3D',
                       '2']

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
        gubun_tag = soup.select('item gubun')
        defcnt_tag = soup.select('item defcnt') #확진자 수
        gubun = []
        defcnt = []
        for gu in gubun_tag:
            gubun.append(gu.text)
        for de in defcnt_tag:
            defcnt.append(de.text)

        sido = dict(zip(gubun,defcnt))
        return sido
    # now = datetime.datetime.now()
    # nowDate = int(now.strftime('%Y%m%d'))
    # seoul = comong.Infection_City().get_users_from_collection({'id':nowDate})
    # seoul_list=[]
    # for s in seoul:
    #     seoul_list.append(s)
    # return render(request, 'corona_map/sidoinfo_state.html', {'soup_data': seoul_list})


# 한국 지도에서 시도별, 확진자 수
# sidoinfo_state() 함수 사용
def folium_page(request):
    # mongodb collection infection_city에 api request해서 데이터 저장.
    infection_city()
    # seoul = comong.Infection_City().get_users_from_collection({})
    # print(seoul)
    soup_sido_data_list = sidoinfo_state()
    geo_sido_data = 'corona_map/static/json_data/korea_sido.json'
    with open(geo_sido_data, "r", encoding="utf8") as f:
        contents = f.read()
        json_data = json.loads(contents)
    data_df = pd.DataFrame(columns=['시', '확진자'])
    sido_data_list = []
    for k, v in soup_sido_data_list.items():
        sido_data = {}
        sido_data['시'] = k
        sido_data['확진자'] = int(v)
        sido_data_list.append(sido_data)
    sido_data_list.pop(0)
    sido_data_list.pop()

    for sido_data in sido_data_list:
        series_obj = pd.Series(sido_data)
        data_df = data_df.append(series_obj, ignore_index=True)
    # 서울시 중심부의 위도, 경도
    seoul_center = [36.3, 127.8]
    # 맵이 center 에 위치하고, zoom 레벨은 7로 시작하는 맵 m
    m = folium.Map(location=seoul_center, zoom_start=6)
    # Choropleth 레이어를 만들고, 맵 m에 추가
    folium.Choropleth(
        geo_data=json_data,
        data=data_df,
        columns=('시', '확진자'),
        key_on='feature.properties.CTP_KOR_NM',
        fill_color='PuRd',
        legend_name='확진자', ).add_to(m)

    sido_lati_longi = [{'시':'제주','위도':33.37,'경도':126.52},{'시':'경남','위도':0,'경도':0},{'시':'경북','위도':0,'경도':0},\
                       {'시':'전남','위도':0,'경도':0},{'시':'전북','위도':0,'경도':0},{'시':'충남','위도':0,'경도':0} ,\
                       {'시':'충북','위도':0,'경도':0},{'시':'강원','위도':0,'경도':0},{'시':'경기','위도':0,'경도':0},\
                       {'시':'세종','위도':0,'경도':0},{'시':'울산','위도':35.53,'경도':129.31},{'시':'대전','위도':36.35,'경도':127.38},\
                       {'시':'광주','위도':35.16,'경도':126.85},{'시':'인천','위도':37.45,'경도':126.70},{'시':'대구','위도':35.87,'경도':128.60},\
                       {'시':'부산','위도':35.18,'경도':129.07},{'시':'서울','위도':37.56,'경도':126.97},]
    for si_ma in sido_lati_longi:
        sido_html = '<h4>{}</h4><a href="http://192.168.0.16:8000/seoul/" target="_blank">{}</a>'.format(si_ma['시'], '서울')
        folium.Marker([si_ma['위도'], si_ma['경도']],
            popup=folium.map.Popup(sido_html, parse_html=False), #.decode('cp949').encode('utf-8')
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)

    m = m._repr_html_()  # updated
    context = {'mapdata': m}
    return render(request, 'corona_map/folium_page.html', context)

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
        # 시도명(한글)
        item_dict['gubun'] = item.find('gubun').string
        # 시도명(영어)
        item_dict['gubunen'] = item.find('gubunen').string
        # 전일대비 증감 수
        item_dict['incdec'] = int(item.find('incdec').string)
        # 격리 해제 수
        item_dict['isolclearcnt'] = int(item.find('isolclearcnt').string)
        # 10만명당 발생률
        item_dict['qurrate'] = item.find('qurrate').string
        # 사망자 수
        item_dict['deathcnt'] = int(item.find('deathcnt').string)
        # 격리중 환자수
        item_dict['isolingcnt'] = int(item.find('isolingcnt').string)
        # 해외유입 수
        item_dict['overflowcnt'] = int(item.find('overflowcnt').string)
        # 지역발생 수
        item_dict['localocccnt'] = int(item.find('localocccnt').string)
        item_list_result.append(item_dict)
    item_df = pd.DataFrame(columns=['gubun', 'gubunen', 'incdec', 'isolclearcnt', 'qurrate', 'deathcnt', 'isolingcnt', 'overflowcnt', 'localocccnt'])
    for a in item_list_result:
        a_object = pd.Series(a)
        item_df = item_df.append(a_object, ignore_index=True)
    return render(request, 'corona_map/coIs_home.html', {'soup_data': soup})

def chart_bar(request):
    # 수녕, 서율, 지은
    sido_serviceKey = ['0',
                       'hFxBvUwCFBcRvWK6wJdgZXgFmjnogBAgCMQ%2BWfZmCQngtc%2FkNb%2FvVqfS2ouV%2BxKMAbEbE94ZYhW3m6A3hxKyig%3D%3D',
                       '2']
    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson'
    SERVICE_KEY = unquote(sido_serviceKey[1])
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': 100,
        'numOfRows': 100,
        'startCreateDt': 20200811,
        'endCreateDt': 20200818
    }
    res = requests.get(url, params=params)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    item_list = soup.select('item')
    item_list_result = []
    for idx, item in enumerate(item_list, 1):
        item_dict = {}
        # 등록일시분초 2020-08-14 10:36:59.393
        item_dict['createdt'] = item.find('createdt').string
        # 기준일시2020년 08월 14일 00시
        item_dict['stdday'] = item.find('stdday').string
        # 시도명(한글)
        item_dict['gubun'] = item.find('gubun').string
        # 시도명(영어)
        item_dict['gubunen'] = item.find('gubunen').string
        # 전일대비 증감 수
        item_dict['incdec'] = item.find('incdec').string
        # 격리 해제 수
        item_dict['isolclearcnt'] = item.find('isolclearcnt').string
        # 10만명당 발생률
        item_dict['qurrate'] = item.find('qurrate').string
        # 사망자 수
        item_dict['deathcnt'] = int(item.find('deathcnt').string)
        # 격리중 환자수
        item_dict['isolingcnt'] = item.find('isolingcnt').string
        # 해외유입 수
        item_dict['overflowcnt'] = item.find('overflowcnt').string
        # 지역발생 수
        item_dict['localocccnt'] = int(item.find('localocccnt').string)
        item_list_result.append(item_dict)
    item_df = pd.DataFrame(
        columns=['createdt', 'stdday', 'gubun', 'gubunen', 'incdec', 'isolclearcnt', 'qurrate', 'deathcnt', 'isolingcnt', 'overflowcnt',
                 'localocccnt'])
    for a in item_list_result:
        a_object = pd.Series(a)
        item_df = item_df.append(a_object, ignore_index=True)

    totalCount = item_df['deathcnt'].sum()

    # 지역별 확진자 현황
    barPlotData = item_df[['gubun', 'localocccnt']].groupby('gubun').sum()
    barPlotData = barPlotData.reset_index()
    barPlotData = barPlotData.loc[barPlotData['gubun'] != '합계']
    barPlotData.columns = ['gubun', 'localocccnt']
    barPlotData = barPlotData.sort_values(by='localocccnt', ascending=False)
    barPlotVals = barPlotData['localocccnt'].values.tolist()
    gubunNames = barPlotData['gubun'].values.tolist()

    # 날자별 코로나 현황
    lineChartData = item_df[['stdday', item_df.columns[-1]]].groupby('stdday').sum()
    lineChartData = lineChartData.reset_index()
    lineChartData.columns = ['stdday', 'localocccnt']
    lineChartData = lineChartData.sort_values(by='localocccnt', ascending=True)
    lineChartVals = lineChartData['localocccnt'].values.tolist()
    dateTimes = lineChartData['stdday'].values.tolist()

    context = {'totalCount': totalCount, 'barPlotVals': barPlotVals, 'gubunNames': gubunNames, 'lineChartVals': lineChartVals, 'dateTimes': dateTimes}
    return render(request, 'corona_map/chart_bar.html', context)


def chart_bar_by_age_gender(request):
    serviceKey = '67xjSd3vhpWMN4oQ3DztMgLyq4Aa1ugw1ssq%2FHeJAeniNIwyPspLp7XpNoa8mBbTJQPc3dAxqvtFm57fJIfq8w%3D%3D'
    numOfRows = 10
    pageNo = 10
    startCreateDt = '20200310'
    endCreateDt = '20200814'  # datetime.datetime.now()
    url = f'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19GenAgeCaseInfJson?serviceKey={serviceKey}&numOfRows={numOfRows}&pageNo={pageNo}&startCreateDt={startCreateDt}&endCreateDt={endCreateDt}'
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    item_list = soup.select('item')
    item_list_result = []
    for idx, item in enumerate(item_list, 1):
        item_dict = {}
        # 확진자
        item_dict['confcase'] = int(item.find('confcase').string)
        # 확진률
        item_dict['confcaserate'] = item.find('confcaserate').string
        # 등록일시분초
        item_dict['createdt'] = item.find('createdt').string
        # 치명률
        item_dict['criticalrate'] = float(item.find('criticalrate').string)
        # 사망자
        item_dict['death'] = int(item.find('death').string)
        # 사망률
        item_dict['deathrate'] = item.find('deathrate').string
        # 구분(성별,연령별)0-9
        item_dict['gubun'] = item.find('gubun').string

        item_list_result.append(item_dict)
    item_df = pd.DataFrame(columns=['confcase', 'confcaserate', 'createdt', 'criticalrate', 'death', 'deathrate', 'gubun'])
    for a in item_list_result:
        a_object = pd.Series(a)
        item_df = item_df.append(a_object, ignore_index=True)

    totalCount = item_df['death'].sum()

    # 연령별 치명률 시각화
    oldPlotData = item_df[['gubun', 'criticalrate']].groupby('gubun').mean()
    oldPlotData = oldPlotData.reset_index()
    oldPlotData.columns = ['gubun', 'criticalrate']
    oldPlotData = oldPlotData.sort_values(by='criticalrate', ascending=False)
    oldPlotData = oldPlotData.loc[(oldPlotData['gubun'] != '여성') & (oldPlotData['gubun'] != '남성')]
    oldPlotVals = oldPlotData['criticalrate'].values.tolist()
    oldGubunNames = oldPlotData['gubun'].values.tolist()

    # 성별 치명률 시각화
    genderPlotData = item_df[['gubun', 'criticalrate']].groupby('gubun').mean()
    genderPlotData = genderPlotData.reset_index()
    genderPlotData.columns = ['gubun', 'criticalrate']
    genderPlotData = genderPlotData.sort_values(by='criticalrate', ascending=False)
    genderPlotData = genderPlotData.loc[(genderPlotData['gubun'] == '여성') | (genderPlotData['gubun'] == '남성')]
    genderPlotVals = genderPlotData['criticalrate'].values.tolist()
    genderGubunNames = genderPlotData['gubun'].values.tolist()

    context = {'totalCount': totalCount, 'oldPlotVals': oldPlotVals, 'oldGubunNames': oldGubunNames, 'genderPlotVals': genderPlotVals, 'genderGubunNames': genderGubunNames}
    return render(request, 'corona_map/by_age_gender.html', context)

