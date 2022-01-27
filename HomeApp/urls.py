from django.urls import path
from . import views
# making urlpatterns for 3 different pages.
urlpatterns = [
    path('', views.root,name='index'),
    path('search', views.search,name='search'),
    path('report', views.report,name='report')
]
