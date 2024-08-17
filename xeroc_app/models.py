from django.db import models

# Create your models here.

class UploadedFile(models.Model):
    user_name = models.CharField(max_length=255, default='Unknown')
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.file.name}"
    