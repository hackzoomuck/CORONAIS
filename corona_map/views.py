from django.shortcuts import render
from urllib.parse import unquote
from bs4 import BeautifulSoup
import pandas as pd
import folium
import json
import requests
import corona_map.MongoDbManager as comong
from corona_map.Api import Infection_city, Infection_status, Infection_by_age_gender, News_board
import pymongo
import datetime


import corona_map.MongoDbManager as comong
from corona_map.Api.Infection_city import infection_city
from corona_map.Api.Infection_by_age_gender import infection_by_age_gender
from corona_map.Api.Infection_status import infection_status

from corona_map.Api.Gugun_status import get_seoul_data_list
from corona_map.Api.data_init import seoul_data_init

def call_data_init(request):
    seoul_data_init()
    return render(request, 'corona_map/coIs_home.html', {'soup_data': 'call_data_init에서 넘어옴'})

def call_gugun_info(request):
    get_seoul_data_list()
    return render(request, 'corona_map/coIs_home.html', {'soup_data': 'call_gugun_info에서 넘어옴'})

# infection_city collection 에서 {시도, 확진자 수} 데이터 전처리 함수
def infection_city_all_values():
    now = datetime.datetime.now()
    # 오늘 날짜 했는 데, 아직 시도별 api 데이터가 업데이트 되지 않아서 지난 날 것을 호출함.
    nowDate = int(now.strftime('%Y%m%d'))-1
    # 하루의 시도별 데이터
    infection_date_data = comong.Infection_City().get_users_from_collection({})

    infection_city_all_values_list = []
    for idd in infection_date_data:
        item_dict = {}
        # 등록일시분초 2020-08-14 10:36:59.393
        item_dict['createdt'] = idd['createdt']
        # 기준일시2020년 08월 14일 00시
        item_dict['stdday'] = idd['stdday']
        # 확진자 수(총 확진자 수)
        item_dict['defcnt'] = idd['defcnt']
        # 시도명(한글)
        item_dict['gubun'] = idd['gubun']
        # 시도명(영어)
        item_dict['gubunen'] = idd['gubunen']
        # 전일대비 증감 수
        item_dict['incdec'] = idd['incdec']
        # 격리 해제 수
        item_dict['isolclearcnt'] = idd['isolclearcnt']
        # 사망자 수
        item_dict['deathcnt'] = idd['deathcnt']
        # 격리중 환자수
        item_dict['isolingcnt'] = idd['isolingcnt']
        infection_city_all_values_list.append(item_dict)

    return infection_city_all_values_list

# infection_state collection 전국 코로나 현황 수 get함수
def infection_state_all_value():
    now = datetime.datetime.now()
    # 오늘 날짜 호출함.
    nowDate = int(now.strftime('%Y%m%d'))-1
    # 하루의 시도별 데이터
    infection_date_data = comong.Infection_Status().get_users_from_collection({'id': nowDate})

    item_dict = {}
    for idd in infection_date_data:
        # 확진자 수
        item_dict['decidecnt'] = idd['decidecnt']
        # 격리해제 수
        item_dict['clearcnt'] = idd['clearcnt']
        # 검사진행 수
        item_dict['examcnt'] = idd['examcnt']
        # 사망자 수
        item_dict['deathcnt'] = idd['deathcnt']
    print(item_dict)
    return item_dict

