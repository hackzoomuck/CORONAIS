from corona_map.Api import Gugun_status
from corona_map.Api import Gugun_status_calc

from corona_map.Api.Gugun_status import get_seoul_data_list, init_gugun_data



from corona_map.Api import Infection_city, Infection_status, Infection_by_age_gender, News_board

def seoul_data_init():
    flag = False
    flag = Gugun_status.init_gugun_data()

    if flag:
        Gugun_status_calc.init_seoul_calc_data()

def folium_data_init():
    # mongodb collection infection_city에 api request해서 데이터 저장.
    # Infection_city.infection_city()
    # News_board.news_board_list()
    # Infection_by_age_gender.infection_by_age_gender()
    # Infection_status.infection_status()

