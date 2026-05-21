import os
import sys
import django
from django.db import connection

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nypunya_worker_app.settings')
django.setup()

def update_db():
    with connection.cursor() as cursor:
        try:
            print("Checking request_work table columns...")
            cursor.execute("DESCRIBE request_work")
            columns = [col[0] for col in cursor.fetchall()]
            
            if 'preferred_slot' not in columns:
                print("Adding column 'preferred_slot' to 'request_work' table...")
                cursor.execute("ALTER TABLE request_work ADD COLUMN preferred_slot VARCHAR(100) NULL")
                print("Column added successfully!")
            else:
                print("'preferred_slot' already exists.")
                
            print("Database update successful!")
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == "__main__":
    update_db()
