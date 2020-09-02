from django.shortcuts import render
import pandas as pd
import folium
import json
from corona_map.Api.Infection_status import infection_state_all_value
from corona_map.Api.Infection_city import infection_city_gubun_defcnt
from corona_map.Api.main_data_graph_function import infection_city_all_values, infection_city_oneday_values, infection_all_value, infection_oneday_value, infection_by_age_all_value, infection_by_gender_all_value
from corona_map.Api.data_init import seoul_data_init, folium_data_init
from corona_map.Api.Gugun_status_calc import get_seoul_calc_data_list

# 데이터 init 함수
def call_data_init(request):
    seoul_data_init()
    folium_data_init()
    return render(request, 'corona_map/coIs_init.html', {'soup_data': 'call_data_init에서 넘어옴'})


def call_gugun_info(request):
    data = get_seoul_calc_data_list()
    return render(request, 'corona_map/coIs_init.html', {'soup_data': data})


# 템플릿 적용
# infection_state_all_value() 함수 사용
def cois_main(request):
    # 총 확진자수, 격리해제수, 검사진행수, 사망자수 구하기 위한 함수
    in_st_dict = infection_state_all_value()

    # 지역별 코로나 총확진자 현황
    item_list_result = infection_city_all_values()
    barCityAllKeys = item_list_result['i_city_all_key']
    barCityAllVals = item_list_result['i_city_all_value']

    # 지역별 코로나 일별확진자 현황
    item_city_oneday_result = infection_city_oneday_values()
    barCityOnedayKeys = item_city_oneday_result['i_city_oneday_key']
    barCityOnedayVals = item_city_oneday_result['i_city_oneday_value']


    # 날자별 코로나 총확진자 현황
    item_state_all_result = infection_all_value()
    lineAllKeys = item_state_all_result['i_state_all_key']
    lineAllVals = item_state_all_result['i_state_all_value']

    # 날자별 코로나 일별확진자 현황
    item_i_oneday_result = infection_oneday_value()
    lineOnedayKeys = item_i_oneday_result['oneday_key_list']
    lineOnedayVals = item_i_oneday_result['oneday_value_list']

    ##################################################################################

    # 성별, 연령별
    # 연령별 치명률 현황
    age_result_dict = infection_by_age_all_value()
    oldGubunNames = age_result_dict['age_key_list']
    oldPlotVals = age_result_dict['age_value_list']

    age_dict = dict()
    for k, v in zip(oldGubunNames, oldPlotVals):
        age_dict[k] = v

    age_dict = dict(sorted(age_dict.items(), reverse=True))

    oldGubunNames.clear()
    oldPlotVals.clear()

    for k in age_dict.keys():
        oldGubunNames.append(k)

    for v in age_dict.values():
        oldPlotVals.append(v)

    # 성별 치명률 현황
    gender_result_dict = infection_by_gender_all_value()
    genderGubunNames = gender_result_dict['gender_key_list']
    genderPlotVals = gender_result_dict['gender_value_list']

    context = {'barCityAllVals': barCityAllVals, 'barCityAllKeys': barCityAllKeys,
               'lineAllVals': lineAllVals, 'lineAllKeys': lineAllKeys, 'oldPlotVals': oldPlotVals, 'oldGubunNames': oldGubunNames,
               'genderPlotVals': genderPlotVals, 'genderGubunNames': genderGubunNames, 'decideCnt': in_st_dict['decidecnt'],
               'clearCnt': in_st_dict['clearcnt'],'examCnt': in_st_dict['examcnt'],'deathCnt': in_st_dict['deathcnt'],
               'lineOnedayKeys': lineOnedayKeys, 'lineOnedayVals': lineOnedayVals,
               'barCityOnedayKeys': barCityOnedayKeys, 'barCityOnedayVals': barCityOnedayVals}

    return render(request, 'corona_map/index.html', context)



# 한국 지도에서 시도별, 확진자 수
# infection_city_gubun_defcnt() 함수 사용
def folium_page(request):

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

    # 보여주는 중심부의 위도, 경도
    seoul_center = [35.5, 132.0]
    # 맵이 center 에 위치하고, zoom 레벨은 7로 시작하는 맵 m
    m = folium.Map(location=seoul_center, zoom_start=7, width='100%', height='100%')

    # Choropleth 레이어를 만들고, 맵 m에 추가
    folium.Choropleth(
        geo_data=json_data,
        data=data_df,
        columns=('시', '확진자'),
        key_on='feature.properties.CTP_KOR_NM',
        fill_color='PuRd'
         ).add_to(m)



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
                       {'시':'서울','위도':37.56,'경도':126.97,'링크':'"http://127.0.0.1:8000/seoul-main/"'}]


    for si_ma in sido_lati_longi:
        sido_html = '<h4>{}</h4><h4>총 확진자 {}</h4><a href='.format(si_ma['시'], soup_sido_data_list[si_ma['시']])+si_ma['링크']+'target="_blank">{}</a>'.format(si_ma['시'])
        folium.Marker([si_ma['위도'], si_ma['경도']],
            popup=folium.map.Popup(sido_html, parse_html=False, max_width=200), #.decode('cp949').encode('utf-8')
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)

    m = m._repr_html_()  # updated
    context = {'mapdata': m}
    return render(request, 'corona_map/folium_page.html', context)
