import os
import sys
import django
from django.urls import get_resolver

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nypunya_worker_app.settings')
django.setup()

def check_urls():
    resolver = get_resolver()
    for name in resolver.reverse_dict.keys():
        if isinstance(name, str) and 'admin_view_users' in name:
            print(f"URL found: {name}")
            return
    print("URL 'admin_view_users' NOT found in resolver!")

if __name__ == "__main__":
    check_urls()