# 템플릿 적용
def cois_main(request):
    
    item_list_result=infection_city_all_values()
    in_st_dict = infection_state_all_value()
    item_df = pd.DataFrame(
        columns=['createdt', 'stdday', 'defcnt', 'gubun', 'gubunen', 'incdec', 'isolclearcnt', 'deathcnt', 'isolingcnt'])
    for a in item_list_result:
        a_object = pd.Series(a)
        item_df = item_df.append(a_object, ignore_index=True)

    totalCount = item_df['deathcnt'].sum()

    # 지역별 확진자 현황
    barPlotData = item_df[['gubun', 'defcnt']].groupby('gubun').sum()
    barPlotData = barPlotData.reset_index()
    barPlotData = barPlotData.loc[barPlotData['gubun'] != '합계']
    barPlotData.columns = ['gubun', 'defcnt']
    barPlotData = barPlotData.sort_values(by='defcnt', ascending=False)
    barPlotVals = barPlotData['defcnt'].values.tolist()
    gubunNames = barPlotData['gubun'].values.tolist()

    # 날자별 코로나 현황
    lineChartData = item_df[['stdday', item_df.columns[-1]]].groupby('stdday').sum()
    lineChartData = lineChartData.reset_index()
    lineChartData.columns = ['stdday', 'defcnt']
    lineChartData = lineChartData.sort_values(by='defcnt', ascending=True)
    lineChartVals = lineChartData['defcnt'].values.tolist()
    dateTimes = lineChartData['stdday'].values.tolist()

    ##################################################################################
    # 성별, 연령별 조회
    sido_serviceKey = ['0',
                       '%2BNZvj3PPWZaxtFa6tqekV3%2BWlT4NSYB4HY5kXLacieOJKfCtyZpafsGzvJsZzvOMg2KUGrKEIQyy9k58uA1g1A%3D%3D',
                       '2']
    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19GenAgeCaseInfJson'
    SERVICE_KEY = unquote(sido_serviceKey[1])
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': 10,
        'numOfRows': 10,
        'startCreateDt': 20200811,
        'endCreateDt': 20200818
    }
    response = requests.get(url, params=params)

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
        try:
            item_dict['criticalrate'] = float(item.find('criticalrate').string)
        except Exception:
            item_dict['criticalrate'] = 0
        # 사망자
        item_dict['death'] = int(item.find('death').string)
        # 사망률
        item_dict['deathrate'] = item.find('deathrate').string
        # 구분(성별,연령별)0-9
        item_dict['gubun'] = item.find('gubun').string

        item_list_result.append(item_dict)
    item_df = pd.DataFrame(
        columns=['confcase', 'confcaserate', 'createdt', 'criticalrate', 'death', 'deathrate', 'gubun'])
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

    context = {'totalCount': totalCount, 'barPlotVals': barPlotVals, 'gubunNames': gubunNames,
               'lineChartVals': lineChartVals, 'dateTimes': dateTimes, 'oldPlotVals': oldPlotVals, 'oldGubunNames': oldGubunNames,
               'genderPlotVals': genderPlotVals, 'genderGubunNames': genderGubunNames, 'decideCnt': in_st_dict['decidecnt'],'clearCnt': in_st_dict['clearcnt'],'examCnt': in_st_dict['examcnt'],'deathCnt': in_st_dict['deathcnt']}

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


# infection_city collection 에서 {시도, 확진자 수} 데이터 전처리 함수
def infection_city_gubun_defcnt():
    now = datetime.datetime.now()
    # 오늘 날짜 했는 데, 아직 시도별 api 데이터가 업데이트 되지 않아서 지난 날 것을 호출함.
    nowDate = int(now.strftime('%Y%m%d'))-1
    # 하루의 시도별 데이터
    infection_date_data = comong.Infection_City().get_users_from_collection({'id':nowDate})

    gubun = []
    defcnt = []
    for idd in infection_date_data:
        gubun.append(idd['gubun'])
        defcnt.append(idd['defcnt'])
    # {시도:확진자 수}
    dict_gubun_defcnt = dict(zip(gubun,defcnt))
    return dict_gubun_defcnt


