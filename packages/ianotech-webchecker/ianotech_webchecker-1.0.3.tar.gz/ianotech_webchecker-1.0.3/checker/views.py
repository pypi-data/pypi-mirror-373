import requests
import time
from urllib.parse import urlparse
from django.shortcuts import render
from django.contrib import messages
from .forms import URLCheckForm
from .models import WebsiteCheck

def get_page_title(content):
    """Extract page title from HTML content"""
    try:
        import re
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
    except:
        pass
    return "No Title"

def generate_screenshot_url(url):
    """Generate screenshot URL using a free screenshot service"""
    try:
        # Using shot.screenshotapi.net (free service)
        # Alternative: https://htmlcsstoimage.com/demo_url or https://api.screenshotmachine.com
        encoded_url = requests.utils.quote(url, safe='')
        screenshot_url = f"https://shot.screenshotapi.net/screenshot?token=free&url={encoded_url}&width=1200&height=800&output=image&file_type=png&wait_for_event=load"
        return screenshot_url
    except:
        return ""

def check_website_status(url):
    """Check if a website is up or down quickly"""
    try:
        # Add protocol if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        start_time = time.time()
        
        # Quick check with shorter timeout
        response = requests.get(
            url, 
            timeout=5,  # Reduced timeout
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            allow_redirects=True
        )
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        status = 'up' if 200 <= response.status_code < 400 else 'down'
        
        # Get page title quickly
        page_title = "No Title"
        screenshot_url = ""
        
        if status == 'up':
            try:
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' in content_type and len(response.content) < 1000000:  # 1MB limit
                    page_title = get_page_title(response.text)
                
                # Generate screenshot URL (external service)
                screenshot_url = generate_screenshot_url(url)
            except:
                pass
        
        return {
            'status': status,
            'status_code': response.status_code,
            'response_time': response_time,
            'error_message': '',
            'page_title': page_title,
            'screenshot_url': screenshot_url
        }
        
    except requests.exceptions.Timeout:
        return {
            'status': 'down',
            'status_code': None,
            'response_time': None,
            'error_message': 'Connection timed out',
            'page_title': '',
            'screenshot_url': ''
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'down',
            'status_code': None,
            'response_time': None,
            'error_message': str(e),
            'page_title': '',
            'screenshot_url': ''
        }

def index(request):
    form = URLCheckForm()
    result = None
    
    if request.method == 'POST':
        form = URLCheckForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            
            check_result = check_website_status(url)

            website_check = WebsiteCheck.objects.create(
                url=url,
                status=check_result['status'],
                response_time=check_result['response_time'],
                status_code=check_result['status_code'],
                error_message=check_result['error_message'],
                page_title=check_result['page_title'],
                screenshot_url=check_result['screenshot_url']
            )
            
            result = {
                'url': url,
                'status': check_result['status'],
                'status_code': check_result['status_code'],
                'response_time': check_result['response_time'],
                'error_message': check_result['error_message'],
                'page_title': check_result['page_title'],
                'screenshot_url': check_result['screenshot_url']
            }
            
            # success/error message
            if check_result['status'] == 'up':
                messages.success(request, f"Website {url} is UP! ({check_result['response_time']}ms)")
            else:
                messages.error(request, f"Website {url} is DOWN!")
    
    return render(request, 'checker/index.html', {
        'form': form,
        'result': result
    })