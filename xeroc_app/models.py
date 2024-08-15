from django.db import models

# Create your models here.

class UploadedFile(models.Model):
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)