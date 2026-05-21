import os
import sys
import django
from django.db import connection

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nypunya_worker_app.settings')
django.setup()

def check_data():
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT user_id, email FROM user_register LIMIT 10")
            for row in cursor.fetchall():
                print(f"User: {row[0]}, Email: {row[1]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