# 한국 지도에서 시도별, 확진자 수
# infection_city_gubun_defcnt() 함수 사용
def folium_page(request):
    # mongodb collection infection_city에 api request해서 데이터 저장.
    print(Infection_city.infection_city())
    print(News_board.news_board_list())
    print(Infection_by_age_gender.infection_by_age_gender())
    print(Infection_status.infection_status())

    soup_sido_data_list = infection_city_gubun_defcnt()
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

    sido_lati_longi = [{'시':'제주','위도':33.37,'경도':126.52,'링크':'"https://www.jeju.go.kr/corona19.jsp#corona-main"'},\
                       {'시':'경남','위도':35.3426,'경도':128.7092,'링크':'"http://xn--19-q81ii1knc140d892b.kr/main/main.do#close"'},\
                       {'시':'경북','위도':36.6883,'경도':127.3555,'링크':'"http://www.gb.go.kr/Main/open_contents/section/wel/page.do?mnu_uid=5760&LARGE_CODE=360&MEDIUM_CODE=10&SMALL_CODE=50&SMALL_CODE2=60mnu_order=2"'},\
                       {'시':'전남','위도':34.8951,'경도':127.0315,'링크':'"https://www.jeonnam.go.kr/coronaMainPage.do"'},\
                       {'시':'전북','위도':35.7111,'경도':127.0628,'링크':'"http://www.jeonbuk.go.kr/board/list.jeonbuk?boardId=BBS_0000105&menuCd=DOM_000000110001000000&contentsSid=1219&cpath="'},\
                       {'시':'충남','위도':36.6744,'경도':126.8118,'링크':'"http://www.chungnam.go.kr/coronaStatus.do"'},\
                       {'시':'충북','위도':36.8514,'경도':127.7245,'링크':'"http://www1.chungbuk.go.kr/covid-19/index.do"'},\
                       {'시':'강원','위도':37.7720,'경도':128.4307,'링크':'"http://www.provin.gangwon.kr/covid-19.html"'},\
                       {'시':'경기','위도':37.4673,'경도':127.2832,'링크':'"https://www.gg.go.kr/contents/contents.do?ciIdx=1150&menuId=2909"'},\
                       {'시':'세종','위도':36.4775,'경도':127.2902,'링크':'"https://www.sejong.go.kr/bbs/R3273/list.do;jsessionid=o6jTyarJU9zCvVIWG455Wxp12IDT6Ko4ELucV5fpauxN93LAVXwjiLSIhTYiPxxr.Portal_WAS1_servlet_engine5?cmsNoStr=17465"'},\
                       {'시':'울산','위도':35.53,'경도':129.31,'링크':'"http://www.ulsan.go.kr/corona.jsp"'},\
                       {'시':'대전','위도':36.35,'경도':127.38,'링크':'"https://www.daejeon.go.kr/corona19/index.do"'},\
                       {'시':'광주','위도':35.16,'경도':126.85,'링크':'"https://www.gwangju.go.kr/c19/"'},\
                       {'시':'인천','위도':37.45,'경도':126.70,'링크':'"https://www.incheon.go.kr/health/HE020409"'},\
                       {'시':'대구','위도':35.87,'경도':128.60,'링크':'"http://covid19.daegu.go.kr/"'},\
                       {'시':'부산','위도':35.18,'경도':129.07,'링크':'"http://www.busan.go.kr/covid19/Corona19.do"'},\
                       {'시':'서울','위도':37.56,'경도':126.97,'링크':'"http://127.0.0.1:8000/seoul/"'}]


    for si_ma in sido_lati_longi:
        sido_html = '<h4>{}</h4><h4>총 확진자 {}</h4><a href='.format(si_ma['시'], soup_sido_data_list[si_ma['시']])+si_ma['링크']+'target="_blank">{}</a>'.format(si_ma['시'])
        folium.Marker([si_ma['위도'], si_ma['경도']],
            popup=folium.map.Popup(sido_html, parse_html=False, max_width=200), #.decode('cp949').encode('utf-8')
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)

    m = m._repr_html_()  # updated
    context = {'mapdata': m}
    return render(request, 'corona_map/folium_page.html', context)


