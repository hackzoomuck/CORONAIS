from django.shortcuts import render
from urllib.parse import unquote
from bs4 import BeautifulSoup
import pandas as pd
import folium
import json
import requests
import corona_map.MongoDbManager as comong
from corona_map.Api.Infection_city import infection_city
from corona_map.Api.Infection_by_age_gender import infection_by_age_gender
from corona_map.Api.Infection_status import infection_status

import pymongo
# 현재날짜를 사용하기 위한 모듈
import datetime
import re

'''
 @ sigu_url 크롤링 주소
 @ sigu_name = 도시 이름
 @ cure_cnt_tag = 완치자 태그
 @ sub_cure_cnt_tag = 완치자 계산을 위한 서브 태그
'''


def get_cnt_cure(sigu_url, sigu_name, cure_cnt_tag, sub_cure_cnt_tag):
    res_headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'),
        'Accept': (
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
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
            count_int = regex.sub('', count_int).replace(r'[^0-9]', '')
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
        'city_url': 'https://www.jongno.go.kr/portalMain.do;jsessionid=WRbjo7mxihEc2FtUXnZ8KUhCfSD3fYAhm2iyQ17E3HY1FDdtV6TOPaw70mYWKyKW.was_servlet_engine1',
        'city_name': '종로구',
        'cure_cnt_tag': '#corona19_info > div > div.popup-body > div.coronal-table > table > tbody > tr > td:nth-child(2)',
        'sub_cure_cnt_tag': ''
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
        'city_url': 'http://www.sdm.go.kr/index.do',
        'city_name': '서대문구',
        'cure_cnt_tag': '#relativeDiv > div.corona-popup.is-visible > div > div.corona-popup-number > ul > li:nth-child(2)',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://www.mapo.go.kr/html/corona/intro.htm',
        'city_name': '마포구',
        'cure_cnt_tag': 'body > div > div > div.intro-status > div.is-cont.clearfix > div.isc-left > table > tbody > tr:nth-child(2) > td:nth-child(2)',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://www.yangcheon.go.kr/site/yangcheon/coronaStatusList.do',
        'city_name': '양천구',
        'cure_cnt_tag': '#content > div:nth-child(3) > div.redtable > table > tbody > tr:nth-child(2) > td:nth-child(2) > b',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://www.gangseo.seoul.kr/new_portal/living/safe/page06_07.jsp',
        'city_name': '강서구',
        'cure_cnt_tag': '.blue3',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'https://www.guro.go.kr/corona2.jsp',
        'city_name': '구로구',
        'cure_cnt_tag': '#content1 > div > div.outbreak_pink > div > span:nth-child(5)',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'https://www.geumcheon.go.kr/portal/intro.do',
        'city_name': '금천구',
        'cure_cnt_tag': '#wrapper > div > div.bottom_box > div.text_area > div.table_text_left.clearfix > div > ul > li.pink_line.clearfix > div.box_col.box_w70 > span.text_table.clearfix > table > tbody > tr > td:nth-child(3)',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://www.dongjak.go.kr/',
        'city_name': '동작구',
        'cure_cnt_tag': '.intr_tb tr:nth-child(3) td',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'https://www.ydp.go.kr/site/corona/index.jsp',
        'city_name': '영등포구',
        'cure_cnt_tag': '#iptDiss_cnt4',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'https://www.seocho.go.kr/html/notice/main.jsp',
        'city_name': '서초구',
        'cure_cnt_tag': '#wrap > div.covidNew > div > div.countList > ul > li.item3 > span.count > b',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'http://www.songpa.go.kr/index.jsp',
        'city_name': '송파구',
        'cure_cnt_tag': '#wraper > div.new-pop > div.np-thalf > div.npt-cont.clearfix > div.nc-left > div.status-table > table > tbody > tr > td:nth-child(3)',
        'sub_cure_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    city_data_dict = {
        'city_url': 'https://www.gangdong.go.kr/',
        'city_name': '강동구',
        'cure_cnt_tag': '#main-wrap > div.main-center > div.grey-box > ul > li.green > div.cont-right > p > strong',
        'sub_cure_cnt_tag': ''
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
        'city_url': 'https://www.gwangjin.go.kr/portal/main/main.do#n',
        'city_name': '광진구',
        'cure_cnt_tag': '.table-sty2 td:nth-child(3)',
        'sub_cure_cnt_tag': '.table-sty2 td:nth-child(4)'
    }
    cities_data_list.append(city_data_dict)

    for city_data in cities_data_list:
        city_url = city_data['city_url']
        city_name = city_data['city_name']
        cure_cnt_tag = city_data['cure_cnt_tag']  # 완치자 누적
        sub_cure_cnt_tag = city_data['sub_cure_cnt_tag']  # 실험한거야
        get_cnt_cure(city_url, city_name, cure_cnt_tag, sub_cure_cnt_tag)

    ######################### 강남은 강남 JSON 따로 있으니 처리 빼야함 ####################
    city_url = 'http://www.gangnam.go.kr/etc/json/covid19.json'
    city_name = '강남구'
    res = requests.get(city_url)
    count_int = res.json()['status']['counter8']
    print('{}: {} '.format(city_name, count_int))

    return render(request, 'corona_map/cure_people.html')

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
    print(infection_city())
    print(infection_by_age_gender())
    #print(infection_status())

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
                       {'시':'서울','위도':37.56,'경도':126.97,'링크':'<h4>{}</h4><a href="https://www.incheon.go.kr/health/HE020409" target="_blank">{}</a>'}]


    for si_ma in sido_lati_longi:
        sido_html = '<h4>{}</h4><h4>총 확진자 {}</h4><a href='.format(si_ma['시'], soup_sido_data_list[si_ma['시']])+si_ma['링크']+'target="_blank">{}</a>'.format(si_ma['시'])
        folium.Marker([si_ma['위도'], si_ma['경도']],
            popup=folium.map.Popup(sido_html, parse_html=False, max_width=200), #.decode('cp949').encode('utf-8')
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

