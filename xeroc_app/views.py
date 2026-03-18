# from django.shortcuts import render, redirect
# from supabase import create_client, Client
# from .forms import UploadFileForm
# from .models import UploadedFile, PageView
# import os
# from django.http import JsonResponse, HttpResponse, Http404
# from django.views.decorators.http import require_http_methods
# import re
# from django.conf import settings
# import urllib.parse
# import logging

# from django.core.serializers import serialize

# from .models import UploadedFile

# logger = logging.getLogger(__name__)


# # Initialize Supabase client
# SUPABASE_URL = os.environ.get("SUPABASE_URL")
# SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# # Create your views here.
# def homepage(request):
#     if settings.COUNT_PAGE_VIEWS:
#         page_view, created = PageView.objects.get_or_create(pk=1)
#         page_view.count += 1
#         page_view.save()
#         view_count = page_view.count
#     else:
#         view_count = "Development mode: View count not tracked."

#     context = {'view_count': view_count}
#     return render(request, 'home.html', context)

# def success_view(request):
#     return render(request, 'success.html')


# def details(request):
#     files = UploadedFile.objects.all().order_by('-uploaded_at')  # Sorted by uploaded_at in descending order
#     return render(request, 'files.html', {'files': files})

# def password(request):
#     return render(request, 'password.html')

# def sanitize_filename(filename):
#     # Replace spaces with underscores and remove any special characters except periods and underscores
#     filename = re.sub(r'[^\w\.\-]', '_', filename)
#     return filename

# @require_http_methods(["GET", "POST"])
# def upload_file(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             file = request.FILES['file']
#             user_name = form.cleaned_data['user_name'].strip().lower()  # Trim spaces and make it lowercase
#             user_name = re.sub(r'\s+', '_', user_name)  # Replace spaces with underscores
            
#             original_file_name = file.name
#             sanitized_file_name = sanitize_filename(original_file_name)
#             file_size = file.size

#             if not file_size:  # Check if file_size is available
#                 return JsonResponse({'success': False, 'error': 'File size is missing'})
            
#             print(f"Uploading file: {original_file_name}, Size: {file_size} bytes, Uploaded by: {user_name}")

#             # Create a new file name with the username as part of the path or name
#             unique_file_name = f"{user_name}_{sanitized_file_name}"
#             unique_file_name = urllib.parse.quote(unique_file_name)  # URL-encode the file name

#             try:
#                 # Read file content
#                 file_content = file.read()
#                 content_type = file.content_type
#                 print("File read successfully")

#                 # Upload file to Supabase storage
#                 response = supabase.storage.from_('flies').upload(unique_file_name, file_content, {
#                     'content-type': content_type
#                 })
#                 response_data = response.json()  # Convert response to JSON
#                 print(f"Supabase response: {response_data}")

#                 if response_data.get('error'):
#                     print(f"Error uploading file: {response_data['error']}")
#                     return JsonResponse({'success': False, 'error': response_data['error']})

#                 file_url = f"{SUPABASE_URL}/storage/v1/object/public/flies/{unique_file_name}"

#                 # Save the file information and user name in the database
#                 UploadedFile.objects.create(user_name=user_name, file_name=unique_file_name, file_url=file_url, file_size=file_size)
                
#                 # Return file_url in the response
#                 return JsonResponse({'success': True, 'file_url': file_url})
#             except Exception as e:
#                 print(f"Exception during file upload: {e}")
#                 return JsonResponse({'success': False, 'error': str(e)})
#         return JsonResponse({'success': False, 'error': 'Invalid request method'})
#     else:
#         form = UploadFileForm()
    
#     return render(request, 'home.html', {'form': form})

# def list_files_view(request):
#     user_name = request.GET.get('user_name', '').lower()  # Get user name from query params.
#     try:
#         response = supabase.storage.from_('flies').list()

        
        
#         if isinstance(response, list):
#             flies = response
#         else:
#             flies = []

#         file_data = []
#         for file in flies:
#             file_data.append({'name': file['name'], 'url': f"{SUPABASE_URL}/storage/v1/object/public/flies/{file['name']}" })

