from django.urls import path
from .views import homepage, upload_file, success_view

urlpatterns = [
    path("", homepage, name="home"),
    path("upload/", upload_file, name="upload_file"),
    path("success/", success_view, name="success_view"),  # This is for the success view
]
