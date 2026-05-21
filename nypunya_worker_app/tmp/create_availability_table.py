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
            print("Creating worker_availability table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS worker_availability (
                    availability_id INT AUTO_INCREMENT PRIMARY KEY,
                    worker_id VARCHAR(50),
                    available_date VARCHAR(50),
                    time_slot VARCHAR(50),
                    status VARCHAR(50) DEFAULT 'available'
                )
            """)
            print("Table 'worker_availability' created successfully!")
        except Exception as e:
            print(f"Error creating table: {e}")

if __name__ == "__main__":
    update_db()