#         return JsonResponse(file_data, safe=False)
#     except Exception as e:
#         print(f"Exception during listing flies: {e}")
#         return JsonResponse({'error': str(e)}, status=500)
    

# from django.http import JsonResponse
# from .models import UploadedFile

# def confirm_upload(request):
#     """
#     Confirm if a file URL exists in the database.
    
#     Args:
#     request (HttpRequest): The incoming request object.
    
#     Returns:
#     JsonResponse: A JSON response with success status and error message (if any).
#     """

#     file_url = request.GET.get('file_url')
#     print(f"Received file_url: {file_url}")  # Debug print

#     if not file_url:
#         return JsonResponse({'success': False, 'error': 'File URL is missing'})

#     try:
#         file_record = UploadedFile.objects.get(file_url=file_url)
#         print(f"File record found: {file_record}")  # Debug print
#         return JsonResponse({'success': True})
#     except UploadedFile.DoesNotExist:
#         print("File not found in the database")  # Debug print
#         return JsonResponse({'success': False, 'error': 'File not uploaded to the database'})
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")  # Debug print
#         return JsonResponse({'success': False, 'error': 'An unexpected error occurred'})


 
# def delete_file_view(request, file_name):
#     response = supabase.storage.from_('flies').remove([file_name])
#     if response.get('error'):
#         return JsonResponse({'error': response['error']}, status=400)
#     return JsonResponse({'message': 'File deleted successfully'})

# def download_file_view(request, file_name):
#     try:
#         file_url = f"{SUPABASE_URL}/storage/v1/object/public/flies/{file_name}"
#         response = supabase.storage.from_('flies').download(file_name)
#         if response.status_code == 200:
#             content_type = 'application/pdf' if file_name.endswith('.pdf') else 'application/octet-stream'
#             response = HttpResponse(response.content, content_type=content_type)
#             response['Content-Disposition'] = f'inline; filename="{file_name}"'
#             response['X-Frame-Options'] = 'SAMEORIGIN'  # Allow embedding in iframes
#             return response
#         else:
#             return JsonResponse({'error': 'File not found'}, status=404)
#     except Exception as e:
#         print(f"Exception during file download: {e}")
#         return JsonResponse({'error': str(e)}, status=500)
    
# def search_files_by_user(request):
#     user_name = request.GET.get('user_name', '').strip().lower()
#     user_name = re.sub(r'\s+', '_', user_name)  # Replace spaces with underscores
#     files = UploadedFile.objects.filter(user_name__icontains=user_name)
#     return render(request, 'files_list.html', {'files': files})



# def list_files_view(request):
#     # Retrieve and order files by uploaded_at
#     files = UploadedFile.objects.all().order_by('-uploaded_at')

#     # Prepare the data for the frontend
#     files_data = [{
#         'name': file.file_name,
#         'url': file.file_url,
#         'uploaded_at': int(file.uploaded_at.timestamp() * 1000),  # Convert to milliseconds
#     } for file in files]

#     return JsonResponse(files_data, safe=False)
import os
import re
import json
import requests
import urllib.parse
import traceback
import logging

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.serializers import serialize

from supabase import create_client, Client

from .forms import UploadFileForm
from .models import UploadedFile, PageView

logger = logging.getLogger(__name__)

# ==========================================
# SUPABASE & WEBHOOK CONFIGURATION
# ==========================================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")

# Print pricing & allowed formats
ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
PRICE_BW = 3
PRICE_COLOR = 10


# ==========================================
# EXISTING DJANGO VIEWS (Web App)
# ==========================================
def homepage(request):
    if getattr(settings, 'COUNT_PAGE_VIEWS', False):
        page_view, created = PageView.objects.get_or_create(pk=1)
        page_view.count += 1
        page_view.save()
        view_count = page_view.count
    else:
        view_count = "Development mode: View count not tracked."

    context = {'view_count': view_count}
    return render(request, 'home.html', context)

def success_view(request):
    return render(request, 'success.html')

def details(request):
    files = UploadedFile.objects.all().order_by('-uploaded_at')
    return render(request, 'files.html', {'files': files})

def password(request):
    return render(request, 'password.html')

