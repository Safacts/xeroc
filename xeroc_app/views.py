from django.shortcuts import render, redirect
from supabase import create_client, Client
from .forms import UploadFileForm
from .models import UploadedFile
import os
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
import re

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


def sanitize_filename(filename):
    # Replace spaces with underscores and remove any special characters except periods and underscores
    filename = re.sub(r'[^\w\.\-]', '_', filename)
    return filename

@require_http_methods(["GET", "POST"])
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            user_name = form.cleaned_data['user_name'].lower()  # Get the user name from the form and make it lowercase
            original_file_name = file.name
            sanitized_file_name = sanitize_filename(original_file_name)
            file_size = file.size
            print(f"Uploading file: {original_file_name}, Size: {file_size} bytes, Uploaded by: {user_name}")

            # Create a new file name with the username as part of the path or name
            unique_file_name = f"{user_name}_{sanitized_file_name}"

            try:
                # Read file content
                file_content = file.read()
                print("File read successfully")

                # Upload file to Supabase storage
                response = supabase.storage.from_('flies').upload(unique_file_name, file_content)
                response_data = response.json()  # Convert response to JSON
                print(f"Supabase response: {response_data}")

                if response_data.get('error'):
                    print(f"Error uploading file: {response_data['error']}")
                    return render(request, 'home.html', {'form': form, 'error': response_data['error']})

                file_url = f"{SUPABASE_URL}/storage/v1/object/public/flies/{unique_file_name}"

                # Save the file information and user name in the database
                UploadedFile.objects.create(user_name=user_name, file_name=unique_file_name, file_url=file_url)
                return redirect('success_view')
            except Exception as e:
                print(f"Exception during file upload: {e}")
                return render(request, 'home.html', {'form': form, 'error': str(e)})
    else:
        form = UploadFileForm()
    
    return render(request, 'home.html', {'form': form})

def list_files_view(request):
    user_name = request.GET.get('user_name', '').lower()  # Get user name from query params
    try:
        response = supabase.storage.from_('flies').list()

        
        
        if isinstance(response, list):
            flies = response
        else:
            flies = []

        file_data = []
        for file in flies:
            file_data.append({'name': file['name'], 'url': f"{SUPABASE_URL}/storage/v1/object/public/flies/{file['name']}" })

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
    

def search_files_by_user(request):
    user_name = request.GET.get('user_name')
    files = UploadedFile.objects.filter(user_name__icontains=user_name)
    return render(request, 'files_list.html', {'files': files})