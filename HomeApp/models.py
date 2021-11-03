from django.db import models

# Report Model
class Report(models.Model):
    id = models.AutoField(primary_key=True)
    link = models.TextField()
    csrfmiddlewaretoken = models.TextField()
    img_1 = models.ImageField(blank=True, null=True,upload_to = 'report_images')
    img_2 = models.ImageField(blank=True, null=True,upload_to = 'report_images')
    result = models.BooleanField(default = False)

    def __str__(self):
        return str(self.id)
