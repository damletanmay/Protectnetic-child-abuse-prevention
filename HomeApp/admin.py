from django.contrib import admin
from .models import Report
from .models import File
# Register your models here.
# registering report & file so that we can see it in database.
admin.site.register(Report)
admin.site.register(File)
