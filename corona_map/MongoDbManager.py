import pymongo

# collection infection_city
class Infection_City:
    _instance = None
    # 몽고디비연결
    client = pymongo.MongoClient('mongodb+srv://coronais:1q2w3e4r@cluster0.uy7ix.mongodb.net/coronais?retryWrites=true&w=majority')
    # collection 생성
    database = client['coronais']['infection_city']

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def get_users_from_collection(cls, _query):
        assert cls.database
        return cls.database.find(_query)

    def get_particular_users_from_collection(cls, *_query):
        assert cls.database
        return cls.database.find(_query[0], _query[1])

    def add_user_on_collection(cls, _data):
        if type(_data) is list:
            return cls.database.insert_many(_data)
        else:
            return cls.database.insert_one(_data)

    def get_aggregate_users_from_collection(cls, _query):
        assert cls.database
        return cls.database.aggregate(_query)


# collection infection_by_age_gender
class Infection_By_Age_Gender:
    _instance = None
    # 몽고디비연결
    client = pymongo.MongoClient('mongodb+srv://coronais:1q2w3e4r@cluster0.uy7ix.mongodb.net/coronais?retryWrites=true&w=majority')
    # collection 생성
    database = client['coronais']['infection_by_age_gender']

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def get_users_from_collection(cls, _query):
        assert cls.database
        return cls.database.find(_query)

    def get_aggregate_users_from_collection(cls, _query):
        assert cls.database
        return cls.database.aggregate(_query)


    def add_user_on_collection(cls, _data):
        if type(_data) is list:
            return cls.database.insert_many(_data)
        else:
            return cls.database.insert_one(_data)

# collection infection_status
class Infection_Status:
    _instance = None
    # 몽고디비연결
    client = pymongo.MongoClient('mongodb+srv://coronais:1q2w3e4r@cluster0.uy7ix.mongodb.net/coronais?retryWrites=true&w=majority')
    # collection 생성
    database = client['coronais']['infection_status']

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def get_users_from_collection(cls, _query):
        assert cls.database
        return cls.database.find(_query)

    def get_particular_users_from_collection(cls, *_query):
        assert cls.database
        return cls.database.find(_query[0], _query[1])


    def add_user_on_collection(cls, _data):
        if type(_data) is list:
            return cls.database.insert_many(_data)
        else:
            return cls.database.insert_one(_data)


class News_Board:
    _instance = None
    # 몽고디비연결
    client = pymongo.MongoClient('mongodb+srv://coronais:1q2w3e4r@cluster0.uy7ix.mongodb.net/coronais?retryWrites=true&w=majority')
    # collection 생성
    database = client['coronais']['news_board']
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def get_users_from_collection(cls, _query):
        assert cls.database
        return cls.database.find(_query)

    def get_users_one_from_collection(cls, _query):
        assert cls.database
        return cls.database.find_one(_query)

    def add_user_on_collection(cls, _data):
        if type(_data) is list:
            return cls.database.insert_many(_data)
        else:
            return cls.database.insert_one(_data)

class News_Board_Comment:
    _instance = None
    # 몽고디비연결
    client = pymongo.MongoClient('mongodb+srv://coronais:1q2w3e4r@cluster0.uy7ix.mongodb.net/coronais?retryWrites=true&w=majority')
    # collection 생성
    database = client['coronais']['news_board_comment']
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def get_users_from_collection(cls, _query):
        assert cls.database
        return cls.database.find(_query)

    def get_users_one_from_collection(cls, _query):
        assert cls.database
        return cls.database.find_one(_query)

    def get_particular_users_from_collection(cls, _query, _query2):
        assert cls.database
        return cls.database.find(_query, _query2)

    def add_user_on_collection(cls, _data):
        if type(_data) is list:
            return cls.database.insert_many(_data)
        else:
            return cls.database.insert_one(_data)

class Infection_Smallcity:
    '''
    구 데이터 관리 DB Manager
    '''

    _instance = None
    # 몽고디비연결
    client = pymongo.MongoClient('mongodb+srv://coronais:1q2w3e4r@cluster0.uy7ix.mongodb.net/coronais?retryWrites=true&w=majority')
    # collection 생성
    database = client['coronais']['infection_smallcity']

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def get_gugun_status_datas_from_collection(cls, *_query):
        assert cls.database
        return cls.database.find(_query[0], _query[1])

    def add_gugun_status_datas_on_collection(cls, _data):
        if type(_data) is list:
            return cls.database.insert_many(_data)
        else:
            return cls.database.insert_one(_data)


class Infection_Smallcity_Calc:
    '''
    계산된 구 데이터
    '''

    _instance = None
    # 몽고디비연결
    client = pymongo.MongoClient('mongodb+srv://coronais:1q2w3e4r@cluster0.uy7ix.mongodb.net/coronais?retryWrites=true&w=majority')
    # collection 생성
    database = client['coronais']['infection_smallcity_calc']

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def get_gugun_status_datas_from_collection(cls, *_query):
        assert cls.database
        return cls.database.find(_query[0], _query[1])

    def get_gugun_status_all_data_from_collection(cls):
        assert cls.database
        return cls.database.find({},{'_id': 0})

    def add_gugun_status_datas_on_collection(cls, _data):
        if type(_data) is list:
            return cls.database.insert_many(_data)
        else:
            return cls.database.insert_one(_data)