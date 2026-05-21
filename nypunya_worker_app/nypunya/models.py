from django.db import models


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, default='approved', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'category'


class Complaint(models.Model):
    complaint_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=50, blank=True, null=True)
    complaint_date = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, default='open', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'complaint'


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=50, blank=True, null=True)
    feedback_date = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feedback'


class FeedbackNltk(models.Model):
    feedback_nltk_id = models.AutoField(primary_key=True)
    agency_id = models.CharField(max_length=50, blank=True, null=True)
    positive_count = models.IntegerField(blank=True, null=True)
    negative_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feedback_nltk'


class Login(models.Model):
    admin_id = models.CharField(primary_key=True, max_length=50)
    password = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'login'


class OutSideWork(models.Model):
    out_side_work_id = models.AutoField(primary_key=True)
    worker_id = models.CharField(max_length=50, blank=True, null=True)
    user_id = models.CharField(max_length=50, blank=True, null=True)
    work_details = models.CharField(max_length=500, blank=True, null=True)
    request_date = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'out_side_work'


class RequestWork(models.Model):
    request_work_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=50, blank=True, null=True)
    request_date = models.CharField(max_length=50, blank=True, null=True)
    agency_id = models.CharField(max_length=50, blank=True, null=True)
    category_id = models.IntegerField(blank=True, null=True)
    work_description = models.CharField(max_length=50, blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    work_id = models.IntegerField(blank=True, null=True)
    agency_reply = models.CharField(max_length=500, blank=True, null=True)
    preferred_slot = models.CharField(max_length=100, blank=True, null=True)
    cancel_reason = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'request_work'


class WorkerAvailability(models.Model):
    availability_id = models.AutoField(primary_key=True)
    worker_id = models.CharField(max_length=50, blank=True, null=True)
    available_date = models.CharField(max_length=50, blank=True, null=True)
    time_slot = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, default='available')

    class Meta:
        managed = False
        db_table = 'worker_availability'


class TrainingVideos(models.Model):
    training_video_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'training_videos'


class VideoPayment(models.Model):
    video_payment_id = models.AutoField(primary_key=True)
    worker_id = models.CharField(max_length=50)
    training_video_id = models.IntegerField()
    amount = models.IntegerField()
    payment_date = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'video_payment'


class UserRegister(models.Model):
    user_id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    user_image = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_register'


class Agency(models.Model):
    agency_id = models.CharField(primary_key=True, max_length=50)
    category_id = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    register_no = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    agency_image = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'agency'


class Workers(models.Model):
    worker_id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    agency_id = models.CharField(max_length=50, blank=True, null=True)
    resume_edu = models.CharField(max_length=500, blank=True, null=True)
    experience_cert = models.CharField(max_length=500, blank=True, null=True)
    availability = models.CharField(max_length=50, default='active', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'workers'


class AssignWorker(models.Model):
    assign_id = models.AutoField(primary_key=True)
    request_work_id = models.IntegerField(blank=True, null=True)
    worker_id = models.CharField(max_length=50, blank=True, null=True)
    assign_date = models.CharField(max_length=50, blank=True, null=True)
    work_description = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'assign_worker'


class WorkerWorkCategory(models.Model):
    work_category_id = models.AutoField(primary_key=True)
    worker_id = models.CharField(max_length=50, default='0')
    category_id = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'worker_work_category'


class WorkPhotos(models.Model):
    work_photo_id = models.AutoField(primary_key=True)
    work_request_id = models.IntegerField(blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'work_photos'
class AgencyWork(models.Model):
    work_id = models.AutoField(primary_key=True)
    agency_id = models.CharField(max_length=50)
    category_id = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    work_image = models.CharField(max_length=500, null=True, blank=True)
    specifications = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'agency_work'


class UserImageUpload(models.Model):
    upload_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=50)
    image_path = models.CharField(max_length=500)
    upload_date = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'user_image_upload'
