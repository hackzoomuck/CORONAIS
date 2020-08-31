from django.http import HttpResponse
import json
from django.shortcuts import render
import corona_map.MongoDbManager as comong


def seoul_main(request):
    return render(request, 'seoul_map/index.html')


