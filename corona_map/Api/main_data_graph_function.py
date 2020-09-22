import datetime
import corona_map.MongoDbManager as comong





'''
# 작성자 : 최수녕
# 함수 설명 : infection_city 테이블에서 id의 최댓값을 구하는 함수(가장 최근 날짜 구하기)
# 리턴값 : id의 최댓값(숫자)
'''
def infection_city_max_id():
    max_id = comong.Infection_City().get_aggregate_users_from_collection([{'$group':{'_id':'null','total':{'$max':'$id'}}},{'$project':{'_id':0,'total':1}}])
    max_id = list(max_id)[0]['total']
    return max_id


'''
# 작성자 : 최수녕
# 함수 설명 : 시도별 총확진자 구하는 함수
# 리턴값 : 시/도 이름 list , 시/도에 따른 총확진자 list
'''
def infection_city_all_values():
    max_date = infection_city_max_id()
    infection_date_data = comong.Infection_City().get_particular_users_from_collection({'$and':[{'id':max_date},{'gubun':{'$nin':['합계','검역']}}]},{'gubun': 1, 'defcnt': 1, '_id': 0})
    i_city_all_key = []
    i_city_all_value = []
    for infection_data in infection_date_data:
        i_city_all_key.append(infection_data['gubun'])
        i_city_all_value.append(infection_data['defcnt'])
    context = {'i_city_all_key': i_city_all_key, 'i_city_all_value': i_city_all_value}
    return context


'''
# 작성자 : 최수녕
# 함수 설명 : 시도별 일별 확진자 구하는 함수
# 리턴값 : 시/도 이름 list , 시/도에 따른 확진자(전일대비 증감 수) list
'''
def infection_city_oneday_values():
    max_date = infection_city_max_id()
    infection_date_data = comong.Infection_City().get_particular_users_from_collection({'$and':[{'id':max_date},{'gubun':{'$nin':['합계','검역']}}]},{'gubun': 1, 'incdec': 1, '_id': 0})
    i_city_oneday_key = []
    i_city_oneday_value = []
    for infection_data in infection_date_data:
        i_city_oneday_key.append(infection_data['gubun'])
        i_city_oneday_value.append(infection_data['incdec'])
    context = {'i_city_oneday_key': i_city_oneday_key, 'i_city_oneday_value': i_city_oneday_value}
    return context


'''
# 작성자 : 최수녕
# 함수 설명 : 전국 일별 코로나 총확진자 데이터 구하는 함수
# 리턴값 : 날자값 list, 날자에 따른 일별 확진자 list
'''
def infection_all_value():
    now = datetime.datetime.now()
    nowDate = int(now.strftime('%Y%m%d'))
    pastday_at_this_time = datetime.datetime.now() - datetime.timedelta(days=7)
    pastDate = int(pastday_at_this_time.strftime('%Y%m%d'))

    infection_date_data = comong.Infection_Status().get_particular_users_from_collection({'$and':[{'id':{'$gte':pastDate}},{'id':{'$lte':nowDate}}]},{'id': 1, 'decidecnt': 1, '_id': 0}).sort('id', 1)
    i_state_all_key = []
    i_state_all_value = []
    for infection_data in infection_date_data:
        i_state_all_key.append(infection_data['id'])
        i_state_all_value.append(infection_data['decidecnt'])
    context = {'i_state_all_key': i_state_all_key, 'i_state_all_value': i_state_all_value}
    return context


'''
# 작성자 : 최수녕
# 함수 설명 : 전국 일별(일별 순수 확진자) 코로나 확진자 데이터 구하는 함수
# 리턴값 : 날자값 list, 날자에 따른 일별 확진자 list
'''
def infection_oneday_value():
    now = datetime.datetime.now()
    nowDate = int(now.strftime('%Y%m%d'))
    pastday_at_this_time = datetime.datetime.now() - datetime.timedelta(days=7)
    pastDate = int(pastday_at_this_time.strftime('%Y%m%d'))

    infection_date_data = comong.Infection_Status().get_particular_users_from_collection(
        {'$and': [{'id': {'$gte': pastDate}}, {'id': {'$lte': nowDate}}]},
        {'decidecnt': 1, 'id': 1, '_id': 0}).sort('id',1)

    infection_data_list = list(infection_date_data)
    oneday_value_list = []
    oneday_key_list = []
    for i in range(0, len(infection_data_list) - 1):
        decidecnt_oneday_data = int(infection_data_list[i + 1]['decidecnt'] - infection_data_list[i]['decidecnt'])
        id_oneday_data = infection_data_list[i+1]['id']
        oneday_value_list.append(decidecnt_oneday_data)
        oneday_key_list.append(id_oneday_data)

    context = {'oneday_value_list': oneday_value_list, 'oneday_key_list': oneday_key_list}
    return context


'''
# 작성자 : 최수녕
# 함수 설명 : 나이별 치명률 평균값 구하는 함수
# 리턴값 : 성별(여성/남성) list , 성별에 따른 치명률 list
'''
def infection_by_age_all_value():
    infection_date_data = comong.Infection_By_Age_Gender().get_aggregate_users_from_collection(
        [
            {'$match': {'$and': [{'gubun': {'$not': {'$regex': '여성'}}}, {'gubun': {'$not': {'$regex': '남성'}}}]}},
            {'$group': {'_id': '$gubun', 'mean_criticalrate': {'$avg': '$criticalrate'}}},
            {'$sort': {'mean_criticalrate': -1}},
            {
                '$project': {
                    'gubun': '$_id',
                    'mean_criticalrate': 1,
                    '_id': 0
                }
            }
        ]
    )
    infection_by_age_all_value_list = list(infection_date_data)
    age_key_list = []
    age_value_list = []
    for infection_by_age_all_value_dict in infection_by_age_all_value_list:
        age_key_list.append(infection_by_age_all_value_dict['gubun'])
        age_value_list.append(infection_by_age_all_value_dict['mean_criticalrate'])

    context = {'age_key_list': age_key_list, 'age_value_list': age_value_list}

    return context


'''
# 작성자 : 최수녕
# 함수 설명 : 성별 치명률 평균값 구하는 함수
# 리턴값 : 성별(여성/남성) list , 성별에 따른 치명률 list
'''
def infection_by_gender_all_value():
    infection_date_data = comong.Infection_By_Age_Gender().get_aggregate_users_from_collection(
        [
            {'$match': {'$or': [{'gubun': {'$regex': '여성'}}, {'gubun': {'$regex': '남성'}}]}},
            {'$group': {'_id': '$gubun', 'mean_criticalrate': {'$avg': '$criticalrate'}}},
            {'$sort': {'mean_criticalrate': -1}},
            {
                '$project': {
                    'gubun': '$_id',
                    'mean_criticalrate': 1,
                    '_id': 0
                }
            }
        ]
    )
    infection_by_gender_all_value_list = list(infection_date_data)
    age_key_list = []
    age_value_list = []
    for infection_by_age_all_value_dict in infection_by_gender_all_value_list:
        age_key_list.append(infection_by_age_all_value_dict['gubun'])
        age_value_list.append(infection_by_age_all_value_dict['mean_criticalrate'])

    context = {'gender_key_list': age_key_list, 'gender_value_list': age_value_list}
    return context