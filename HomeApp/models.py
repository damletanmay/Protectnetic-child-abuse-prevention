from django.db import models

# Report Model
class Report(models.Model):
    id = models.AutoField(primary_key=True)
    link = models.TextField()
    csrfmiddlewaretoken = models.TextField()
    img_1 = models.ImageField(default = None,blank=True, null=True,upload_to = 'report_images')
    img_2 = models.ImageField(default = None,blank=True, null=True,upload_to = 'report_images')
    zip = models.FileField(default = None,blank=True, null=True,upload_to = 'encrypted_zip_files')
    pdf_report = models.FileField(default = None, blank=True, null=True,upload_to = 'pdf_reports')
    result = models.BooleanField(default = False)

    def __str__(self):
        return str(self.id)

class File(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField(default = None, blank=True, null=True,upload_to = 'files')
    def __str__(self):
        return str(self.id)
