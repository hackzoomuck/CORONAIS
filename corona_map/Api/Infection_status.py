import corona_map.MongoDbManager as comong
from urllib.parse import unquote
from bs4 import BeautifulSoup
import requests

# 현재날짜를 사용하기 위한 모듈
import datetime

def infection_status():
    # 수녕, 서율, 지은
    sido_serviceKey = ['0',
                       'BjW9a8K51p0oRJ0hl%2BBpizJzZ9gT3e%2Beb75QhG9kXdeK9ENW7CCAl9nX28%2BRD97JlAsDrTv7StIwvUPCxA4iTw%3D%3D',
                       '%2BNZvj3PPWZaxtFa6tqekV3%2BWlT4NSYB4HY5kXLacieOJKfCtyZpafsGzvJsZzvOMg2KUGrKEIQyy9k58uA1g1A%3D%3D']
    url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson'
    SERVICE_KEY = unquote(sido_serviceKey[1])

    now = datetime.datetime.now()
    nowDate = int(now.strftime('%Y%m%d'))
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': 100,
        'numOfRows': 100,
        'startCreateDt': nowDate,
        'endCreateDt': nowDate
    }
    res = requests.get(url, params=params)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    item_list = soup.select('item')
    item_list_result = []
    for item in item_list:
        item_dict = {}
        try:
            # 확진자 수
            item_dict['decidecnt'] = int(item.find('decidecnt').string)
        except (AttributeError, KeyError):
            item_dict['decidecnt'] = 0

        try:
            # 격리해제 수
            item_dict['clearcnt'] = int(item.find('clearcnt').string)
        except (AttributeError, KeyError):
            item_dict['clearcnt'] = 0

        try:
            # 검사진행 수
            item_dict['examcnt'] = int(item.find('examcnt').string)
        except (AttributeError, KeyError):
            item_dict['examcnt'] = 0

        try:
            # 사망자 수
            item_dict['deathcnt'] = int(item.find('deathcnt').string)
        except (AttributeError, KeyError):
            item_dict['examcnt'] = 0

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


        date_string = item.find('createdt').string[:10].split('-')
        dateis = ''.join(date_string)
        item_dict['id'] = int(dateis)

        item_list_result.append(item_dict)
    comong.Infection_Status().add_user_on_collection(item_list_result)
    # print(item_list_result,'item_list_result==================================')

    return 'infection_status.py complete'



# infection_state collection 전국 코로나 현황 수 get함수
def infection_state_all_value():
    now_date = 0
    if int(datetime.datetime.now().strftime('%H')) >= 14:
        now_date = int(datetime.datetime.now().strftime('%Y%m%d'))
    else:
        timestamp = datetime.datetime.now() - datetime.timedelta(days=1)
        now_date = int(timestamp.strftime('%Y%m%d'))
    # 하루의 시도별 데이터
    infection_date_data = comong.Infection_Status().get_users_from_collection({'id': now_date})

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

    return item_dict
