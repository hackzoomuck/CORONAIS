import corona_map.MongoDbManager as comong
from urllib.parse import unquote
from bs4 import BeautifulSoup
import requests

# 현재날짜를 사용하기 위한 모듈
import datetime


# '보건복지부_코로나19시,도발생_현황 조회 서비스' api 데이터전처리함수
def infection_city():
    print('보건복지부_코로나19시,도발생_현황 조회 서비스 - 데이터 입력 중')
    # 수녕, 서율, 지은 apikey
    inf_serviceKey = ['67xjSd3vhpWMN4oQ3DztMgLyq4Aa1ugw1ssq%2FHeJAeniNIwyPspLp7XpNoa8mBbTJQPc3dAxqvtFm57fJIfq8w%3D%3D',
                      'hFxBvUwCFBcRvWK6wJdgZXgFmjnogBAgCMQ%2BWfZmCQngtc%2FkNb%2FvVqfS2ouV%2BxKMAbEbE94ZYhW3m6A3hxKyig%3D%3D',
                      '%2BNZvj3PPWZaxtFa6tqekV3%2BWlT4NSYB4HY5kXLacieOJKfCtyZpafsGzvJsZzvOMg2KUGrKEIQyy9k58uA1g1A%3D%3D']
    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson'
    SERVICE_KEY = unquote(inf_serviceKey[1]),
    now = datetime.datetime.now()
    nowDate = int(now.strftime('%Y%m%d'))
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': 1,
        'numOfRows': 1,
        'startCreateDt': nowDate,
        'endCreateDt': nowDate
    }

    res = requests.get(url, params=params)

    if res.status_code == 200:
        html = res.text
        if html is '':
            return print('오늘 데이터가 업데이트 되지 않았습니다.')
        print('html',html)
        soup = BeautifulSoup(html, 'html.parser')
        item_tag = soup.select('item')
        for item in item_tag:
            item_dict = {}
            # 시도명(한글)
            item_dict['gubun'] = item.find('gubun').string
            #시도명(영어)
            item_dict['gubunen'] = item.find('gubunen').string
            # 확진자 수(총 확진자 수)
            item_dict['defcnt'] = int(item.find('defcnt').string)
            # 격리중 환자수(현재 확진자 수)
            item_dict['isolingcnt'] = int(item.find('isolingcnt').string)
            # 전일대비 증감 수(오늘 확진자 수)
            item_dict['incdec'] = int(item.find('incdec').string)
            # 격리 해제 수(총완치자수)
            item_dict['isolclearcnt'] = int(item.find('isolclearcnt').string)
            # 사망자 수
            item_dict['deathcnt'] = int(item.find('deathcnt').string)
            # 기준일시2020년 08월 14일 00시
            item_dict['stdday'] = item.find('stdday').string
            # 등록일시분초 2020-08-14 10:36:59.393
            item_dict['createdt'] = item.find('createdt').string

            date_string = item.find('createdt').string[:10].split('-')
            dateis = ''.join(date_string)
            item_dict['id'] = int(dateis)
            print(item_dict)
            comong.Infection_City().add_user_on_collection(item_dict)

        print('보건복지부_코로나19시,도발생_현황 조회 서비스 - 데이터 입력 완료')
        return "good infection_city.py"