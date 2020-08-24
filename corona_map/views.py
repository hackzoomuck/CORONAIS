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

def get_gugun_info(request):
    cure_people()
    return render(request, 'corona_map/gugun_info.html')

'''
 @ get_gugun_cnt  
 @ gugun_info_dict 
'''
def get_gugun_cnt(gugun_info_dict):
    def_cnt_int = None  # 확진자 수 (총 확진자)  DB : DEF_CNT
    isol_clear_cnt_int = None  # 격리 해제 수(총 완치자) DB : ISOL_CLEAR_CNT
    isol_ing_cnt_int = None  # 격리중 환자수(현재확진자수) DB : ISOL_ING_CNT
    death_cnt_int = None  # 사망자 DB : DEATH_CNT

    res_headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'),
        'Accept': (
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
        'Cookie': ('WMONID=DKSQRGw_Nxb;')
    }

    gugun_url = gugun_info_dict['gugun_url']    # 크롤링 대상 url
    gugun_name = gugun_info_dict['gugun_name']  # 구, 군 이름
    isol_clear_cnt_tag = gugun_info_dict['isol_clear_cnt_tag']  # 누적 완치자 tag
    sub_isol_clear_cnt_tag = gugun_info_dict['sub_isol_clear_cnt_tag']  # 누적 완치자 tag2
    def_cnt_tag = gugun_info_dict['def_cnt_tag']    # 누적 감염자 tag
    isol_ing_cnt_tag = gugun_info_dict['isol_ing_cnt_tag']  # 현재 확진자 tag

    res = requests.get(gugun_url, headers=res_headers)
    if 200 <= res.status_code < 400:
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')

        isol_clear_cnt_list = [None]    # 누적 완치자 크롤링 lsit
        def_cnt_list = [None]   # 누적 확진자 크롤링 list
        isol_ing_cnt_list = [None]  # 현재 확진자 크롤링 list

        if isol_clear_cnt_tag:
            # print('isol_clear_cnt_tag 읽기 시도')
            isol_clear_cnt_list = soup.select(isol_clear_cnt_tag)
        if def_cnt_tag:
            # print('def_cnt_tag 읽기 시도')
            def_cnt_list = soup.select(def_cnt_tag)
        if isol_ing_cnt_tag:
            # print('isol_clear_cnt_tag 읽기 시도')
            isol_ing_cnt_list = soup.select(isol_ing_cnt_tag)

        isol_clear_cnt = None  # 누적 완치자
        def_cnt = None  # 누적 감염자
        isol_ing_cnt = None  # 현재 확진자

        try:
            if gugun_name == '영등포구':
                if isol_clear_cnt_list[0] is not None:
                    isol_clear_cnt = isol_clear_cnt_list[0]['value']
                if isol_ing_cnt_list[0] is not None:
                    isol_ing_cnt = isol_ing_cnt_list[0]['value']

            elif gugun_name == '양천구':
                count_text = isol_clear_cnt_list[0].text
                matched = re.search(r'(\d+)명\((\d+)\명완치', count_text)
                def_cnt = matched.group(1)
                isol_clear_cnt = matched.group(2)

            elif gugun_name == '광진구':
                sub_isol_clear_cnt_tag_list = soup.select(sub_isol_clear_cnt_tag)

                isol_clear_cnt = str(int(isol_clear_cnt_list[0].text) + int(sub_isol_clear_cnt_tag_list[0].text))
                def_cnt = def_cnt_list[0].text

            else:
                if isol_clear_cnt_list[0] is not None:
                    isol_clear_cnt = isol_clear_cnt_list[0].text
                if def_cnt_list[0] is not None:
                    def_cnt = def_cnt_list[0].text
                if isol_ing_cnt_list[0] is not None:
                    isol_ing_cnt = isol_ing_cnt_list[0].text

            # 정보 구하기
            regex = re.compile(r'[^0-9]')

            # int 화
            if isol_clear_cnt is not None:
                isol_clear_cnt_int = int(regex.sub('', isol_clear_cnt).replace(r'[^0-9]', ''))
            if def_cnt is not None:
                def_cnt_int = int(regex.sub('', def_cnt).replace(r'[^0-9]', ''))
            if isol_ing_cnt is not None:
                isol_ing_cnt_int = int(regex.sub('', isol_ing_cnt).replace(r'[^0-9]', ''))

        except Exception as ex:
            print(gugun_name,'EXCEPTION ERROR : ',ex)

    # 못 받아온 값 확인
    if isol_clear_cnt_int is None:
        isol_ing_cnt_int = 99999999999 # 총 완치자는 모두 받아옴을 확인. 또는 사망자가 있을경우 알 수 없다.

    if def_cnt_int is None:
        if isol_clear_cnt_int is not None and isol_ing_cnt_int is not None:
            def_cnt_int = isol_clear_cnt_int + isol_ing_cnt_int
        else:
            def_cnt_int = 99999999999

    if isol_ing_cnt_int is None:
        if def_cnt_int is not None and isol_clear_cnt_int  is not None:
            isol_ing_cnt_int = def_cnt_int - isol_clear_cnt_int
        else:
            isol_ing_cnt_int = 99999999999

    death_cnt_int = def_cnt_int-isol_ing_cnt_int-isol_clear_cnt_int

    print('도시명: {}'.format(gugun_name))
    print('누적 확진자: {}'.format(def_cnt_int))
    print('현재 확진자: {}'.format(isol_ing_cnt_int))
    print('누적 완치자: {}'.format(isol_clear_cnt_int))
    print('사망자: {}'.format(death_cnt_int))


