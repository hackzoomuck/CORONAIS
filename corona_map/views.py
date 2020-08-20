from django.shortcuts import render
from urllib.parse import unquote
from bs4 import BeautifulSoup
import pandas as pd
import folium
import json
import requests
import re
import matplotlib.pyplot as plt
plt.rc("font", family="Malgun Gothic")
'''
 @ sigu_url 크롤링 주소
 @ sigu_name = 도시 이름
 @ cure_cnt_tag = 완치자 태그
 @ sub_cure_cnt_tag = 완치자 계산을 위한 서브 태그
'''
def get_cnt_cure(sigu_url, sigu_name, cure_cnt_tag, sub_cure_cnt_tag):

    res_headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'),
        'Accept': ('text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
        'Cookie': ('WMONID=DKSQRGw_Nxb;')
    }
    res = requests.get(sigu_url, headers=res_headers)
    if 200 <= res.status_code < 400:
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        counter_list = soup.select(cure_cnt_tag)

        try:
            if sigu_name == '영등포구':
                count_int = counter_list[0]['value']
            elif sigu_name == '양천구':
                count_int = counter_list[0].text
                matched = re.search(r'(\d+)', count_int)
                count_int = matched.group(1)
            elif sigu_name == '광진구':
                sub_cure_cnt_tag_list = soup.select(sub_cure_cnt_tag)
                count_int = str(int(counter_list[0].text) + int(sub_cure_cnt_tag_list[0].text))
            else:
                count_int = counter_list[0].text

            # 도시 이름, 완치자
            regex = re.compile(r'[^0-9]')
            count_int = regex.sub('', count_int).replace(r'[^0-9]','')
            print('{}: {} '.format(sigu_name, count_int))
        except Exception as ex:
            print(ex)
            print(sigu_name)

