from django.shortcuts import render, redirect
from supabase import create_client, Client
from .forms import UploadFileForm
from .models import UploadedFile
import os
from django.http import JsonResponse, HttpResponse, Http404

# Initialize Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create your views here.
def homepage(request):
    return render(request, 'home.html')

def success_view(request):
    return render(request, 'success.html')


def details(request):
    return render(request, 'files.html')


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
                response = supabase.storage.from_('flies').upload(file_name, file_content)
                response_data = response.json()  # Convert response to JSON
                print(f"Supabase response: {response_data}")

                if response_data.get('error'):
                    print(f"Error uploading file: {response_data['error']}")
                    return render(request, 'home.html', {'form': form, 'error': response_data['error']})

                file_url = f"{SUPABASE_URL}/storage/v1/object/public/flies/{file_name}"
                UploadedFile.objects.create(file_name=file_name, file_url=file_url)
                return redirect('success_view')
            except Exception as e:
                print(f"Exception during file upload: {e}")
                return render(request, 'home.html', {'form': form, 'error': str(e)})
    else:
        form = UploadFileForm()
    
    return render(request, 'home.html', {'form': form})

def list_files_view(request):
    try:
        response = supabase.storage.from_('flies').list()
        if isinstance(response, list):
            flies = response
        else:
            flies = []

        file_data = []
        for file in flies:
            file_data.append({'name': file['name'], 'url': f"{SUPABASE_URL}/storage/v1/object/public/flies/{file['name']}"})

        return JsonResponse(file_data, safe=False)
    except Exception as e:
        print(f"Exception during listing flies: {e}")
        return JsonResponse({'error': str(e)}, status=500)
 
def delete_file_view(request, file_name):
    response = supabase.storage.from_('flies').remove([file_name])
    if response.get('error'):
        return JsonResponse({'error': response['error']}, status=400)
    return JsonResponse({'message': 'File deleted successfully'})

def download_file_view(request, file_name):
    try:
        file_url = f"{SUPABASE_URL}/storage/v1/object/public/flies/{file_name}"
        response = supabase.storage.from_('flies').download(file_name)
        if response.status_code == 200:
            content_type = 'application/pdf' if file_name.endswith('.pdf') else 'application/octet-stream'
            response = HttpResponse(response.content, content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{file_name}"'
            response['X-Frame-Options'] = 'SAMEORIGIN'  # Allow embedding in iframes
            return response
        else:
            return JsonResponse({'error': 'File not found'}, status=404)
    except Exception as e:
        print(f"Exception during file download: {e}")
        return JsonResponse({'error': str(e)}, status=500)