def coIs_home(request):
    # 수녕, 서율, 지은
    sido_serviceKey = ['0',
                       'BjW9a8K51p0oRJ0hl%2BBpizJzZ9gT3e%2Beb75QhG9kXdeK9ENW7CCAl9nX28%2BRD97JlAsDrTv7StIwvUPCxA4iTw%3D%3D',
                       '2']
    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson'
    SERVICE_KEY = unquote(sido_serviceKey[1])
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': 10,
        'numOfRows': 10,
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
        try:
            # 확진자 수
            item_dict['decidecnt'] = int(item.find('decidecnt').string)
        except (AttributeError, KeyError):
            item_dict['decidecnt'] = 0
        # 격리해제 수
        try:
            item_dict['clearcnt'] = int(item.find('clearcnt').string)
        except (AttributeError, KeyError):
            item_dict['clearcnt'] = 0
        # 검사진행 수
        item_dict['examcnt'] = int(item.find('examcnt').string)
        # 사망자 수
        item_dict['deathcnt'] = int(item.find('deathcnt').string)
        # 결과 음성 수
        item_dict['resutlnegcnt'] = int(item.find('resutlnegcnt').string)
        # 누적 검사 수
        item_dict['accexamcnt'] = int(item.find('accexamcnt').string)
        # 누적 검사 완료 수
        item_dict['accexamcompcnt'] = int(item.find('accexamcompcnt').string)
        # 누적 환진률
        item_dict['accdefrate'] = item.find('accdefrate').string
        # 기준일
        item_dict['statedt'] = item.find('statedt').string
        # 기준시간
        item_dict['statetime'] = item.find('statetime').string
        item_list_result.append(item_dict)
    # item_df = pd.DataFrame(columns=['gubun', 'gubunen', 'incdec', 'isolclearcnt', 'qurrate', 'deathcnt', 'isolingcnt', 'overflowcnt', 'localocccnt'])
    # for a in item_list_result:
    #     a_object = pd.Series(a)
    #     item_df = item_df.append(a_object, ignore_index=True)
    return render(request, 'corona_map/coIs_home.html', {'soup_data': item_list_result})

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

    sido_serviceKey = ['0',
                       '%2BNZvj3PPWZaxtFa6tqekV3%2BWlT4NSYB4HY5kXLacieOJKfCtyZpafsGzvJsZzvOMg2KUGrKEIQyy9k58uA1g1A%3D%3D',
                       '2']
    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19GenAgeCaseInfJson'
    SERVICE_KEY = unquote(sido_serviceKey[1])
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': 10,
        'numOfRows': 10,
        'startCreateDt': 20200811,
        'endCreateDt': 20200818
    }
    response = requests.get(url, params=params)

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
        try:
            item_dict['criticalrate'] = float(item.find('criticalrate').string)
        except Exception:
            item_dict['criticalrate'] = 0
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
    return render(request, 'corona_map/by_age_gender_piechart.html', context)

from urllib.parse import urljoin

def news_board_list(request):
    main_url = 'https://yna.co.kr'
    url = 'https://ars.yna.co.kr/api/v2/sokbo?lang=KR&count=100&minute=800'
    response = requests.get(url)
    json_text = response.json()
    json_url_list = []
    json_data = json_text['DATA']
    word = '코로나'
    for json_url in json_data:
        title_url_dict = dict()
        title_url_dict['datetime'] = json_url['DATETIME']
        if word in json_url['TITLE']:
            title_url_dict['url'] = urljoin(main_url, json_url['URL'])
            json_url_list.append(title_url_dict)
    gisa_result_list = []
    for corona_url in json_url_list:
        response = requests.get(corona_url['url'])
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        news_title = soup.select_one('title').text.split('|')[0]
        tag_test = '#articleWrap > div.content01.scroll-article-zone01 > div > div > div.story-news.article p'
        gisa_list = soup.select(tag_test)
        gisa_content_str = ''
        gisa_dict = dict()
        for gisa in gisa_list:
            gisa_content_str += gisa.text
        gisa_dict['datetime'] = corona_url['datetime'][0:8]
        gisa_dict['title'] = news_title
        gisa_dict['content'] = gisa_content_str
        gisa_result_list.append(gisa_dict)
    return render(request, 'corona_map/test_api.html', {'news_board_list': gisa_result_list})
