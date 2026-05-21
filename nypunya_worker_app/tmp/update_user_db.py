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
            print("Checking user_register table columns...")
            cursor.execute("DESCRIBE user_register")
            columns = [col[0] for col in cursor.fetchall()]
            
            if 'user_image' not in columns:
                print("Adding column 'user_image' to 'user_register' table...")
                cursor.execute("ALTER TABLE user_register ADD COLUMN user_image VARCHAR(500) NULL")
                print("Column added successfully!")
            else:
                print("'user_image' already exists.")
                
            print("Database update successful!")
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == "__main__":
    update_db()
