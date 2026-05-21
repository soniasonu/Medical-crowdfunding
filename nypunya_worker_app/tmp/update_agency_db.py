import os
import sys
import django
from django.db import connection

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nypunya_worker_app.settings')
django.setup()

def add_agency_image_column():
    with connection.cursor() as cursor:
        try:
            print("Checking agency table columns...")
            cursor.execute("DESCRIBE agency")
            columns = [col[0] for col in cursor.fetchall()]
            
            if 'agency_image' not in columns:
                print("Adding column 'agency_image' to 'agency' table...")
                cursor.execute("ALTER TABLE agency ADD COLUMN agency_image VARCHAR(500) NULL")
                print("Column added successfully!")
            else:
                print("'agency_image' already exists.")
                
            print("Database update successful!")
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == "__main__":
    add_agency_image_column()