def sanitize_filename(filename):
    # Replace spaces with underscores and remove special characters except periods/underscores
    filename = re.sub(r'[^\w\.\-]', '_', filename)
    return filename

@require_http_methods(["GET", "POST"])
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            user_name = form.cleaned_data['user_name'].strip().lower()
            user_name = re.sub(r'\s+', '_', user_name)
            
            original_file_name = file.name
            sanitized_file_name = sanitize_filename(original_file_name)
            file_size = file.size

            if not file_size:
                return JsonResponse({'success': False, 'error': 'File size is missing'})
            
            print(f"Uploading file: {original_file_name}, Size: {file_size} bytes, Uploaded by: {user_name}")

            unique_file_name = f"{user_name}_{sanitized_file_name}"
            unique_file_name = urllib.parse.quote(unique_file_name)

            try:
                file_content = file.read()
                content_type = file.content_type
                
                response = supabase.storage.from_('flies').upload(unique_file_name, file_content, {
                    'content-type': content_type
                })
                response_data = response.json()

                if response_data.get('error'):
                    return JsonResponse({'success': False, 'error': response_data['error']})

                file_url = f"{SUPABASE_URL}/storage/v1/object/public/flies/{unique_file_name}"
                UploadedFile.objects.create(user_name=user_name, file_name=unique_file_name, file_url=file_url, file_size=file_size)
                
                return JsonResponse({'success': True, 'file_url': file_url})
            except Exception as e:
                print(f"Exception during file upload: {e}")
                return JsonResponse({'success': False, 'error': str(e)})
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    else:
        form = UploadFileForm()
    
    return render(request, 'home.html', {'form': form})

def list_files_view(request):
    files = UploadedFile.objects.all().order_by('-uploaded_at')
    files_data = [{
        'name': file.file_name,
        'url': file.file_url,
        'uploaded_at': int(file.uploaded_at.timestamp() * 1000),
    } for file in files]
    return JsonResponse(files_data, safe=False)

