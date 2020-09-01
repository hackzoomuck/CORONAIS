import datetime

from corona_map.Api import Gugun_status
import corona_map.MongoDbManager as DBmanager


def get_seoul_calc_data_dict() -> dict():
    print('서울 데이터 계산 시작')
    seoul_gu_data_list = Gugun_status.get_seoul_data_list()
    #print(seoul_gu_data_list['stdday'])
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

    #print(seoul_calc_data_dict['stdday'])
    print('서울 데이터 계산 끝')
    return seoul_calc_data_dict




def init_seoul_calc_data():
    seoul_data_dict = get_seoul_calc_data_dict()
    print('서울 계산 데이터 insert')
    DBmanager.Infection_Smallcity_Calc().add_gugun_status_datas_on_collection(seoul_data_dict)

def get_seoul_calc_data_list() -> list:
    print('계산된 서울 데이터 꺼냄')
    now_date = int(datetime.datetime.now().strftime('%Y%m%d'))
    sql_query_0 = {'stdday': now_date}
    sql_query_1 = {'_id': 0}

    cursor_obj = DBmanager.Infection_Smallcity_Calc().get_gugun_status_datas_from_collection(sql_query_0, sql_query_1)

    cursor_objs_list = list(cursor_obj)
    seoul_gus_data_list = list()

    for obj_dict in cursor_objs_list:
        if obj_dict.get('seoul'):
            seoul_gus_data_list = obj_dict['seoul']
            break

    return seoul_gus_data_list