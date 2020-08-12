from django.shortcuts import render

# Create your views here.
def coIs_home(request):
    return render(request, 'corona_map/coIs_home.html')
