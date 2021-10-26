from django.shortcuts import render,redirect
from .AgeDetection import process_images
from .PDetector import p_detect
import os
import requests as req

def root(request):
    return render(request,'index.html')

# def handle_img(request):
#     return render(request,'search.html',{"msg":"P-content Found"})

def handle_link(request):
    #save scraped images in /images folder then ...
    print(dict(request.POST.items()))
    link = request.POST.get('link')
    path = os.path.dirname(__file__)
    path = path + r"\images"
    age_array = process_images(path)
    # print(age_array)
    if age_array:
        predictions = p_detect(path)
        for i in predictions:
            print(i)
        return render(request,'search.html')
    else:
        return render(request,'search.html',{'error':'Some Error Occured!'})

def handle_txt(request):
    return render(request,'search.html')

def handle_csv(request):
    return render(request,'search.html')

def search(request):
    if request.method == 'GET':
        return render(request,'search.html')
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
    return render(request,'report.html')
