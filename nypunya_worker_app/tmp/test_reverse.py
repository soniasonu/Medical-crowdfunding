import os
import sys
import django
from django.urls import reverse

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nypunya_worker_app.settings')
django.setup()

def check_reverse():
    try:
        url = reverse('admin_view_users')
        print(f"URL Reversed Successfully: {url}")
    except Exception as e:
        print(f"FAIL: {str(e)}")

if __name__ == "__main__":
    check_reverse()