def cure_people(request):
    # http://ncov.mohw.go.kr/ 코로나 바이러스 감염증 중앙대책본부 통계 자료
    
    cities_data_list = []

    sigu_url = 'https://www.seoul.go.kr/coronaV/coronaStatus.do'
    sigu_name = '서울'

    city_data_dict = {
        'city_url' : 'https://www.jongno.go.kr/portalMain.do;jsessionid=WRbjo7mxihEc2FtUXnZ8KUhCfSD3fYAhm2iyQ17E3HY1FDdtV6TOPaw70mYWKyKW.was_servlet_engine1',
        'city_name' : '종로구',
        'cure_cnt_tag' : '#corona19_info > div > div.popup-body > div.coronal-table > table > tbody > tr > td:nth-child(2)',
        'sub_cure_cnt_tag' : ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://www.junggu.seoul.kr/index.jsp#',
        'city_name': '중구',
        'cure_cnt_tag': '#wrap > div.popup_container > div.virus_popup01 > div.popup_body > div > div.col_right.clearfix > div.r_inner_left > div > div > table > tbody > tr > td:nth-child(2)',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://www.yongsan.go.kr/index.htm',
        'city_name': '용산구',
        'cure_cnt_tag': '#wrap > div.layer-popup > div > div.popup-contents.virus > div > div:nth-child(1) > div > table > tbody > tr > td:nth-child(2)',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://www.ddm.go.kr/',
        'city_name': '동대문구',
        'cure_cnt_tag': '#contents > div.inner > section:nth-child(1) > div > table > tbody > tr > td:nth-child(3) > strong',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://c19.jungnang.go.kr/',
        'city_name': '중랑구',
        'cure_cnt_tag': '#jn_intro_wrap > div > div.intro_tbl_box > dl.intro_tbl.jn_intro_tbl > dd:nth-child(3) > span',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://www.sd.go.kr/sd/intro.do',
        'city_name': '성동구',
        'cure_cnt_tag': '#content > div.top_box > div > div.top_area1 > ul > li.alone > span:nth-child(3) > em',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://www.sb.go.kr/',
        'city_name': '성북구',
        'cure_cnt_tag': '#main_popup > div.wrap-div1 > div.box2-n.clearfix > div.con2.style2 > div > div.box1.clearfix > div.box-c.c1 > p > span.num',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://www.gangbuk.go.kr/intro_gb.jsp',
        'city_name': '강북구',
        'cure_cnt_tag': '.itembox .text',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://www.dobong.go.kr/',
        'city_name': '도봉구',
        'cure_cnt_tag': '#base > div.corona_pop > div > div.pop_section02 > div.corona_box_wrap > div.corona_box.left_box > div > dl:nth-child(3) > dd',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'https://www.nowon.kr/corona19/index.do',
        'city_name': '노원구',
        'cure_cnt_tag': 'body > div.corona-info > div > div > div > div > table > tbody > tr > td:nth-child(2)',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'https://www.ep.go.kr/CmsWeb/viewPage.req?idx=PG0000004918',
        'city_name': '은평구',
        'cure_cnt_tag': '#content > div > div.sub_content > div > div > div:nth-child(3) > table > tbody > tr > td:nth-child(2)',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url' : 'http://www.sdm.go.kr/index.do',
        'city_name' : '서대문구',
        'cure_cnt_tag' : '#relativeDiv > div.corona-popup.is-visible > div > div.corona-popup-number > ul > li:nth-child(2)',
        'sub_cure_cnt_tag' : ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url' : 'http://www.mapo.go.kr/html/corona/intro.htm',
        'city_name' : '마포구',
        'cure_cnt_tag' : 'body > div > div > div.intro-status > div.is-cont.clearfix > div.isc-left > table > tbody > tr:nth-child(2) > td:nth-child(2)',
        'sub_cure_cnt_tag' : ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url' : 'http://www.yangcheon.go.kr/site/yangcheon/coronaStatusList.do',
        'city_name' : '양천구',
        'cure_cnt_tag' : '#content > div:nth-child(3) > div.redtable > table > tbody > tr:nth-child(2) > td:nth-child(2) > b',
        'sub_cure_cnt_tag' : ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url' : 'http://www.gangseo.seoul.kr/new_portal/living/safe/page06_07.jsp',
        'city_name' : '강서구',
        'cure_cnt_tag' : '.blue3',
        'sub_cure_cnt_tag' : ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url':'https://www.guro.go.kr/corona2.jsp',
        'city_name':'구로구',
        'cure_cnt_tag':'#content1 > div > div.outbreak_pink > div > span:nth-child(5)',
        'sub_cure_cnt_tag':''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url':'https://www.geumcheon.go.kr/portal/intro.do',
        'city_name':'금천구',
        'cure_cnt_tag':'#wrapper > div > div.bottom_box > div.text_area > div.table_text_left.clearfix > div > ul > li.pink_line.clearfix > div.box_col.box_w70 > span.text_table.clearfix > table > tbody > tr > td:nth-child(3)',
        'sub_cure_cnt_tag':''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url':'http://www.dongjak.go.kr/',
        'city_name':'동작구',
        'cure_cnt_tag':'.intr_tb tr:nth-child(3) td',
        'sub_cure_cnt_tag':''
    }
    cities_data_list.append(city_data_dict)


    city_data_dict = {
        'city_url':'https://www.ydp.go.kr/site/corona/index.jsp',
        'city_name':'영등포구',
        'cure_cnt_tag':'#iptDiss_cnt4',
        'sub_cure_cnt_tag':''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url':'https://www.seocho.go.kr/html/notice/main.jsp',
        'city_name':'서초구',
        'cure_cnt_tag':'#wrap > div.covidNew > div > div.countList > ul > li.item3 > span.count > b',
        'sub_cure_cnt_tag':''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url':'http://www.songpa.go.kr/index.jsp',
        'city_name':'송파구',
        'cure_cnt_tag':'#wraper > div.new-pop > div.np-thalf > div.npt-cont.clearfix > div.nc-left > div.status-table > table > tbody > tr > td:nth-child(3)',
        'sub_cure_cnt_tag':''
    }
    cities_data_list.append(city_data_dict)


    city_data_dict = {
        'city_url':'https://www.gangdong.go.kr/',
        'city_name':'강동구',
        'cure_cnt_tag':'#main-wrap > div.main-center > div.grey-box > ul > li.green > div.cont-right > p > strong',
        'sub_cure_cnt_tag':''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://www.gwanak.go.kr/site/gwanak/main.do',
        'city_name': '관악구',
        'cure_cnt_tag': '.corona_con td:nth-child(3)',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    #### 광진구 완치자 = 해외입국자 완치 + 국내감염 완치
    city_data_dict = {
        'city_url':'https://www.gwangjin.go.kr/portal/main/main.do#n',
        'city_name':'광진구',
        'cure_cnt_tag':'.table-sty2 td:nth-child(3)',
        'sub_cure_cnt_tag':'.table-sty2 td:nth-child(4)'
    }
    cities_data_list.append(city_data_dict)


    for city_data in cities_data_list:
        city_url = city_data['city_url']
        city_name = city_data['city_name']
        cure_cnt_tag = city_data['cure_cnt_tag'] # 완치자 누적
        sub_cure_cnt_tag = city_data['sub_cure_cnt_tag'] # 실험한거야
        get_cnt_cure(city_url, city_name, cure_cnt_tag, sub_cure_cnt_tag)

    ######################### 강남은 강남 JSON 따로 있으니 처리 빼야함 ####################
    city_url = 'http://www.gangnam.go.kr/etc/json/covid19.json'
    city_name = '강남구'
    res = requests.get(city_url)
    count_int = res.json()['status']['counter8']
    print('{}: {} '.format(city_name, count_int))

    return render(request, 'corona_map/cure_people.html')

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
        item_dict['incdec'] = item.find('incdec').string
        # 격리 해제 수
        item_dict['isolclearcnt'] = item.find('isolclearcnt').string
        # 10만명당 발생률
        item_dict['qurrate'] = item.find('qurrate').string
        # 사망자 수
        item_dict['deathcnt'] = item.find('deathcnt').string
        # 격리중 환자수
        item_dict['isolingcnt'] = item.find('isolingcnt').string
        # 해외유입 수
        item_dict['overflowcnt'] = item.find('overflowcnt').string
        # 지역발생 수
        item_dict['localocccnt'] = item.find('localocccnt').string
        item_list_result.append(item_dict)
    item_df = pd.DataFrame(columns=['gubun', 'gubunen', 'incdec', 'isolclearcnt', 'qurrate', 'deathcnt', 'isolingcnt', 'overflowcnt', 'localocccnt'])
    for a in item_list_result:
        a_object = pd.Series(a)
        item_df = item_df.append(a_object, ignore_index=True)
    return render(request, 'corona_map/coIs_home.html', {'soup_data': item_list_result})

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
    totalCount = item_df[item_df.columns[-1]].sum()
    barPlotData = item_df[['']]
    context = {'totalCount': totalCount}
    return render(request, 'corona_map/chart_bar.html', context)