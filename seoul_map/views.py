import json
import folium
from django.shortcuts import render
from corona_map.Api.Gugun_status_calc import get_seoul_calc_data_list, get_daily_incdec_list, get_seoul_total_data_dict

def seoul_main(request):
    seoul_total_data = get_seoul_total_data_dict()
    daily_gu_all_data_list = get_daily_incdec_list()

    datetime_list = list()
    daily_incdec_list = list()

    for data in daily_gu_all_data_list:
        datetime_list.append(data['stdday'])
        daily_incdec_list.append(data['incdec'])

    daily_gu_data_list = list(get_seoul_calc_data_list())

    area_list = list()
    area_daily_incdec_list = list()

    for data in daily_gu_data_list:
        # print(data)
        area_list.append(data['gubunsmall'])
        area_daily_incdec_list.append(data['incdec'])




    context = {
        'datetime_list':datetime_list,
        'daily_incdec_list':daily_incdec_list,
        'area_list':area_list,
        'area_daily_incdec_list':area_daily_incdec_list,
      
        'defcnt':seoul_total_data['defcnt'],
        'isolclearcnt':seoul_total_data['isolclearcnt'],
        'isolingcnt':seoul_total_data['isolingcnt'],
        'deathcnt':seoul_total_data['deathcnt']-1
    }   

    return render(request, 'seoul_map/index.html', context)

# 서울 지도
def seoul_map(request):
    # 중심위치 잡아서 지도보여주기 위한 변수 입력.
    m = folium.Map([37.562600, 126.991732], zoom_start=12)

    # 서울시 구 별로 구분시켜주는 선을 그려주기 위해서 seoul_line.json 사용
    with open('corona_map/static/json_data/seoul_line.json', mode='rt', encoding='utf-8') as sl:
        geo = json.loads(sl.read())
        sl.close()
    # 서울시 구 별 위도 경도 seoul_lati_longi.json 사용
    with open('corona_map/static/json_data/seoul_lati_longi.json', mode='rt', encoding='utf-8') as sll:
        seo_ll = json.loads(sll.read())
        sll.close()

    # get_seoul_yesterday_data_list 데이터를 변수 seoul_list 에 저장
    seoul_list = get_seoul_calc_data_list()
    # seoul_list에 위도, 경도 추가된 데이터, seoul_data_add_lati_longi_list 변수에 저장
    seoul_data_add_lati_longi_list = []
    for gsl, gsll in zip(seoul_list, seo_ll):
        gsl["lng"] = gsll["lng"]
        gsl["lat"] = gsll["lat"]
        seoul_data_add_lati_longi_list.append(gsl)

    # popup 창에 seoul_data_add_lati_longi_list 데이터 저장
    for seoul_dict in seoul_data_add_lati_longi_list:
        popup_info = '<h4>{}</h4> <p>총 확진자 {}</p><p>격리중 환자수 {}&nbsp;오늘 확진자 수 {}</p><p>격리 해제 수 {}&nbsp;완치자 수 {}</p><p>사망자 수 {}</p>'.format(seoul_dict['gubunsmall'], seoul_dict['defcnt'],seoul_dict['isolingcnt'],seoul_dict['incdec'],seoul_dict['isolclearcnt'],seoul_dict['curedcnt'],seoul_dict['deathcnt'])
        folium.Marker(
            location=[float(seoul_dict['lat']), float(seoul_dict['lng'])],
            popup=folium.map.Popup(popup_info, max_width=200),
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)

    folium.GeoJson(
        geo,
        name='seoul_line'
    ).add_to(m)
    m = m._repr_html_()  # updated
    context = {'my_map': m}


    return render(request, 'seoul_map/seoul_map.html', context)


