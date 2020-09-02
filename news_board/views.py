from django.http import HttpResponse
import json
from django.shortcuts import render
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import base64

import corona_map.MongoDbManager as comong


# 뉴스 기사 리스트조회
def news_board(request):
    board_list = comong.News_Board().get_users_from_collection({}).sort('id',-1)
    return render(request, 'news_board/news_board_list.html', {'board_list': board_list})


# 뉴스 상세페이지 조회
def news_board_detail(request, id):
    board_detail = comong.News_Board().get_users_one_from_collection({'id': id})
    return render(request, 'news_board/news_board_detail.html', {'board_detail': board_detail})


# 뉴스데이터 크롤링 테스트
def news_board_list(request):
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

    gisa_result_list = []
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
        gisa_dict['datetime'] = corona_url['datetime'][0:8]
        gisa_dict['title'] = news_title
        gisa_dict['content'] = gisa_content_str
        gisa_result_list.append(gisa_dict)
    return render(request, 'news_board/news_board_list_crawling.html', {'news_board_list': gisa_result_list})


# Ajax로 댓글 삽입
def news_comment_insert(request):
    id = request.POST['id']
    comment = request.POST['comment']
    comment = comment.encode("UTF-8")
    comment = base64.b64encode(comment)
    comment = comment.decode("UTF-8")
    context = {'id': id, 'comment': comment}
    result = comong.News_Board_Comment().add_user_on_collection(context)
    if result:
        status = 'success'
    else:
        status = 'fail'
    return HttpResponse(status, content_type='application/json')


# Ajax로 댓글 조회 불러오기
def news_comment_list(request, id):
    print('news_comment_list진입')
    comment_data_list = comong.News_Board_Comment().get_particular_users_from_collection({'id': str(id)}, {'_id': 0}).sort('id',-1)
    comment_list = list()
    for data_dict in comment_data_list:
        comment = data_dict['comment']
        comment = comment.encode("UTF-8")
        comment = base64.b64decode(comment)
        comment = comment.decode("UTF-8")
        dict = {
            'id':data_dict['id'],
            'comment':comment
        }
        comment_list.append(dict)
    return HttpResponse(json.dumps(comment_list), content_type='application/json')
