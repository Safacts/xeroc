from django.shortcuts import render, redirect
from supabase import create_client, Client
from .forms import UploadFileForm
from .models import UploadedFile
import os
from django.http import JsonResponse

# Initialize Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create your views here.
def homepage(request):
    return render(request, 'home.html')

def success_view(request):
    return render(request, 'success.html')


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            # Upload file to Supabase storage
            file_name = file.name
            response = supabase.storage().from_('your-bucket').upload(file_name, file.read())
            
            if response.get('error'):
                return render(request, 'home.html', {'form': form, 'error': response['error']})
            
            file_url = f"{SUPABASE_URL}/storage/v1/object/public/your-bucket/{file_name}"
            UploadedFile.objects.create(file_name=file_name, file_url=file_url)
            return redirect('success_view')  # Define your success view
    else:
        form = UploadFileForm()
    
    return render(request, 'syccess.html', {'form': form})
