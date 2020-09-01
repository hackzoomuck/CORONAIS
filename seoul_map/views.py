import json
import folium
from django.shortcuts import render
from corona_map.Api.Gugun_status import get_seoul_data_list

def seoul_main(request):
    return render(request, 'seoul_map/index.html')

# 서울 지도
def seoul_map(request):
    # 중심위치 잡아서 지도보여주기 위한 변수 입력.
    m = folium.Map([37.562600, 126.991732], zoom_start=11)

    # 서울시 구 별로 구분시켜주는 선을 그려주기 위해서 seoul_line.json 사용
    with open('corona_map/static/json_data/seoul_line.json', mode='rt', encoding='utf-8') as sl:
        geo = json.loads(sl.read())
        sl.close()
    # 서울시 구 별 위도 경도 seoul_lati_longi.json 사용
    with open('corona_map/static/json_data/seoul_lati_longi.json', mode='rt', encoding='utf-8') as sll:
        seo_ll = json.loads(sll.read())
        sll.close()

    # get_seoul_data_list 데이터를 변수 seoul_list 에 저장
    seoul_list = get_seoul_data_list()
    print(seoul_list)
    # seoul_list에 위도, 경도 추가된 데이터, seoul_data_add_lati_longi_list 변수에 저장
    seoul_data_add_lati_longi_list = []
    for gsl, gsll in zip(seoul_list, seo_ll):
        gsl["lng"] = gsll["lng"]
        gsl["lat"] = gsll["lat"]
        seoul_data_add_lati_longi_list.append(gsl)

    # popup 창에 seoul_data_add_lati_longi_list 데이터 저장
    for seoul_dict in seoul_data_add_lati_longi_list:
        popup_info = '<h4>{}</h4> <h5>총 확진자 {}</h5><br><h5>격리중 환자수 {}</h5><br><h5>격리 해제 수 {}</h5><br><h5>사망자 수 {}</h5>'.format(seoul_dict['gubunsmall'], seoul_dict['defcnt'],seoul_dict['isolingcnt'],seoul_dict['isolclearcnt'],seoul_dict['deathcnt'])
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


