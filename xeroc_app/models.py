from django.db import models

# # Create your models here.

# class UploadedFile(models.Model):
#     user_name = models.CharField(max_length=255, default='Unknown')
#     file_name = models.CharField(max_length=255)
#     file_url = models.URLField()
#     file_size = models.PositiveIntegerField(default=0)  # Add default value here
#     uploaded_at = models.DateTimeField(auto_now_add=True)

    
#     def __str__(self):
#         return f"{self.user_name} - {self.file_name}"  # Use file_name instead of file

from django.db import models
from django.utils import timezone
import pytz

class PageView(models.Model):
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.count)
    
    
class UploadedFile(models.Model):
    user_name = models.CharField(max_length=255, default='Unknown')
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    file_size = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Convert the current time to IST
        ist = pytz.timezone('Asia/Kolkata')
        self.uploaded_at = timezone.now().astimezone(ist)
        super().save(*args, **kwargs)

    def __str__(self):
        ist = pytz.timezone('Asia/Kolkata')
        uploaded_at_ist = self.uploaded_at.astimezone(ist)
        return f"{self.user_name} - {self.file_name} - {uploaded_at_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}"

