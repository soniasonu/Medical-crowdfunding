import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nypunya_worker_app.settings')
django.setup()

from nypunya.models import TrainingVideos

videos = TrainingVideos.objects.all()
for v in videos:
    original = v.file_path
    if v.file_path:
        # Remove any leading /media/ or media/
        if v.file_path.startswith('/media/'):
            v.file_path = v.file_path[7:]
        elif v.file_path.startswith('media/'):
            v.file_path = v.file_path[6:]
        
        # Also handle potential double slashes like /media//media/
        if v.file_path.startswith('/media/'):
             v.file_path = v.file_path[7:]
             
        if original != v.file_path:
            v.save()
            print(f"Cleaned video ID {v.training_video_id}: {original} -> {v.file_path}")

print("Database cleanup for training videos completed.")
