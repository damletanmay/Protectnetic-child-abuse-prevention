from django.shortcuts import render,redirect

# Create your views here.
def root(request):
    return render(request,'index.html')

def report(request):
    return render(request,'report.html')

def search(request):
    return render(request,'search.html')
