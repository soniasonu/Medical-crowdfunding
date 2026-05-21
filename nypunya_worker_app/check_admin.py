import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nypunya_worker_app.settings')
django.setup()

from nypunya.models import Login

try:
    admin = Login.objects.filter(admin_id='admin').first()
    if admin:
        print(f"Admin found: ID={admin.admin_id}, Password={admin.password}")
    else:
        print("Admin user 'admin' not found. Creating it for you...")
        Login.objects.create(admin_id='admin', password='admin')
        print("Admin user 'admin' with password 'admin' created successfully.")
except Exception as e:
    print(f"Error: {e}")
