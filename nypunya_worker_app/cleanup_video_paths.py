import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nypunya_worker_app.settings')
django.setup()

from nypunya.models import TrainingVideos

videos = TrainingVideos.objects.all()
for v in videos:
    if v.file_path and v.file_path.startswith('/media//media/'):
        v.file_path = v.file_path.replace('/media//media/', '/media/')
        v.save()
        print(f"Fixed double prefix (//) for video ID {v.training_video_id}")
    elif v.file_path and v.file_path.startswith('/media/media/'):
        v.file_path = v.file_path.replace('/media/media/', '/media/')
        v.save()
        print(f"Fixed double prefix for video ID {v.training_video_id}")
    elif v.file_path and v.file_path.startswith('media/media/'):
        v.file_path = v.file_path.replace('media/media/', 'media/')
        v.save()
        print(f"Fixed relative double prefix for video ID {v.training_video_id}")

print("Database cleanup for training videos completed.")
