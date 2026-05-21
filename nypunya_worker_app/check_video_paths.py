import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nypunya_worker_app.settings')
django.setup()

from nypunya.models import TrainingVideos

videos = TrainingVideos.objects.all()
for v in videos:
    print(f"ID: {v.training_video_id}, Path: {v.file_path}")
