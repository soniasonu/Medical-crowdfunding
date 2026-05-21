import os
import sys
import django
from django.db import connection

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nypunya_worker_app.settings')
django.setup()

def check_tables():
    with connection.cursor() as cursor:
        try:
            for table in ['user_register', 'feedback', 'workers', 'out_side_work', 'assign_worker']:
                print(f"\n--- Columns in {table} ---")
                cursor.execute(f"DESCRIBE {table}")
                for col in cursor.fetchall():
                    print(col)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_tables()
