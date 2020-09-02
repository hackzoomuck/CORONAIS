from bs4 import BeautifulSoup
import requests
import re
import datetime

import corona_map.MongoDbManager as DBmanager

def crawling_seoul_gu_state_dict(gugun_info_dict) -> dict:
    '''
     get_seoul_gu_state_dict 실제로 크롤링이 작동하는 함수
     gugun_info_dict 크롤링을 위한 데이터 파라미터
    '''

    def_cnt_int = None  # 확진자 수 (총 확진자)  DB : DEF_CNT
    isol_clear_cnt_int = None  # 격리 해제 수(총 완치자) DB : ISOL_CLEAR_CNT
    isol_ing_cnt_int = None  # 격리중 환자수(현재확진자수) DB : ISOL_ING_CNT
    death_cnt_int = None  # 사망자 DB : DEATH_CNT

    isol_clear_cnt_list = None  # 누적 완치자 크롤링 lsit
    def_cnt_list = None  # 누적 확진자 크롤링 list
    isol_ing_cnt_list = None  # 현재 확진자 크롤링 list

    isol_clear_cnt = None  # 누적 완치자
    def_cnt = None  # 누적 감염자
    isol_ing_cnt = None  # 현재 확진자

    res_headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'),
        'Accept': (
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
        'Cookie': ('WMONID=DKSQRGw_Nxb;')
    }

    gugun_url = gugun_info_dict['gugun_url']  # 크롤링 대상 url
    gugun_name = gugun_info_dict['gugun_name']  # 구, 군 이름
    isol_clear_cnt_tag = gugun_info_dict['isol_clear_cnt_tag']  # 누적 완치자 tag
    sub_isol_clear_cnt_tag = gugun_info_dict['sub_isol_clear_cnt_tag']  # 누적 완치자 tag2
    def_cnt_tag = gugun_info_dict['def_cnt_tag']  # 누적 감염자 tag
    isol_ing_cnt_tag = gugun_info_dict['isol_ing_cnt_tag']  # 현재 확진자 tag

    res = requests.get(gugun_url, headers=res_headers, verify=False)

    if 200 <= res.status_code < 400:
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')

        if isol_clear_cnt_tag:
            # print('isol_clear_cnt_tag 읽기 시도')
            isol_clear_cnt_list = soup.select(isol_clear_cnt_tag)
            # print(isol_clear_cnt_list)
        if def_cnt_tag:
            # print('def_cnt_tag 읽기 시도')
            def_cnt_list = soup.select(def_cnt_tag)
            # print(def_cnt_list)
        if isol_ing_cnt_tag:
            # print('isol_ing_cnt_tag 읽기 시도')
            isol_ing_cnt_list = soup.select(isol_ing_cnt_tag)
            # print(isol_ing_cnt_list)

        try:
            if gugun_name == '영등포구':
                if isol_clear_cnt_list is not None:
                    isol_clear_cnt = isol_clear_cnt_list[0]['value']
                if isol_ing_cnt_list is not None:
                    isol_ing_cnt = isol_ing_cnt_list[0]['value']

            elif gugun_name == '양천구':
                count_text = isol_clear_cnt_list[0].text
                matched = re.search(r'(\d+)명\((\d+)\명완치', count_text)
                def_cnt = matched.group(1)
                isol_clear_cnt = matched.group(2)

            elif gugun_name == '강서구':
                isol_ing_cnt_list = isol_clear_cnt_list[0].select('td:nth-last-child(3)')
                death_cnt_list = isol_clear_cnt_list[0].select('td:nth-last-child(1)')
                isol_clear_cnt_list = isol_clear_cnt_list[0].select('td:nth-last-child(2)')

                isol_ing_cnt = str(isol_ing_cnt_list[0].text)
                isol_clear_cnt = str(isol_clear_cnt_list[0].text)
                death_cnt_int = int(death_cnt_list[0].text)

            elif gugun_name == '광진구':
                sub_isol_clear_cnt_tag_list = soup.select(sub_isol_clear_cnt_tag)

                isol_clear_cnt = str(int(isol_clear_cnt_list[0].text) + int(sub_isol_clear_cnt_tag_list[0].text))
                def_cnt = def_cnt_list[0].text

            elif gugun_name == '중랑구':
                count_text = isol_clear_cnt_list[0].text
                matched = re.search(r'(\d+)(\s)\((\d+)\)', count_text)
                def_cnt = matched.group(1)
                isol_clear_cnt = matched.group(3)

            else:
                if isol_clear_cnt_list is not None:
                    isol_clear_cnt = isol_clear_cnt_list[0].text
                if def_cnt_list is not None:
                    def_cnt = def_cnt_list[0].text
                if isol_ing_cnt_list is not None:
                    isol_ing_cnt = isol_ing_cnt_list[0].text

            # 정보 구하기
            regex = re.compile(r'[^0-9]')

            # int 화
            # print('정규표현식 작동')
            if isol_clear_cnt is not None:
                isol_clear_cnt_int = int(regex.sub('', isol_clear_cnt).replace(r'[^0-9]', ''))
            if def_cnt is not None:
                def_cnt_int = int(regex.sub('', def_cnt).replace(r'[^0-9]', ''))
            if isol_ing_cnt is not None:
                isol_ing_cnt_int = int(regex.sub('', isol_ing_cnt).replace(r'[^0-9]', ''))

        except Exception as ex:
            print(gugun_name, 'EXCEPTION ERROR : ', ex)

    # 못 받아온 값 확인
    if isol_clear_cnt_int is None:
        if death_cnt_int is not None and def_cnt_int is not None and isol_ing_cnt_int is not None:
            isol_clear_cnt_int = def_cnt_int - death_cnt_int - isol_ing_cnt_int
        else:
            if isol_ing_cnt_int is not None and def_cnt_int is not None:
                isol_clear_cnt_int = def_cnt_int - isol_ing_cnt_int
            else:
                isol_ing_cnt_int = -1

    if def_cnt_int is None:
        if isol_clear_cnt_int is not None and isol_ing_cnt_int is not None and death_cnt_int is not None:
            def_cnt_int = isol_clear_cnt_int + isol_ing_cnt_int + death_cnt_int
        else:
            if isol_clear_cnt_int is not None and isol_ing_cnt_int is not None:
                def_cnt_int = isol_clear_cnt_int + isol_ing_cnt_int
            else:
                def_cnt_int = -1

    if isol_ing_cnt_int is None:
        if def_cnt_int is not None and isol_clear_cnt_int is not None and death_cnt_int is not None:
            isol_ing_cnt_int = def_cnt_int - isol_clear_cnt_int - death_cnt_int
        else:
            if def_cnt_int is not None and isol_clear_cnt_int is not None:
                isol_ing_cnt_int = def_cnt_int - isol_clear_cnt_int
            else:
                isol_ing_cnt_int = -1

    if death_cnt_int is None:
        if def_cnt_int is not None and isol_clear_cnt_int is not None:
            death_cnt_int = def_cnt_int - isol_ing_cnt_int - isol_clear_cnt_int
        else:
            death_cnt_int = -1

    # 종합 데이터 dict 리턴
    gugun_data_dict = {
        'gubunsmall': gugun_name,
        'defcnt': def_cnt_int,
        'isolingcnt':isol_ing_cnt_int,
        'isolclearcnt':isol_clear_cnt_int,
        'deathcnt':death_cnt_int
    }
    return gugun_data_dict

