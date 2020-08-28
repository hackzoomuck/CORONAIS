import corona_map.MongoDbManager as comong
from urllib.parse import unquote, urljoin
from bs4 import BeautifulSoup
import requests

# 현재날짜를 사용하기 위한 모듈
import datetime


def news_board_list():
    main_url = 'https://yna.co.kr'
    url = 'https://ars.yna.co.kr/api/v2/sokbo?lang=KR&count=100&minute=800'
    response = requests.get(url)
    json_text = response.json()
    json_url_list = []
    json_data = json_text['DATA']
    word = '코로나'
    for json_url in json_data:
        title_url_dict = dict()
        title_url_dict['datetime'] = json_url['DATETIME']
        if word in json_url['TITLE']:
            title_url_dict['url'] = urljoin(main_url, json_url['URL'])
            json_url_list.append(title_url_dict)

    count = 0
    for corona_url in json_url_list:
        response = requests.get(corona_url['url'])
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        news_title = soup.select_one('title').text.split('|')[0]
        tag_test = '#articleWrap > div.content01.scroll-article-zone01 > div > div > div.story-news.article p'
        gisa_list = soup.select(tag_test)
        gisa_content_str = ''
        gisa_dict = dict()
        for gisa in gisa_list:
            gisa_content_str += gisa.text
        gisa_dict['id'] = int(corona_url['datetime'][0:8])*100 + count
        count += 1
        gisa_dict['title'] = news_title
        gisa_dict['content'] = gisa_content_str
        comong.News_Board().add_user_on_collection(gisa_dict)
    return "good! new board"