def cure_people():
    # http://ncov.mohw.go.kr/ 코로나 바이러스 감염증 중앙대책본부 통계 자료

    cities_data_list = []

    city_url = 'https://www.seoul.go.kr/coronaV/coronaStatus.do'
    city_name = '서울'
    # 0 종로구
    city_data_dict = {
        'gugun_url': 'https://www.jongno.go.kr/portalMain.do;jsessionid=WRbjo7mxihEc2FtUXnZ8KUhCfSD3fYAhm2iyQ17E3HY1FDdtV6TOPaw70mYWKyKW.was_servlet_engine1',
        'gugun_name': '종로구',
        'isol_clear_cnt_tag': '#corona19_info > div > div.popup-body > div.coronal-table > table > tbody > tr > td:nth-child(2)', # 누적 완치자
        'sub_isol_clear_cnt_tag': '', # 누적 완치자 2 서브로 필요한 경우
        'def_cnt_tag':'#corona19_info > div > div.popup-body > div.coronal-table > table > tbody > tr > td:nth-child(1)', # 누적 확진자
        'isol_ing_cnt_tag':'#corona19_info > div > div.popup-body > div.coronal-table > table > tbody > tr > td:nth-child(4)' # 현재 확진자

    }
    cities_data_list.append(city_data_dict)
    
    # 1 중구
    city_data_dict = {
        'gugun_url': 'http://www.junggu.seoul.kr/index.jsp#',
        'gugun_name': '중구',
        'isol_clear_cnt_tag': '#wrap > div.popup_container > div.virus_popup01 > div.popup_body > div > div.col_right.clearfix > div.r_inner_left > div > div > table > tbody > tr > td:nth-child(2)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag':'#wrap > div.popup_container > div.virus_popup01 > div.popup_body > div > div.col_right.clearfix > div.r_inner_left > div > div > table > thead > tr:nth-child(1) > th:nth-child(1)',
        'isol_ing_cnt_tag':'#wrap > div.popup_container > div.virus_popup01 > div.popup_body > div > div.col_right.clearfix > div.r_inner_left > div > div > table > tbody > tr > td:nth-child(1)'
    }
    cities_data_list.append(city_data_dict)
    
    # 2 용산구
    city_data_dict = {
        'gugun_url': 'http://www.yongsan.go.kr/index.htm',
        'gugun_name': '용산구',
        'isol_clear_cnt_tag': '#wrap > div.layer-popup > div > div.popup-contents.virus > div > div:nth-child(1) > div > table > tbody > tr > td:nth-child(2)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': '#wrap > div.layer-popup > div > div.popup-contents.virus > div > div:nth-child(1) > div > table > tbody > tr > td:nth-child(1)'
    }
    cities_data_list.append(city_data_dict)

    # 3 동대문구
    city_data_dict = {
        'gugun_url': 'http://www.ddm.go.kr/',
        'gugun_name': '동대문구',
        'isol_clear_cnt_tag': '#contents > div.inner > section:nth-child(1) > div > table > tbody > tr > td:nth-child(3) > strong',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '#contents > div.inner > section:nth-child(1) > div > table > tbody > tr > td:nth-child(1)',
        'isol_ing_cnt_tag': '#contents > div.inner > section:nth-child(1) > div > table > tbody > tr > td:nth-child(2)'
    }
    cities_data_list.append(city_data_dict)

    # 4 중랑구
    city_data_dict = {
        'gugun_url': 'http://c19.jungnang.go.kr/',
        'gugun_name': '중랑구',
        'isol_clear_cnt_tag': '#jn_intro_wrap > div > div.intro_tbl_box > dl.intro_tbl.jn_intro_tbl > dd:nth-child(3) > span',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '#jn_intro_wrap > div.intro_containter > div.intro_tbl_box > dl.intro_tbl.jn_intro_tbl > dd:nth-child(2) > span',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    # 5 성동구
    city_data_dict = {
        'gugun_url': 'http://www.sd.go.kr/sd/intro.do',
        'gugun_name': '성동구',
        'isol_clear_cnt_tag': '#content > div.top_box > div > div.top_area1 > ul > li.alone > span:nth-child(3) > em',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '#content > div.top_box > div > div.top_area1 > ul > li.alone > span.stat_title',
        'isol_ing_cnt_tag': '#content > div.top_box > div > div.top_area1 > ul > li.alone > span.stat_txt.first_txt > em'
    }
    cities_data_list.append(city_data_dict)
    
    # 6 성북구
    city_data_dict = {
        'gugun_url': 'http://www.sb.go.kr/',
        'gugun_name': '성북구',
        'isol_clear_cnt_tag': '#main_popup > div.wrap-div1 > div.box2-n.clearfix > div.con2.style2 > div > div.box1.clearfix > div.box-c.c1 > p > span.num',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '#main_popup > div.wrap-div1 > div.box2-n.clearfix > div.con2.style2 > div > div.box1.clearfix > div.box-c.c1 > p > span.num',
        'isol_ing_cnt_tag': '#main_popup > div.wrap-div1 > div.box2-n.clearfix > div.con2.style2 > div > div.box1.clearfix > div.box-c.c2 > p > span.num'
    }
    cities_data_list.append(city_data_dict)

    # 7 강북구
    city_data_dict = {
        'gugun_url': 'http://www.gangbuk.go.kr/intro_gb.jsp',
        'gugun_name': '강북구',
        'isol_clear_cnt_tag': '#corona_container > main > div.section.state > div.sectionbox > div > div > div.rowbox.rowbox2.clearfix > div.conbox.clearfix > ul > li.item.item04 > div > p',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '#corona_container > main > div.section.state > div.sectionbox > div > div > div.rowbox.rowbox2.clearfix > div.conbox.clearfix > ul > li.item.item01 > div > p',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 8 도봉구
    city_data_dict = {
        'gugun_url': 'http://www.dobong.go.kr/',
        'gugun_name': '도봉구',
        'isol_clear_cnt_tag': '#base > div.new_curtain > div > ul > li.box01 > div > div > div.corona_box.left_box > div > dl:nth-child(3) > dd',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '#base > div.new_curtain > div > ul > li.box01 > div > div > div.corona_box.left_box > div > dl:nth-child(1) > dd',
        'isol_ing_cnt_tag': '#base > div.new_curtain > div > ul > li.box01 > div > div > div.corona_box.left_box > div > dl:nth-child(2) > dd'
    }
    cities_data_list.append(city_data_dict)
    
    # 9 노원구
    city_data_dict = {
        'gugun_url': 'https://www.nowon.kr/corona19/index.do',
        'gugun_name': '노원구',
        'isol_clear_cnt_tag': 'body > div.corona-info > div > div > div > div > table > tbody > tr > td:nth-child(2)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 10 은평구
    city_data_dict = {
        'gugun_url': 'https://www.ep.go.kr/CmsWeb/viewPage.req?idx=PG0000004918',
        'gugun_name': '은평구',
        'isol_clear_cnt_tag': '#content > div > div.sub_content > div > div > div:nth-child(3) > table > tbody > tr > td:nth-child(2)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 11 은평구
    city_data_dict = {
        'gugun_url': 'http://www.sdm.go.kr/index.do',
        'gugun_name': '서대문구',
        'isol_clear_cnt_tag': '#relativeDiv > div.corona-popup.is-visible > div > div.corona-popup-number > ul > li:nth-child(2)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 12 마포구
    city_data_dict = {
        'gugun_url': 'http://www.mapo.go.kr/html/corona/intro.htm',
        'gugun_name': '마포구',
        'isol_clear_cnt_tag': 'body > div > div > div.intro-status > div.is-cont.clearfix > div.isc-left > table > tbody > tr:nth-child(2) > td:nth-child(2)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 13 양천구
    city_data_dict = {
        'gugun_url': 'http://www.yangcheon.go.kr/site/yangcheon/coronaStatusList.do',
        'gugun_name': '양천구',
        'isol_clear_cnt_tag': '#content > div:nth-child(3) > div.redtable > table > tbody > tr:nth-child(2) > td:nth-child(2) > b',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 14 강서구
    city_data_dict = {
        'gugun_url': 'http://www.gangseo.seoul.kr/new_portal/living/safe/page06_07.jsp',
        'gugun_name': '강서구',
        'isol_clear_cnt_tag': '.blue3',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 15 구로구
    city_data_dict = {
        'gugun_url': 'https://www.guro.go.kr/corona2.jsp',
        'gugun_name': '구로구',
        'isol_clear_cnt_tag': '#content1 > div > div.outbreak_pink > div > span:nth-child(5)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 16 금천구
    city_data_dict = {
        'gugun_url': 'https://www.geumcheon.go.kr/portal/intro.do',
        'gugun_name': '금천구',
        'isol_clear_cnt_tag': '#wrapper > div > div.bottom_box > div.text_area > div.table_text_left.clearfix > div > ul > li.pink_line.clearfix > div.box_col.box_w70 > span.text_table.clearfix > table > tbody > tr > td:nth-child(3)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 17 동작구
    city_data_dict = {
        'gugun_url': 'http://www.dongjak.go.kr/',
        'gugun_name': '동작구',
        'isol_clear_cnt_tag': '.intr_tb tr:nth-child(3) td',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 18 영등포구
    city_data_dict = {
        'gugun_url': 'https://www.ydp.go.kr/site/corona/index.jsp',
        'gugun_name': '영등포구',
        'isol_clear_cnt_tag': '#iptDiss_cnt4',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': '#iptDiss_cnt1'
    }
    cities_data_list.append(city_data_dict)
    
    # 19 서초구
    city_data_dict = {
        'gugun_url': 'https://www.seocho.go.kr/html/notice/main.jsp',
        'gugun_name': '서초구',
        'isol_clear_cnt_tag': '#wrap > div.covidNew > div > div.countList > ul > li.item3 > span.count > b',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 20 송파구
    city_data_dict = {
        'gugun_url': 'http://www.songpa.go.kr/index.jsp',
        'gugun_name': '송파구',
        'isol_clear_cnt_tag': '#wraper > div.new-pop > div.np-thalf > div.npt-cont.clearfix > div.nc-left > div.status-table > table > tbody > tr > td:nth-child(3)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 21 강동구
    city_data_dict = {
        'gugun_url': 'https://www.gangdong.go.kr/',
        'gugun_name': '강동구',
        'isol_clear_cnt_tag': '#main-wrap > div.main-center > div.grey-box > ul > li.green > div.cont-right > p > strong',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 22 관악구
    city_data_dict = {
        'gugun_url': 'http://www.gwanak.go.kr/site/gwanak/main.do',
        'gugun_name': '관악구',
        'isol_clear_cnt_tag': '.corona_con td:nth-child(3)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)
    
    # 23 광진구
    city_data_dict = {
        'gugun_url': 'https://www.gwangjin.go.kr/portal/main/main.do#n',
        'gugun_name': '광진구',
        'isol_clear_cnt_tag': '.table-sty2 td:nth-child(3)',
        'sub_isol_clear_cnt_tag': '.table-sty2 td:nth-child(4)',
        'def_cnt_tag': '.table-sty2 th:nth-child(1)',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    for city_data_dict in cities_data_list:
        get_gugun_cnt(city_data_dict)

    # get_gugun_cnt(cities_data_list[8])

    ######################### 강남은 강남 JSON 따로 있으니 처리 빼야함 ####################
    gugun_url = 'http://www.gangnam.go.kr/etc/json/covid19.json'
    gugun_name = '강남구'
    res = requests.get(gugun_url)
    def_cnt_int = res.json()['status']['counter8']

    print('도시명: {}'.format(gugun_name))
    print('누적 확진자: {}'.format(def_cnt_int))
    print('현재 확진자: {}'.format(99999999999))
    print('누적 완치자: {}'.format(99999999999))
    print('사망자: {}'.format(99999999999))


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
                       '67xjSd3vhpWMN4oQ3DztMgLyq4Aa1ugw1ssq%2FHeJAeniNIwyPspLp7XpNoa8mBbTJQPc3dAxqvtFm57fJIfq8w%3D%3D',
                       '2']
    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson'
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
    return render(request, 'corona_map/by_age_gender.html', context)

