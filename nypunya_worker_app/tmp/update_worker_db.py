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
            print("Checking workers table columns...")
            cursor.execute("DESCRIBE workers")
            columns = [col[0] for col in cursor.fetchall()]
            
            if 'availability' not in columns:
                print("Adding column 'availability' to 'workers' table...")
                cursor.execute("ALTER TABLE workers ADD COLUMN availability VARCHAR(50) DEFAULT 'active' NULL")
                print("Column added successfully!")
            else:
                print("'availability' already exists.")
                
            print("Database update successful!")
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == "__main__":
    update_db()
