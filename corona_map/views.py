from django.shortcuts import render
from urllib.parse import unquote
import pandas as pd
import folium
import json

import matplotlib.pyplot as plt
plt.rc("font", family="Malgun Gothic")



# Create your views here.
def coIs_home(request):
    return render(request, 'corona_map/coIs_home.html')

# 서울 지도
def seoul(request):
    m = folium.Map([37.562600, 126.991732], zoom_start=11)

    with open('corona_map/static/json_data/seoul_line.json', mode='rt', encoding='utf-8') as sl:
        geo = json.loads(sl.read())
        sl.close()

    folium.Marker(
        location=[37.5838699, 127.0565831],
        popup=f'한국',
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

# 한국 지도에서 시도별, 확진자 수
# sidoinfo_state() 함수 사용
def folium_page(request):
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
    # print(sido_data_list)
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
        folium.Marker([si_ma['위도'], si_ma['경도']],
            popup=si_ma['시'], #.decode('cp949').encode('utf-8')
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)

    m = m._repr_html_()  # updated
    context = {'mapdata': m}
    return render(request, 'corona_map/folium_page.html', context)

