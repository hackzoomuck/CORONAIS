from django.shortcuts import render
import corona_map.MongoDbManager as comong
from django.shortcuts import render, get_object_or_404, redirect

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def news_board(request):
    board_list = comong.News_Board().get_users_from_collection({})
    return render(request, 'news_board/news_board_list.html', {'board_list': board_list})


def news_board_detail(request, pk):
    board_detail = comong.News_Board.get_users_from_collection()
    return render(request, 'news_board/news_board_detail.html', {'board_detail': board_detail})


def news_board_list(request):
    main_url = 'https://yna.co.kr'
    url = 'https://ars.yna.co.kr/api/v2/sokbo?lang=KR&count=300&minute=800'
    response = requests.get(url)
    json_text = response.json()
    json_url_list = []
    json_data = json_text['DATA']
    word = '코로나'
    for json_url in json_data:
        if word in json_url['TITLE']:
            json_url_list.append(urljoin(main_url, json_url['URL']))

    gisa_result_list = []
    for corona_url in json_url_list:
        response = requests.get(corona_url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        news_title = soup.select_one('title').text.split('|')[0]
        tag_test = '#articleWrap > div.content01.scroll-article-zone01 > div > div > div.story-news.article p'
        gisa_list = soup.select(tag_test)
        gisa_content_str = ''
        gisa_dict = dict()
        for gisa in gisa_list:
            gisa_content_str += gisa.text
        gisa_dict['title'] = news_title
        gisa_dict['content'] = gisa_content_str
        gisa_result_list.append(gisa_dict)
    return render(request, 'news_board/news_board_list_crawling.html', {'news_board_list': gisa_result_list})