def get_seoul_info_dict() -> dict:
    # http://ncov.mohw.go.kr/ 코로나 바이러스 감염증 중앙대책본부 통계 자료

    seoul_gu_info_list = [] # 리턴되는 구,군 데이터 리스트
    cities_data_list = [] # 크롤링 대상 데이터 리스트

    city_url = 'https://www.seoul.go.kr/coronaV/coronaStatus.do'
    city_name = '서울'
    # 0 종로구
    city_data_dict = {
        'gugun_url': 'https://www.jongno.go.kr/portalMain.do;jsessionid=WRbjo7mxihEc2FtUXnZ8KUhCfSD3fYAhm2iyQ17E3HY1FDdtV6TOPaw70mYWKyKW.was_servlet_engine1',
        'gugun_name': '종로구',
        'isol_clear_cnt_tag': '#corona19_info > div > div.popup-body > div.coronal-table > table > tbody > tr > td:nth-child(2)',
        # 누적 완치자
        'sub_isol_clear_cnt_tag': '',  # 누적 완치자 2 서브로 필요한 경우
        'def_cnt_tag': '#corona19_info > div > div.popup-body > div.coronal-table > table > tbody > tr > td:nth-child(1)',
        # 누적 확진자
        'isol_ing_cnt_tag': '#corona19_info > div > div.popup-body > div.coronal-table > table > tbody > tr > td:nth-child(4)'
        # 현재 확진자

    }
    cities_data_list.append(city_data_dict)

    # 1 중구
    city_data_dict = {
        'gugun_url': 'http://www.junggu.seoul.kr/index.jsp#',
        'gugun_name': '중구',
        'isol_clear_cnt_tag': '#wrap > div.popup_container > div.virus_popup01 > div.popup_body > div > div.col_right.clearfix > div.r_inner_left > div > div > table > tbody > tr > td:nth-child(2)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '#wrap > div.popup_container > div.virus_popup01 > div.popup_body > div > div.col_right.clearfix > div.r_inner_left > div > div > table > thead > tr:nth-child(1) > th:nth-child(1)',
        'isol_ing_cnt_tag': '#wrap > div.popup_container > div.virus_popup01 > div.popup_body > div > div.col_right.clearfix > div.r_inner_left > div > div > table > tbody > tr > td:nth-child(1)'
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
        'isol_clear_cnt_tag': '#jn_bulletin_wrap > div.jb_md_box > div > ul > li:nth-child(1) > b',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    # 5 성동구
    city_data_dict = {
        'gugun_url': 'http://www.sd.go.kr/sd/intro.do',
        'gugun_name': '성동구',
        'isol_clear_cnt_tag': '.top_box .top_area1 .status_list .stat_txt:nth-last-child(2) em',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '.top_box .top_area1 .status_list .alone .stat_title',
        'isol_ing_cnt_tag': '.top_box .top_area1 .status_list .stat_txt.first_txt em'
    }
    cities_data_list.append(city_data_dict)

    # 6 성북구
    city_data_dict = {
        'gugun_url': 'http://www.sb.go.kr/',
        'gugun_name': '성북구',
        'isol_clear_cnt_tag': '#main_popup > div.wrap-div1 > div.box2-n.clearfix > div.con2.style2 > div > div.box1.clearfix > div.box-c.c3 > p > span.num',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '#main_popup > div.wrap-div1 > div.box2-n.clearfix > div.con2.style2 > div > div.box1.clearfix > div.box-c.c1 > p > span.num',
        'isol_ing_cnt_tag': '#main_popup > div.wrap-div1 > div.box2-n.clearfix > div.con2.style2 > div > div.box1.clearfix > div.box-c.c2 > p > span.num:nth-last-child(1)'
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
        'isol_clear_cnt_tag': '.new_curtain .curtain_inner .mt20 .box01 .mt10 .corona_box.left_box .count_list.list_add.left dl:nth-child(3) dd',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '.new_curtain .curtain_inner .mt20 .box01 .mt10 .corona_box.left_box .count_list.list_add.left dl:nth-child(1) dd',
        'isol_ing_cnt_tag': '.new_curtain .curtain_inner .mt20 .box01 .mt10 .corona_box.left_box .count_list.list_add.left dl:nth-child(2) dd'
    }
    cities_data_list.append(city_data_dict)

    # 9 노원구
    city_data_dict = {
        'gugun_url': 'https://www.nowon.kr/corona19/index.do',
        'gugun_name': '노원구',
        'isol_clear_cnt_tag': 'body > div.corona-info > div > div > div > div > table > tbody > tr > td:nth-child(2)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': 'body > div.corona-info > div > div > div > div > table > tbody > tr > td.text-primary.text-medium > span',
        'isol_ing_cnt_tag': 'body > div.corona-info > div > div > div > div > table > tbody > tr > td:nth-child(3)'
    }
    cities_data_list.append(city_data_dict)

    # 10 은평구
    city_data_dict = {
        'gugun_url': 'https://www.ep.go.kr/CmsWeb/viewPage.req?idx=PG0000004918',
        'gugun_name': '은평구',
        'isol_clear_cnt_tag': '#content > div > div.sub_content > div > div > div:nth-child(3) > table > tbody > tr > td:nth-child(2)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '#content > div > div.sub_content > div > div > div:nth-child(3) > table > tbody > tr > td.botn',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    # 11 서대문구
    # 서대문구 사망자가 치료중에 들어있음
    city_data_dict = {
        'gugun_url': 'http://www.sdm.go.kr/index.do',
        'gugun_name': '서대문구',
        'isol_clear_cnt_tag': '#relativeDiv > div.corona-popup.is-visible > div > div.corona-popup-number > ul > li:nth-child(2) > span',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '#relativeDiv > div.corona-popup.is-visible > div > div.corona-popup-number > ul > li:nth-child(1) > span',
        'isol_ing_cnt_tag': '#relativeDiv > div.corona-popup.is-visible > div > div.corona-popup-number > ul > li:nth-child(3) > span'
    }
    cities_data_list.append(city_data_dict)

    # 12 마포구
    city_data_dict = {
        'gugun_url': 'http://www.mapo.go.kr/html/corona/intro.htm',
        'gugun_name': '마포구',
        'isol_clear_cnt_tag': 'body > div > div > div.intro-status > div.is-cont.clearfix > div.isc-left > table > tbody > tr:nth-child(2) > td:nth-child(2)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': 'body > div > div > div.intro-status > div.is-cont.clearfix > div.isc-left > table > thead > tr > th:nth-child(1)',
        'isol_ing_cnt_tag': 'body > div > div > div.intro-status > div.is-cont.clearfix > div.isc-left > table > tbody > tr:nth-child(2) > td:nth-child(1)'
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
        'isol_clear_cnt_tag': '.newcon-wrap > .newcon-list > .con2 > table',
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
        'def_cnt_tag': '#counter1',
        'isol_ing_cnt_tag': '#content1 > div > div.outbreak_pink > div > span:nth-child(3)'
    }
    cities_data_list.append(city_data_dict)

    # 16 금천구
    city_data_dict = {
        'gugun_url': 'https://www.geumcheon.go.kr/portal/intro.do',
        'gugun_name': '금천구',
        'isol_clear_cnt_tag': '#wrapper > div > div.bottom_box > div.text_area > div.table_text_left.clearfix > div > ul > li.pink_line.clearfix > div.box_col.box_w70 > span.text_table.clearfix > table > tbody > tr > td:nth-child(3)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '#wrapper > div > div.bottom_box > div.text_area > div.table_text_left.clearfix > div > ul > li.pink_line.clearfix > div.box_col.box_w70 > span.text_table.clearfix > table > tbody > tr > td:nth-child(1)',
        'isol_ing_cnt_tag': '#wrapper > div > div.bottom_box > div.text_area > div.table_text_left.clearfix > div > ul > li.pink_line.clearfix > div.box_col.box_w70 > span.text_table.clearfix > table > tbody > tr > td:nth-child(2)'
    }
    cities_data_list.append(city_data_dict)

    # 17 동작구
    city_data_dict = {
        'gugun_url': 'http://www.dongjak.go.kr/',
        'gugun_name': '동작구',
        'isol_clear_cnt_tag': '.intr_tb tr:nth-child(3) td',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '',
        'isol_ing_cnt_tag': '.intr_tb tr:nth-child(1) td'
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
        'isol_ing_cnt_tag': '#wrap > div.covidNew > div > div.countList > ul > li.item1 > span.count > b'
    }
    cities_data_list.append(city_data_dict)

    # 20 송파구
    city_data_dict = {
        'gugun_url': 'http://www.songpa.go.kr/index.jsp',
        'gugun_name': '송파구',
        'isol_clear_cnt_tag': '#wraper > div.new-pop > div.np-thalf > div.npt-cont.clearfix > div.nc-left > div.status-table > table > tbody > tr > td:nth-child(3)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '#wraper > div.new-pop > div.np-thalf > div.npt-cont.clearfix > div.nc-left > div.status-table > table > tbody > tr > td:nth-child(1)',
        'isol_ing_cnt_tag': '#wraper > div.new-pop > div.np-thalf > div.npt-cont.clearfix > div.nc-left > div.status-table > table > tbody > tr > td.red-b'
    }
    cities_data_list.append(city_data_dict)

    # 21 강동구
    city_data_dict = {
        'gugun_url': 'https://www.gangdong.go.kr/',
        'gugun_name': '강동구',
        'isol_clear_cnt_tag': '#main-wrap > div.main-center > div.grey-box > ul > li.green > div.cont-right > p > strong',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '#main-wrap > div.main-center > div.grey-box > ul > li.red > div.cont-right > p > strong',
        'isol_ing_cnt_tag': ''
    }
    cities_data_list.append(city_data_dict)

    # 22 관악구
    city_data_dict = {
        'gugun_url': 'http://www.gwanak.go.kr/site/gwanak/main.do',
        'gugun_name': '관악구',
        'isol_clear_cnt_tag': '.f td:nth-last-child(1)',
        'sub_isol_clear_cnt_tag': '',
        'def_cnt_tag': '.f td:nth-last-child(3)',
        'isol_ing_cnt_tag': '.f td:nth-last-child(2)'
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
        seoul_gu_info_list.append(crawling_seoul_gu_state_dict(city_data_dict))

    gugun_url = 'http://www.gangnam.go.kr/etc/json/covid19.json'
    gugun_name = '강남구'
    res = requests.get(gugun_url)
    def_cnt_int = int(res.json()['status']['counter8'])

    gangnam_data_from_json_dict = {
        'gubunsmall': gugun_name,
        'defcnt': def_cnt_int,
        'isolingcnt': -1,
        'isolclearcnt': -1,
        'deathcnt': -1
    }

    seoul_gu_info_list.append(gangnam_data_from_json_dict)

    seoul_data_dict = {
        'seoul': seoul_gu_info_list,
        'stdday': int(datetime.datetime.now().strftime('%Y%m%d'))
    }

    return seoul_data_dict


def init_gugun_data() -> bool:
    data_items_dict = get_seoul_info_dict()
    DBmanager.Infection_Smallcity().add_gugun_status_datas_on_collection(data_items_dict)
    return True

def get_seoul_data_list() -> list:
    now_date = int(datetime.datetime.now().strftime('%Y%m%d'))
    sql_query_0 = {'stdday':now_date}
    sql_query_1 = {'_id': 0}

    cursor_obj = DBmanager.Infection_Smallcity().get_gugun_status_datas_from_collection(sql_query_0, sql_query_1)
    cursor_objs_list = list(cursor_obj)
    print(cursor_objs_list)
    seoul_gus_data_list = list()

    for obj_dict in cursor_objs_list:
        if obj_dict.get('seoul'):
            seoul_gus_data_list = obj_dict['seoul']
            break

    return seoul_gus_data_list

def get_seoul_yesterday_data_list() -> list:
    timestamp = datetime.datetime.now() - datetime.timedelta(days=1)
    find_date = int(timestamp.strftime('%Y%m%d'))
    sql_query_0 = {'stdday': find_date}
    sql_query_1 = {'_id': 0}

    cursor_obj = DBmanager.Infection_Smallcity().get_gugun_status_datas_from_collection(sql_query_0, sql_query_1)

    cursor_objs_list = list(cursor_obj)
    print(cursor_objs_list)
    seoul_gus_data_list = list()

    for obj_dict in cursor_objs_list:
        if obj_dict.get('seoul'):
            seoul_gus_data_list = obj_dict['seoul']
            break

    # print(seoul_gus_data_list)
    return seoul_gus_data_list

