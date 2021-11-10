from django.urls import path
from . import views
urlpatterns = [
    path('', views.root,name='index'),
    path('search', views.search,name='search'),
    path('report', views.report,name='report')
]
