from corona_map.Api import Gugun_status
from corona_map.Api import Gugun_status_calc

def seoul_data_init():
    Gugun_status.init_gugun_data()
    Gugun_status_calc.init_seoul_calc_data()



