from django.urls import path
from . import views
urlpatterns = [
    path('', views.root,name='index'),
    path('report', views.report,name='report'),
    path('search', views.search,name='search'),
]
