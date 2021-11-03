from django.shortcuts import render, redirect
import os
from . import getImages

def root(request):
    return render(request, 'index.html')

def handle_link(request):

    req_dict = dict(request.POST.items())

    csrfmiddlewaretoken = req_dict['csrfmiddlewaretoken']

    link = request.POST.get('link')

    get_images_session_obj = getImages.GetImages()
    return get_images_session_obj.process_images(request,link,csrfmiddlewaretoken)

def handle_txt(request):
    return render(request, 'search.html')


def handle_csv(request):
    return render(request, 'search.html')


def search(request):
    if request.method == 'GET':
        return render(request, 'search.html')
    elif request.method == 'POST':

        link = request.POST.get('button_link')
        txt = request.POST.get('button_txt')
        csv = request.POST.get('button_csv')

        if link:
            return handle_link(request)
        elif txt:
            return handle_txt(request)
        elif csv:
            return handle_csv(request)


def report(request):
    return render(request, 'report.html')
