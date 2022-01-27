import os
import time
import pprint
from . import getImages
from .models import File
from .models import Report
from .tasks import process_link,process_file
from django.shortcuts import render, redirect

# home page / root page
def root(request):
    return render(request, 'index.html')

# search page
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
            # second parameter to identify which type of file is given
            return handle_file(request,1)
        elif csv:
            return handle_file(request,0)

# to handle search page link response
def handle_link(request):

    req_dict = dict(request.POST.items())
    print(req_dict)
    csrfmiddlewaretoken = req_dict['csrfmiddlewaretoken']
    # this token is used to identify each request uniquely across all the files

    link = request.POST.get('link')

    result = process_link.delay(link,csrfmiddlewaretoken) # calling celery task
    print(result) # task id
    return render(request,'search.html',context={'task_id': result.task_id})

# to handle search page file response
def handle_file(request,isTXT):

    req_dict = dict(request.POST.items())
    csrfmiddlewaretoken_main = req_dict['csrfmiddlewaretoken']
    # this token is used to identify each request uniquely across all the files

    if isTXT:
        user_file = request.FILES['txt']
    else:
        user_file =  request.FILES['csv']

    print(user_file.name)

    # saving the file to later read from it
    files = File()
    files.file = user_file
    files.save()

    path = os.path.join(os.path.join(os.getcwd(),"media"),files.file.name)
    print(path)

    result = process_file.delay(files.file.name,path,csrfmiddlewaretoken_main)
    print(result) # task id
    return render(request,'search.html',context={'task_id': result.task_id})


# report list page
def report(request):
    reports = Report.objects.all()
    return render(request, 'report.html',{'reports':reports})
