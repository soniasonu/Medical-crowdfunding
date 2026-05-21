import os
import sys
import django
from django.db import connection

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nypunya_worker_app.settings')
django.setup()

def add_columns():
    with connection.cursor() as cursor:
        try:
            print("Checking workers table columns...")
            cursor.execute("DESCRIBE workers")
            columns = [col[0] for col in cursor.fetchall()]
            
            if 'resume_edu' not in columns:
                print("Adding column 'resume_edu' to 'workers' table...")
                cursor.execute("ALTER TABLE workers ADD COLUMN resume_edu VARCHAR(500) NULL")
            else:
                print("'resume_edu' already exists.")
                
            if 'experience_cert' not in columns:
                print("Adding column 'experience_cert' to 'workers' table...")
                cursor.execute("ALTER TABLE workers ADD COLUMN experience_cert VARCHAR(500) NULL")
            else:
                print("'experience_cert' already exists.")
                
            print("Database update successful!")
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == "__main__":
    add_columns()
