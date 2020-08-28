import corona_map.MongoDbManager as comong
from urllib.parse import unquote
from bs4 import BeautifulSoup
import requests

# 현재날짜를 사용하기 위한 모듈
import datetime

def infection_by_age_gender():

    inf_serviceKey = ['67xjSd3vhpWMN4oQ3DztMgLyq4Aa1ugw1ssq%2FHeJAeniNIwyPspLp7XpNoa8mBbTJQPc3dAxqvtFm57fJIfq8w%3D%3D',
                      'hFxBvUwCFBcRvWK6wJdgZXgFmjnogBAgCMQ%2BWfZmCQngtc%2FkNb%2FvVqfS2ouV%2BxKMAbEbE94ZYhW3m6A3hxKyig%3D%3D',
                      '%2BNZvj3PPWZaxtFa6tqekV3%2BWlT4NSYB4HY5kXLacieOJKfCtyZpafsGzvJsZzvOMg2KUGrKEIQyy9k58uA1g1A%3D%3D']
    SERVICE_KEY = unquote(inf_serviceKey[2])
    now = datetime.datetime.now()
    nowDate = int(now.strftime('%Y%m%d'))

    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19GenAgeCaseInfJson'
    params = {
        'serviceKey': SERVICE_KEY,
        'numOfRows': 10,
        'pageNo': 10,
        'startCreateDt': '20200310',
        'endCreateDt': '20200814'  # datetime.datetime.now()
    }
    res = requests.get(url, params=params)

    if res.status_code == 200:
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        item_list = soup.select('item')
        print(html)
        for item in item_list:
            item_dict = {}
            # 확진자
            item_dict['confcase'] = int(item.find('confcase').string)
            # 확진률
            item_dict['confcaserate'] = item.find('confcaserate').string
            # 등록일시분초 2020-08-24 10:21:08.129
            item_dict['createdt'] = item.find('createdt').string
            # 치명률
            item_dict['criticalrate'] = float(item.find('criticalrate').string)
            # 사망자
            item_dict['death'] = int(item.find('death').string)
            # 사망률
            item_dict['deathrate'] = item.find('deathrate').string
            # 구분(성별,연령별)0-9
            item_dict['gubun'] = item.find('gubun').string

            date_string = item.find('createdt').string[:10].split('-')
            dateis = ''.join(date_string)
            item_dict['id'] = int(dateis)

            comong.Infection_By_Age_Gender().add_user_on_collection(item_dict)
        return 'good! infection_by_age_gender'
    return 'NO! infection_by_age_gender'
