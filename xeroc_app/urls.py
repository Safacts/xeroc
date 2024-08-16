from django.urls import path
from .views import homepage, upload_file, success_view, details, list_files_view, delete_file_view, download_file_view

urlpatterns = [
    path("", homepage, name="home"),
    path("upload/", upload_file, name="upload_file"),
    path("success/", success_view, name="success_view"),  # This is for the success view
    path("detail/",details, name="details"),
    path('files/', list_files_view, name='list_files'),
    path('delete-file/<str:file_name>/', delete_file_view, name='delete_file'),
     path('download-file/<str:file_name>/', download_file_view, name='download_file_view'),
]
