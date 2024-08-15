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
            file_name = file.name
            file_size = file.size
            print(f"Uploading file: {file_name}, Size: {file_size} bytes")

            try:
                # Read file content
                file_content = file.read()
                print("File read successfully")

                # Upload file to Supabase storage
                response = supabase.storage.from_('files').upload(file_name, file_content)
                response_data = response.json()  # Convert response to JSON
                print(f"Supabase response: {response_data}")

                if response_data.get('error'):
                    print(f"Error uploading file: {response_data['error']}")
                    return render(request, 'home.html', {'form': form, 'error': response_data['error']})

                file_url = f"{SUPABASE_URL}/storage/v1/object/public/files/{file_name}"
                UploadedFile.objects.create(file_name=file_name, file_url=file_url)
                return redirect('success_view')
            except Exception as e:
                print(f"Exception during file upload: {e}")
                return render(request, 'home.html', {'form': form, 'error': str(e)})
    else:
        form = UploadFileForm()
    
    return render(request, 'home.html', {'form': form})