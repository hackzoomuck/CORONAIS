from corona_map.Api import Gugun_status

def gu_data_calc():
    seoul_gu_data_list = Gugun_status.get_seoul_data_list()
    # for seoul_gu_data_dict in seoul_gu_data_list:
    #     print(seoul_gu_data_dict['gubunsmall'])
    #     print(seoul_gu_data_dict['defcnt'])
    #     print(seoul_gu_data_dict['isolingcnt'])
    #     print(seoul_gu_data_dict['isolclearcnt'])
    #     print(seoul_gu_data_dict['deathcnt'])
    #     print(seoul_gu_data_dict['stdday'])

def get_seoul_gu_data():
    gu_data_calc()