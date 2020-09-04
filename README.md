# CORONAIS
공공데이터 API에서 제공하는 코로나-19 데이터는 각 시도/시 등 큰 행정구역별 데이터만 제공하고 있으며, 각 자치단체 홈페이지 또한 확진자를 제외한 자세한 내용은 종합하여 제공하고 있지 않았습니다. 때문에 작은 행정단위 구역의 정보또한 종합하여 제공하여 비교할 수 있는 데이터를 알기 쉽게 제공하고자 해당 웹 사이트를 제작하게 되었습니다.
# 프로젝트 정보
## 프로젝트 기간
2020.08.10 ~ 2020.09.04
## 인원
3명
## 개발 플랫폼
Windows 10
## 개발 툴
pycharm, robomongo
## 사용 언어
Python 3.7.8
## 사용 기술
Django, MongoDB
# 데이터베이스 구조 (MongoDB)
![ERD](https://raw.githubusercontent.com/hackzoomuck/CORONAIS/master/coronais-photo/ERD.png)
# 스토리보드
![스토리보드-1](https://raw.githubusercontent.com/hackzoomuck/CORONAIS/master/coronais-photo/스토리보드1.jpg)
![스토리보드-1](https://raw.githubusercontent.com/hackzoomuck/CORONAIS/master/coronais-photo/스토리보드2.jpg)
# 제공 서비스
## 전국 코로나 현황
![메인페이지-1](https://raw.githubusercontent.com/hackzoomuck/CORONAIS/master/coronais-photo/mainpage-1.PNG)
![메인페이지-2](https://raw.githubusercontent.com/hackzoomuck/CORONAIS/master/coronais-photo/mainpage-2.PNG)
## 서울시 코로나 현황
![서울시 코로나 현황-1](https://raw.githubusercontent.com/hackzoomuck/CORONAIS/master/coronais-photo/detail-seoul-1.PNG)
![서울시 코로나 현황-2](https://raw.githubusercontent.com/hackzoomuck/CORONAIS/master/coronais-photo/detail-seoul-2.PNG)
## 뉴스
![뉴스 게시글 목록-1](https://raw.githubusercontent.com/hackzoomuck/CORONAIS/master/coronais-photo/corona-new-1.PNG)
![뉴스 게시글-1](https://raw.githubusercontent.com/hackzoomuck/CORONAIS/master/coronais-photo/corona-new-detail-1.PNG)
# 환경 설정
## 가상 환경 설정 (venv)
새로운 venv 환경설정시, <br>
pip install git+https://github.com/python-visualization/branca.git@master <br>
명령을 내린 후 pip install 해야함.
(folium encoding 관련)
```
ERROR: Could not find a version that satisfies the requirement branca==0.4.1+3.g5887b9b (from -r requirements.txt (line 3)) (from versions: 0.1.1, 0.2.0, 0.3.0, 0.3.1, 0.4.0, 0.4.1)
ERROR: No matching distribution found for branca==0.4.1+3.g5887b9b (from -r requirements.txt (line 3))
```
하지 않을 경우 위와 같은 에러를 만날 수 있음.
## 데이터 베이스 설정
1. CORONAIS/settings.py 에서 DATABASES: 'HOST'에 DB서버의 IP를 기입 (약 80번째 줄 시작)
```python
'default': {
        'ENGINE': 'djongo',
        'NAME': 'coronais', # DB명
        'USER': 'coronais', # 데이터베이스 계정
        'PASSWORD':'coronais', # 계정 비밀번호
        'HOST':'localhost', # 데이테베이스 IP
        'PORT':'27017', # 데이터베이스 port
     }
```
2. 몽고디비에 기본 컬렉션을 만들어준다. (RDB의 테이블)
터미널에서 파이썬 마이그레이션 명령 실행
```bash
python manage.py makemigrations
python manage.py migrate
```
3.  corona_map/MongoDbManage.py 에서 연결 IP도 수정해준다.
현재 7 Line
```python
client = pymongo.MongoClient(host='localhost', port=27017)
```

# 남은 작업
1. 전국 시, 군, 구 별 현황.
데이터가 너무 많아 아직 서울시만 제공..
2. 각 데이터를 API로 제공.
3. 2.번의 API를 이용한 