def confirm_upload(request):
    file_url = request.GET.get('file_url')
    if not file_url:
        return JsonResponse({'success': False, 'error': 'File URL is missing'})

    try:
        file_record = UploadedFile.objects.get(file_url=file_url)
        return JsonResponse({'success': True})
    except UploadedFile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'File not uploaded to the database'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An unexpected error occurred'})

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
            response_obj = HttpResponse(response.content, content_type=content_type)
            response_obj['Content-Disposition'] = f'inline; filename="{file_name}"'
            response_obj['X-Frame-Options'] = 'SAMEORIGIN'
            return response_obj
        else:
            return JsonResponse({'error': 'File not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def search_files_by_user(request):
    user_name = request.GET.get('user_name', '').strip().lower()
    user_name = re.sub(r'\s+', '_', user_name)
    files = UploadedFile.objects.filter(user_name__icontains=user_name)
    return render(request, 'files_list.html', {'files': files})


# ==========================================
# TELEGRAM BOT WEBHOOK (The Magic)
# ==========================================
@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        try:
            update = json.loads(request.body.decode('utf-8'))
            
            print("\n" + "="*50, flush=True)
            print("INCOMING WEBHOOK TRIGGERED!", flush=True)
            print("="*50 + "\n", flush=True)

            # --- SCENARIO 1: BUTTON CLICK ---
            if 'callback_query' in update:
                query = update['callback_query']
                callback_id = query.get('id')
                chat_id = query.get('message', {}).get('chat', {}).get('id')
                message_id = query.get('message', {}).get('message_id')
                data = query.get('data', '')
                
                print(f"🔘 BUTTON CLICKED: {data}", flush=True)

                # Stop the spinner
                ack_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
                requests.post(ack_url, json={"callback_query_id": callback_id})

                if data == "ignore":
                    return JsonResponse({"status": "ok"})

                # Extract File Name
                text = query.get('message', {}).get('text', '')
                file_name = "Unknown_File"
                if "📄 File:" in text:
                    try:
                        file_name = text.split("📄 File:")[1].split('\n')[0].strip()
                    except:
                        pass

                # Handle Color Selection -> Show Dial
                if data.startswith("set_"):
                    mode = data.split("_")[1] 
                    copies = 1 
                    price_per_page = PRICE_BW if mode == 'bw' else PRICE_COLOR
                    mode_name = "Black & White" if mode == 'bw' else "Color"
                    total_price = price_per_page * copies
                    
                    keyboard = {"inline_keyboard": [
                        [{"text": "➖", "callback_data": f"ignore"}, {"text": f"{copies} Copies", "callback_data": "ignore"}, {"text": "➕", "callback_data": f"adj_{mode}_{copies + 1}"}],
                        [{"text": "🔙 Back", "callback_data": "back_to_start"}, {"text": f"🖨️ Print (₹{total_price})", "callback_data": f"prt_{mode}_{copies}"}]
                    ]}
                    
                    edit_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
                    resp = requests.post(edit_url, json={
                        "chat_id": chat_id, "message_id": message_id,
                        "text": f"📄 File: {file_name}\n🎨 Mode: {mode_name} (₹{price_per_page}/page)\n\nUse the dial to set copies:", "reply_markup": keyboard
                    })
                    print(f"🔄 Edit Response: {resp.status_code} | {resp.text}", flush=True)

                # Handle Dial Adjustment
                elif data.startswith("adj_"):
                    parts = data.split("_")
                    mode = parts[1]
                    copies = int(parts[2])
                    price_per_page = PRICE_BW if mode == 'bw' else PRICE_COLOR
                    mode_name = "Black & White" if mode == 'bw' else "Color"
                    total_price = price_per_page * copies
                    
                    minus_btn = f"adj_{mode}_{copies - 1}" if copies > 1 else "ignore"
                    
                    keyboard = {"inline_keyboard": [
                        [{"text": "➖", "callback_data": minus_btn}, {"text": f"{copies} Copies", "callback_data": "ignore"}, {"text": "➕", "callback_data": f"adj_{mode}_{copies + 1}"}],
                        [{"text": "🔙 Back", "callback_data": "back_to_start"}, {"text": f"🖨️ Print (₹{total_price})", "callback_data": f"prt_{mode}_{copies}"}]
                    ]}
                    
                    edit_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
                    requests.post(edit_url, json={
                        "chat_id": chat_id, "message_id": message_id,
                        "text": f"📄 File: {file_name}\n🎨 Mode: {mode_name} (₹{price_per_page}/page)\n\nUse the dial to set copies:", "reply_markup": keyboard
                    })

                # Handle Back Button
                elif data == "back_to_start":
                    keyboard = {"inline_keyboard": [[{"text": "🔲 Black & White (₹3/page)", "callback_data": "set_bw"}], [{"text": "🎨 Color Format (₹10/page)", "callback_data": "set_co"}]]}
                    edit_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
                    requests.post(edit_url, json={
                        "chat_id": chat_id, "message_id": message_id,
                        "text": f"📄 File: {file_name}\n\nStep 1: Choose color format.", "reply_markup": keyboard
                    })

                # Handle Print Trigger (n8n)
                elif data.startswith("prt_"):
                    parts = data.split("_")
                    mode = "Color" if parts[1] == 'co' else "B&W"
                    copies = int(parts[2])
                    total_price = (PRICE_COLOR if mode == "Color" else PRICE_BW) * copies
                    
                    print(f"🚀 Firing to n8n Webhook: {N8N_WEBHOOK_URL}", flush=True)
                    if N8N_WEBHOOK_URL:
                        requests.post(N8N_WEBHOOK_URL, json={
                            "file_name": file_name, "color": mode, "copies": copies, "total_price": total_price
                        })
                    
                    receipt_text = f"✅ Sent to printer!\n\n📄 File: {file_name}\n🎨 Mode: {mode}\n🖨️ Copies: {copies}\n💰 Total: ₹{total_price}\n\nPlease collect at the counter."
                    edit_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
                    requests.post(edit_url, json={"chat_id": chat_id, "message_id": message_id, "text": receipt_text})

                return JsonResponse({"status": "ok"})

            # --- SCENARIO 2: FILE UPLOAD ---
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                file_name = None
                is_valid = False

                if 'document' in update['message']:
                    file_name = update['message']['document'].get('file_name', 'unknown_file')
                    ext = file_name.split('.')[-1].lower() if '.' in file_name else ''
                    if ext in ALLOWED_EXTENSIONS: is_valid = True
                elif 'photo' in update['message']:
                    file_name = "uploaded_image.jpg"
                    is_valid = True

                if is_valid:
                    print("📥 FILE RECEIVED! Sending Menu...", flush=True)
                    keyboard = {"inline_keyboard": [[{"text": "🔲 Black & White (₹3/page)", "callback_data": "set_bw"}], [{"text": "🎨 Color Format (₹10/page)", "callback_data": "set_co"}]]}
                    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                    
                    # Capture Telegram API Response
                    resp = requests.post(url, json={
                        "chat_id": chat_id, "text": f"📄 File: {file_name}\n\nStep 1: Choose color format.", "reply_markup": keyboard
                    })
                    print(f"🚀 TELEGRAM API RESPONSE: {resp.status_code} | {resp.text}", flush=True)

                elif 'document' in update['message'] or 'photo' in update['message']:
                    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                    requests.post(url, json={"chat_id": chat_id, "text": "❌ Invalid format. Upload PDF, Word, or Image."})

            return JsonResponse({"status": "ok"})
            
        except Exception as e:
            print(f"❌ CRITICAL PYTHON CRASH: {e}", flush=True)
            print(traceback.format_exc(), flush=True)
            return JsonResponse({"status": "error"}, status=500)
            
    return JsonResponse({"status": "invalid request"}, status=400)



def send_whatsapp_message(to, message):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

    payload = {
        "From": "whatsapp:+14155238886",  # Twilio sandbox number
        "To": to,
        "Body": message
    }

    response = requests.post(url, data=payload, auth=(account_sid, auth_token))
    print("📤 Twilio Response:", response.status_code, response.text, flush=True)




@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "POST":
        try:
            data = request.POST

            print("\n===== WHATSAPP WEBHOOK HIT =====", flush=True)
            print(data, flush=True)

            from_number = data.get("From")  # user number
            message_body = data.get("Body", "").strip()
            media_url = data.get("MediaUrl0")
            media_type = data.get("MediaContentType0")

            print(f"From: {from_number}", flush=True)
            print(f"Message: {message_body}", flush=True)
            print(f"Media: {media_url}", flush=True)

            # ==========================================
            # CASE 1: FILE RECEIVED
            # ==========================================
            if media_url:
                file_name = media_url.split("/")[-1]

                reply = (
                    f"📄 File received!\n\n"
                    f"Choose print type:\n"
                    f"1️⃣ Black & White (₹3/page)\n"
                    f"2️⃣ Color (₹10/page)\n\n"
                    f"Reply with 1 or 2"
                )

                send_whatsapp_message(from_number, reply)

                return HttpResponse("OK")

            # ==========================================
            # CASE 2: USER REPLY (1 or 2)
            # ==========================================
            if message_body in ["1", "2"]:
                mode = "B&W" if message_body == "1" else "Color"
                price = PRICE_BW if mode == "B&W" else PRICE_COLOR

                # 🔥 Send to n8n
                if N8N_WEBHOOK_URL:
                    requests.post(N8N_WEBHOOK_URL, json={
                        "user": from_number,
                        "color": mode,
                        "copies": 1,
                        "total_price": price
                    })

                reply = (
                    f"✅ Sent to printer!\n\n"
                    f"🎨 Mode: {mode}\n"
                    f"🖨️ Copies: 1\n"
                    f"💰 Price: ₹{price}\n\n"
                    f"Collect at counter."
                )

                send_whatsapp_message(from_number, reply)

                return HttpResponse("OK")

            # ==========================================
            # DEFAULT RESPONSE
            # ==========================================
            send_whatsapp_message(
                from_number,
                "Send a file to start printing 📄"
            )

            return HttpResponse("OK")

        except Exception as e:
            print("❌ ERROR:", str(e), flush=True)
            print(traceback.format_exc(), flush=True)
            return HttpResponse("ERROR", status=500)

    return HttpResponse("Invalid", status=400)