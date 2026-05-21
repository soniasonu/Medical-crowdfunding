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
            print("Creating agency_work table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agency_work (
                    work_id INT AUTO_INCREMENT PRIMARY KEY,
                    agency_id VARCHAR(50),
                    category_id INT,
                    title VARCHAR(200),
                    description VARCHAR(500),
                    price DECIMAL(10, 2),
                    work_image VARCHAR(500),
                    specifications TEXT
                )
            """)
            print("Table 'agency_work' created successfully!")
        except Exception as e:
            print(f"Error creating table: {e}")

if __name__ == "__main__":
    update_db()
