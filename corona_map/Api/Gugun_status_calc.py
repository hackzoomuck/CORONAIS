import datetime

from corona_map.Api import Gugun_status
import corona_map.MongoDbManager as DBmanager


def get_seoul_calc_data_dict() -> dict():
    seoul_gu_data_list = Gugun_status.get_seoul_data_list()
    seoul_gu_yesterday_data_list = Gugun_status.get_seoul_yesterday_data_list()

    seoul_gu_calc_data_list = list()
    for new, old in zip(seoul_gu_data_list, seoul_gu_yesterday_data_list):
        seoul_gu_calc_data_dict = dict()
        seoul_gu_calc_data_dict['gubunsmall'] = new['gubunsmall']       # 구/군명(한글)
        seoul_gu_calc_data_dict['defcnt'] = int(new['defcnt'])               # 확진자 수(총확진자 현재감염중 + 총 완치수 + 사망자 수)
        seoul_gu_calc_data_dict['isolingcnt'] = int(new['isolingcnt'])       # 격리중 환자수(현재확진자수 감염중)

        seoul_gu_calc_data_dict['isolclearcnt'] = int(new['isolclearcnt'])   # 격리 해제 수(총 완치자)
        seoul_gu_calc_data_dict['deathcnt'] = int(new['deathcnt'])           # 사망자 수

        seoul_gu_calc_data_dict['incdec'] = int(new['defcnt']) - int(old['defcnt'])               # 전일대비 증감 수(오늘 확진자수)
        seoul_gu_calc_data_dict['curedcnt'] = int(new['isolclearcnt']) - int(old['isolclearcnt']) # 완치자 수(오늘 완치자수)

        seoul_gu_calc_data_list.append(seoul_gu_calc_data_dict)

    seoul_calc_data_dict = {
        'seoul': seoul_gu_calc_data_list,
        'stdday': int(datetime.datetime.now().strftime('%Y%m%d'))
    }

    return seoul_calc_data_dict




def init_seoul_calc_data():
    seoul_data_dict = get_seoul_calc_data_dict()
    DBmanager.Infection_Smallcity_Calc().add_gugun_status_datas_on_collection(seoul_data_dict)

def get_seoul_calc_data_list() -> list:
    now_date = 0
    if int(datetime.datetime.now().strftime('%H')) >= 14:
        now_date = int(datetime.datetime.now().strftime('%Y%m%d'))
    else:
        timestamp = datetime.datetime.now() - datetime.timedelta(days=1)
        now_date = int(timestamp.strftime('%Y%m%d'))

    sql_query_0 = {'stdday': now_date}
    sql_query_1 = {'_id': 0}

    cursor_obj = DBmanager.Infection_Smallcity_Calc().get_gugun_status_datas_from_collection(sql_query_0, sql_query_1)


    cursor_objs_list = list(cursor_obj)
    seoul_gus_data_list = list()

    for obj_dict in cursor_objs_list:
        if obj_dict.get('seoul'):
            seoul_gus_data_list = obj_dict['seoul']
            break

    return list(seoul_gus_data_list)    

def get_seoul_total_data_dict() -> dict:
    seoul_total = get_seoul_calc_data_list()
    seoul_total_dict = {'defcnt':0,'isolingcnt':0,'isolclearcnt':0,'deathcnt':0}
    for seoul_gugun in seoul_total:
        seoul_total_dict['defcnt'] += seoul_gugun['defcnt']
        if seoul_gugun['gubunsmall'] is '강남구':
            continue
        seoul_total_dict['isolingcnt'] += seoul_gugun['isolingcnt']
        seoul_total_dict['isolclearcnt'] += seoul_gugun['isolclearcnt']
        seoul_total_dict['deathcnt'] += seoul_gugun['deathcnt']

    return seoul_total_dict
  
def get_seoul_calc_all_data_list() -> list:
    cursor_obj = DBmanager.Infection_Smallcity_Calc().get_gugun_status_all_data_from_collection()
    return list(cursor_obj)

def get_daily_incdec_list() -> list:
    seoul_all_data_list = get_seoul_calc_all_data_list()
    seoul_daily_data_list = list()
    for gu_data in seoul_all_data_list:
        seoul_daily_data_dict = dict()
        seoul_daily_data_dict['stdday'] = gu_data['stdday']
        seoul_daily_data_dict['incdec'] = 0

        for gu_dict in gu_data['seoul']:
            seoul_daily_data_dict['incdec'] += gu_dict['incdec']

        seoul_daily_data_list.append(seoul_daily_data_dict)

    return seoul_daily_data_list
