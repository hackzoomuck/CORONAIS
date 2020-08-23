from django.shortcuts import render
import corona_map.MongoDbManager as comong
from django.shortcuts import render, get_object_or_404, redirect


def news_board(request):
    board_list = comong.News_Board().get_users_from_collection({})
    return render(request, 'news_board/news_board_list.html', {'board_list': board_list})


def news_board_detail(request, pk):
    board_detail = comong.News_Board.get_users_from_collection()
    return render(request, 'news_board/news_board_detail.html', {'board_detail': board_detail})
