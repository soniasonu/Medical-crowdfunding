from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from nypunya.models import (
    Category, Complaint, Feedback, FeedbackNltk, Login,
    OutSideWork, RequestWork, TrainingVideos, UserRegister,
    Agency, Workers, AssignWorker, WorkerWorkCategory, WorkPhotos, AgencyWork, WorkerAvailability, VideoPayment, UserImageUpload,
)
from nypunya.services.nlp_feedback import get_sentiment, update_feedback_nltk_for_agency
from nypunya.services.chat_ml import get_response_rnn as chat_get_response_rnn
from django.db.models import Sum, Count, Avg
from django.core.files.storage import FileSystemStorage
import razorpay
import re
import traceback


RAZORPAY_CLIENT = razorpay.Client(auth=("rzp_test_SROSnyInFv81S4", "WIWYANkTTLg7iGbFgEbwj4BM"))


def _require_role(request, *allowed):
    if not request.session.get('user_id'):
        return False
    return request.session.get('role') in allowed


def home(request):
    if request.session.get('user_id'):
        return redirect('dashboard')
    return render(request, 'index.html')


def login_view(request):
    if request.method != 'POST':
        return render(request, 'login.html')
    role = request.POST.get('role')
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    if not role or not username or not password:
        messages.error(request, 'Fill all fields.')
        return render(request, 'login.html')
    if role == 'admin':
        try:
            admin = Login.objects.get(admin_id=username, password=password)
            request.session['user_id'] = admin.admin_id
            request.session['role'] = 'admin'
            request.session['user_name'] = admin.admin_id
            return redirect('dashboard')
        except Login.DoesNotExist:
            messages.error(request, 'Invalid admin ID or password.')
    elif role == 'agency':
        try:
            agency = Agency.objects.get(agency_id=username, password=password)
            if (agency.status or '').lower() != 'approved':
                messages.error(request, 'Agency not approved yet.')
                return render(request, 'login.html')
            request.session['user_id'] = agency.agency_id
            request.session['role'] = 'agency'
            request.session['user_name'] = agency.name or agency.agency_id
            return redirect('dashboard')
        except Agency.DoesNotExist:
            messages.error(request, 'Invalid agency ID or password.')
    elif role == 'worker':
        try:
            worker = Workers.objects.get(worker_id=username, password=password)
            request.session['user_id'] = worker.worker_id
            request.session['role'] = 'worker'
            request.session['user_name'] = worker.name or worker.worker_id
            return redirect('dashboard')
        except Workers.DoesNotExist:
            messages.error(request, 'Invalid worker ID or password.')
    elif role == 'user':
        try:
            user = UserRegister.objects.get(user_id=username, password=password)
            request.session['user_id'] = user.user_id
            request.session['role'] = 'user'
            request.session['user_name'] = user.name or user.user_id
            return redirect('dashboard')
        except UserRegister.DoesNotExist:
            messages.error(request, 'Invalid user ID or password.')
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('home')


def register_select(request):
    return render(request, 'register_select.html')


def register_user_view(request):
    if request.method != 'POST':
        return render(request, 'register_user.html')
    user_id = request.POST.get('user_id', '').strip()
    password = request.POST.get('password', '')
    confirm = request.POST.get('confirm_password', '')
    if password != confirm:
        messages.error(request, 'Passwords do not match.')
        return render(request, 'register_user.html')
    if UserRegister.objects.filter(user_id=user_id).exists():
        messages.error(request, 'User ID already exists.')
        return render(request, 'register_user.html')
    # Handle Profile Image
    user_img_url = None
    if 'user_image' in request.FILES:
        from django.core.files.storage import FileSystemStorage
        fs = FileSystemStorage()
        img = request.FILES['user_image']
        filename = fs.save(f'user_pics/{user_id}_{img.name}', img)
        user_img_url = fs.url(filename)

    UserRegister.objects.create(
        user_id=user_id,
        name=request.POST.get('name', ''),
        address=request.POST.get('address', ''),
        email=request.POST.get('email', ''),
        phone=request.POST.get('phone', ''),
        password=password,
        user_image=user_img_url,
    )
    messages.success(request, 'Registered. You can login now.')
    return redirect('login')


def register_agency_view(request):
    categories = Category.objects.all()
    if request.method != 'POST':
        return render(request, 'register_agency.html', {'categories': categories})
    agency_id = request.POST.get('agency_id', '').strip()
    password = request.POST.get('password', '')
    confirm = request.POST.get('confirm_password', '')
    if password != confirm:
        messages.error(request, 'Passwords do not match.')
        return render(request, 'register_agency.html', {'categories': categories})
    if Agency.objects.filter(agency_id=agency_id).exists():
        messages.error(request, 'Agency ID already exists.')
        return render(request, 'register_agency.html', {'categories': categories})
    # Handle Profile Picture upload
    fs = FileSystemStorage()
    image_path = ""
    if 'agency_image' in request.FILES:
        img = request.FILES['agency_image']
        filename = fs.save(f'agency_pics/{agency_id}_{img.name}', img)
        image_path = fs.url(filename)

    Agency.objects.create(
        agency_id=agency_id,
        category_id=request.POST.get('category_id', ''),
        name=request.POST.get('name', ''),
        address=request.POST.get('address', ''),
        register_no=request.POST.get('register_no', ''),
        phone=request.POST.get('phone', ''),
        email=request.POST.get('email', ''),
        password=password,
        status='pending',
        agency_image=image_path,
    )
    messages.success(request, 'Agency registered. Wait for admin approval.')
    return redirect('login')


def register_worker_view(request):
    categories = Category.objects.filter(status__iexact='approved')
    agencies = Agency.objects.filter(status__iexact='approved')
    if request.method != 'POST':
        return render(request, 'register_worker.html', {'categories': categories, 'agencies': agencies})
    worker_id = request.POST.get('worker_id', '').strip()
    category_id = request.POST.get('category_id', '')
    password = request.POST.get('password', '')
    confirm = request.POST.get('confirm_password', '')
    if password != confirm:
        messages.error(request, 'Passwords do not match.')
        return render(request, 'register_worker.html', {'categories': categories, 'agencies': agencies})
    if Workers.objects.filter(worker_id=worker_id).exists():
        messages.error(request, 'Worker ID already exists.')
        return render(request, 'register_worker.html', {'categories': categories, 'agencies': agencies})
    # Handle File Uploads
    fs = FileSystemStorage()
    resume_path = ""
    if 'resume_edu' in request.FILES:
        rf = request.FILES['resume_edu']
        filename = fs.save(f'worker_docs/{worker_id}_resume_{rf.name}', rf)
        resume_path = fs.url(filename)
    
    exp_path = ""
    if 'experience_cert' in request.FILES:
        ef = request.FILES['experience_cert']
        filename = fs.save(f'worker_docs/{worker_id}_exp_{ef.name}', ef)
        exp_path = fs.url(filename)

    w = Workers.objects.create(
        worker_id=worker_id,
        name=request.POST.get('name', ''),
        address=request.POST.get('address', ''),
        phone=request.POST.get('phone', ''),
        email=request.POST.get('email', ''),
        password=password,
        status='pending',
        agency_id=request.POST.get('agency_id', ''),
        resume_edu=resume_path,
        experience_cert=exp_path,
    )
    WorkerWorkCategory.objects.create(worker_id=worker_id, category_id=int(category_id) if category_id else 0)
    messages.success(request, 'Worker registered with documents. Wait for agency approval.')
    return redirect('login')


def dashboard(request):
    if not request.session.get('user_id'):
        return redirect('login')
    role = request.session.get('role')
    if role == 'admin':
        return _dashboard_admin(request)
    if role == 'agency':
        return _dashboard_agency(request)
    if role == 'worker':
        return _dashboard_worker(request)
    if role == 'user':
        return _dashboard_user(request)
    return redirect('login')


def _dashboard_admin(request):
    categories = Category.objects.filter(status__iexact='approved')
    # Booking stats for live graphical representation
    booking_stats = []
    for cat in categories:
        count = RequestWork.objects.filter(category_id=cat.category_id).count()
        booking_stats.append({'label': cat.name, 'value': count})
        
    agencies_pending = Agency.objects.filter(status__iexact='pending')
    agencies_approved = Agency.objects.filter(status__iexact='approved')
    complaints = Complaint.objects.all().order_by('-complaint_id')[:50]
    feedback_nltk = FeedbackNltk.objects.all()
    feedback_list = Feedback.objects.all().order_by('-feedback_id')[:30]
    ctx = {
        'categories': categories,
        'booking_stats': booking_stats,
        'agencies_pending': agencies_pending,
        'agencies_approved': agencies_approved,
        'complaints': complaints,
        'feedback_nltk': feedback_nltk,
        'feedback_list': feedback_list,
    }
    return render(request, 'dashboard_admin.html', ctx)


def admin_view_categories(request):
    if not _require_role(request, 'admin'):
        return redirect('login')
    pending = Category.objects.filter(status__iexact='pending')
    approved = Category.objects.filter(status__iexact='approved')
    return render(request, 'admin_view_categories.html', {
        'categories_pending': pending, 
        'categories_approved': approved
    })


def admin_view_agencies(request):
    if not _require_role(request, 'admin'):
        return redirect('login')
    agencies_pending = Agency.objects.filter(status__iexact='pending')
    agencies_approved = Agency.objects.filter(status__iexact='approved')
    agencies_blocked = Agency.objects.filter(status__iexact='blocked')
    
    return render(request, 'admin_view_agencies.html', {
        'agencies_pending': agencies_pending,
        'agencies_approved': agencies_approved,
        'agencies_blocked': agencies_blocked
    })


def admin_view_users(request):
    if not _require_role(request, 'admin'):
        return redirect('login')
    users = UserRegister.objects.all()
    return render(request, 'admin_view_users.html', {'users': users})


def admin_view_complaints(request):
    if not _require_role(request, 'admin'):
        return redirect('login')
    complaints = Complaint.objects.all().order_by('-complaint_id')
    return render(request, 'admin_view_complaints.html', {'complaints': complaints})


def admin_view_feedback(request):
    if not _require_role(request, 'admin'):
        return redirect('login')
    
    feedback_nltk = FeedbackNltk.objects.all()
    # Calculate percentages for each entry
    for f in feedback_nltk:
        pos = f.positive_count or 0
        neg = f.negative_count or 0
        total = pos + neg
        if total > 0:
            f.pos_pct = round((pos / total) * 100, 1)
            f.neg_pct = round((neg / total) * 100, 1)
        else:
            f.pos_pct = 0
            f.neg_pct = 0

    feedback_list = Feedback.objects.all().order_by('-feedback_id')
    return render(request, 'admin_view_feedback.html', {
        'feedback_nltk': feedback_nltk,
        'feedback_list': feedback_list
    })


def admin_view_workers(request):
    if not _require_role(request, 'admin'):
        return redirect('login')
    workers = Workers.objects.all()
    return render(request, 'admin_view_workers.html', {'workers': workers})


def admin_view_requests(request):
    if not _require_role(request, 'admin'):
        return redirect('login')
    requests = RequestWork.objects.all().order_by('-request_work_id')
    return render(request, 'admin_view_requests.html', {'requests': requests})


def admin_view_training_videos(request):
    if not _require_role(request, 'admin'):
        return redirect('login')
    videos = TrainingVideos.objects.all().order_by('-training_video_id')
    return render(request, 'admin_view_training_videos.html', {'videos': videos})


def admin_add_training_video(request):
    if not _require_role(request, 'admin'):
        return redirect('login')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video_file = request.FILES.get('video_file')
        
        if video_file:
            fs = FileSystemStorage()
            filename = fs.save(f'training_videos/{video_file.name}', video_file)
            
            TrainingVideos.objects.create(
                title=title,
                description=description,
                file_path=filename,
                status='active'
            )
            messages.success(request, 'Training video uploaded successfully.')
            return redirect('admin_view_training_videos')
            
    return render(request, 'admin_add_training_video.html')


def admin_delete_training_video(request, video_id):
    if not _require_role(request, 'admin'):
        return redirect('login')
    video = get_object_or_404(TrainingVideos, training_video_id=video_id)
    video.delete()
    messages.warning(request, 'Training video deleted.')
    return redirect('admin_view_training_videos')


def admin_category_delete(request, category_id):
    if not _require_role(request, 'admin'):
        return redirect('login')
    cat = get_object_or_404(Category, category_id=category_id)
    cat.delete()
    messages.success(request, 'Category deleted.')
    return redirect('admin_view_categories')


def admin_complaint_resolve(request, complaint_id):
    if not _require_role(request, 'admin'):
        return redirect('login')
    c = get_object_or_404(Complaint, complaint_id=complaint_id)
    c.status = 'resolved'
    c.save()
    messages.success(request, 'Complaint resolved.')
    return redirect('admin_view_complaints')


def _dashboard_agency(request):
    agency_id = request.session['user_id']
    agency = get_object_or_404(Agency, agency_id=agency_id)
    try:
        cat_id = int(agency.category_id)
    except (TypeError, ValueError):
        cat_id = 0
    categories = Category.objects.all()
    workers_pending = Workers.objects.filter(agency_id=agency_id, status__iexact='pending')
    workers_approved = Workers.objects.filter(agency_id=agency_id, status__iexact='approved')
    workers_blocked = Workers.objects.filter(agency_id=agency_id, status__iexact='blocked')
    job_requests = RequestWork.objects.filter(agency_id=agency_id).order_by('-request_work_id')
    assignments = AssignWorker.objects.filter(request_work_id__in=[r.request_work_id for r in job_requests])
    
    # Financial Summary
    total_quoted = RequestWork.objects.filter(agency_id=agency_id).aggregate(Sum('amount'))['amount__sum'] or 0
    confirmed_count = RequestWork.objects.filter(agency_id=agency_id, status__iexact='confirmed').count()
    
    ctx = {
        'categories': categories,
        'workers_pending': workers_pending,
        'workers_approved': workers_approved,
        'workers_blocked': workers_blocked,
        'job_requests': job_requests,
        'assignments': assignments,
        'total_quoted': total_quoted,
        'confirmed_count': confirmed_count,
    }
    return render(request, 'dashboard_agency.html', ctx)


def _dashboard_worker(request):
    worker_id = request.session['user_id']
    categories = Category.objects.filter(
        category_id__in=WorkerWorkCategory.objects.filter(worker_id=worker_id).values_list('category_id', flat=True)
    )
    assignments = AssignWorker.objects.filter(worker_id=worker_id).order_by('-assign_id')
    
    for a in assignments:
        try:
            rw = RequestWork.objects.get(request_work_id=a.request_work_id)
            user = UserRegister.objects.get(user_id=rw.user_id)
            a.customer_name = user.name
            a.customer_phone = user.phone
        except (RequestWork.DoesNotExist, UserRegister.DoesNotExist):
            a.customer_name = 'Unknown'
            a.customer_phone = 'N/A'
            
    training_videos = TrainingVideos.objects.all().order_by('training_video_id')
    paid_video_ids = list(VideoPayment.objects.filter(worker_id=worker_id).values_list('training_video_id', flat=True))
    
    for video in training_videos:
        if video == training_videos[0]:
            video.is_free = True
            video.is_paid = True
        else:
            video.is_free = False
            video.is_paid = video.training_video_id in paid_video_ids

    ctx = {'categories': categories, 'assignments': assignments, 'training_videos': training_videos}
    return render(request, 'dashboard_worker.html', ctx)


def _dashboard_user(request):
    user_id = request.session['user_id']
    categories = Category.objects.all()
    agencies = Agency.objects.filter(status__iexact='approved')
    workers = Workers.objects.filter(status__iexact='approved')
    my_requests = RequestWork.objects.filter(user_id=user_id).order_by('-request_work_id')
    outside_requests = OutSideWork.objects.filter(user_id=user_id).order_by('-out_side_work_id')
    ctx = {
        'categories': categories,
        'agencies': agencies,
        'workers': workers,
        'my_requests': my_requests,
        'outside_requests': outside_requests,
    }
    return render(request, 'dashboard_user.html', ctx)


def user_upload_image(request):
    if not _require_role(request, 'user'):
        return redirect('login')
    
    if request.method == 'POST' and request.FILES.get('image_file'):
        user_id = request.session['user_id']
        image_file = request.FILES['image_file']
        
        fs = FileSystemStorage()
        filename = fs.save(f'user_uploads/{user_id}_{image_file.name}', image_file)
        image_path = fs.url(filename)
        
        UserImageUpload.objects.create(
            user_id=user_id,
            image_path=image_path,
            upload_date=timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        messages.success(request, 'Image uploaded successfully.')
        return redirect('user_upload_image')
    
    user_id = request.session['user_id']
    my_uploads = UserImageUpload.objects.filter(user_id=user_id).order_by('-upload_id')
    return render(request, 'user_upload_image.html', {'my_uploads': my_uploads})


def user_view_request_work(request):
    if not _require_role(request, 'user'):
        return redirect('login')
    categories = Category.objects.all()
    agencies = Agency.objects.filter(status__iexact='approved')
    return render(request, 'user_view_request_work.html', {
        'categories': categories,
        'agencies': agencies
    })


def user_view_my_requests(request):
    if not _require_role(request, 'user'):
        return redirect('login')
    my_requests = RequestWork.objects.filter(user_id=request.session['user_id']).order_by('-request_work_id')
    
    # Fetch availability for relevant agencies
    agency_ids = my_requests.values_list('agency_id', flat=True).distinct()
    availability = WorkerAvailability.objects.filter(
        worker_id__in=Workers.objects.filter(agency_id__in=agency_ids).values_list('worker_id', flat=True),
        status='available'
    ).order_by('available_date', 'time_slot')

    for r in my_requests:
        try:
            assign = AssignWorker.objects.filter(request_work_id=r.request_work_id).first()
            if assign:
                worker = Workers.objects.get(worker_id=assign.worker_id)
                r.assigned_worker_name = worker.name
                r.assigned_worker_phone = worker.phone
                r.assign_id = assign.assign_id
        except:
            pass
    return render(request, 'user_view_my_requests.html', {
        'my_requests': my_requests,
        'availability': availability
    })


def user_view_agency_services(request, agency_id):
    if not _require_role(request, 'user'):
        return redirect('login')
    agency = get_object_or_404(Agency, agency_id=agency_id)
    services = AgencyWork.objects.filter(agency_id=agency_id)
    
    # Fetch all available slots for this agency's workers
    workers = Workers.objects.filter(agency_id=agency_id, status__iexact='approved')
    availability = WorkerAvailability.objects.filter(
        worker_id__in=workers.values_list('worker_id', flat=True),
        status='available'
    ).order_by('available_date', 'time_slot')

    return render(request, 'user_view_agency_services.html', {
        'agency': agency,
        'services': services,
        'availability': availability
    })

def user_book_service_card(request, work_id):
    if not _require_role(request, 'user'):
        return redirect('login')
    work = get_object_or_404(AgencyWork, work_id=work_id)
    user_id = request.session['user_id']
    preferred_slot = request.POST.get('preferred_slot')

    RequestWork.objects.create(
        user_id=user_id,
        request_date=timezone.now().strftime("%Y-%m-%d"),
        agency_id=work.agency_id,
        category_id=work.category_id,
        work_description=f"Booked: {work.title}",
        amount=int(work.price),
        status='pending',
        work_id=work.work_id,
        preferred_slot=preferred_slot
    )
    messages.success(request, f'Request for "{work.title}" sent to agency.')
    return redirect('user_view_my_requests')


def user_send_enquiry(request, work_id):
    if not _require_role(request, 'user'):
        return redirect('login')
    work = get_object_or_404(AgencyWork, work_id=work_id)
    if request.method == 'POST':
        msg = request.POST.get('enquiry_message', '').strip()
        preferred_slot = request.POST.get('preferred_slot')
        RequestWork.objects.create(
            user_id=request.session['user_id'],
            request_date=timezone.now().strftime("%Y-%m-%d"),
            agency_id=work.agency_id,
            category_id=work.category_id,
            work_description=f"Enquiry on {work.title}: {msg}",
            status='enquiry',
            work_id=work.work_id,
            preferred_slot=preferred_slot
        )
        messages.success(request, f'Enquiry for "{work.title}" sent.')
        return redirect('user_view_my_requests')
    return redirect('user_view_agency_services', agency_id=work.agency_id)

def agency_reply_enquiry(request, request_work_id):
    if not _require_role(request, 'agency'):
        return redirect('login')
    rw = get_object_or_404(RequestWork, request_work_id=request_work_id)
    if request.method == 'POST':
        reply = request.POST.get('agency_reply', '').strip()
        rw.agency_reply = reply
        rw.save()
        messages.success(request, 'Reply sent to user.')
    return redirect('agency_view_jobs')


def user_rebook_service(request, request_work_id):
    if not _require_role(request, 'user'):
        return redirect('login')
    old_req = get_object_or_404(RequestWork, request_work_id=request_work_id)
    if old_req.user_id != request.session['user_id']:
        return redirect('dashboard')
    
    # Create new request from old one
    RequestWork.objects.create(
        user_id=request.session['user_id'],
        request_date=timezone.now().strftime("%Y-%m-%d"),
        agency_id=old_req.agency_id,
        category_id=old_req.category_id,
        work_description=f"Re-booked: {old_req.work_description.replace('Booked: ', '').replace('Re-booked: ', '')}",
        amount=old_req.amount, # Carry over amount if it was a card booking
        status='pending',
        work_id=old_req.work_id,
        preferred_slot=None # New booking needs new slot
    )
    messages.success(request, 'Service re-booked successfully. Agency will review it.')
    return redirect('user_view_my_requests')


def user_cancel_booking(request, request_work_id):
    if not _require_role(request, 'user'):
        return redirect('login')
    rw = get_object_or_404(RequestWork, request_work_id=request_work_id)
    if rw.user_id != request.session['user_id']:
        return redirect('dashboard')
    
    if rw.status == 'confirmed':
        messages.error(request, 'Confirmed bookings cannot be cancelled.')
        return redirect('user_view_my_requests')

    if request.method == 'POST':
        reason = request.POST.get('cancel_reason', '').strip()
        rw.status = 'cancelled'
        rw.cancel_reason = reason
        rw.save()
        messages.warning(request, 'Booking has been cancelled.')
    return redirect('user_view_my_requests')


def user_reschedule_booking(request, request_work_id):
    if not _require_role(request, 'user'):
        return redirect('login')
    rw = get_object_or_404(RequestWork, request_work_id=request_work_id)
    if rw.user_id != request.session['user_id']:
        return redirect('dashboard')
    
    if request.method == 'POST':
        new_slot = request.POST.get('new_slot')
        rw.preferred_slot = new_slot
        rw.save()
        messages.success(request, f'Booking rescheduled to {new_slot}')
    return redirect('user_view_my_requests')


def user_view_outside_work(request):
    if not _require_role(request, 'user'):
        return redirect('login')
    workers = Workers.objects.filter(status__iexact='approved')
    outside_requests = OutSideWork.objects.filter(user_id=request.session['user_id']).order_by('-out_side_work_id')
    return render(request, 'user_view_outside_work.html', {
        'workers': workers,
        'outside_requests': outside_requests
    })


def user_view_complaints(request):
    if not _require_role(request, 'user'):
        return redirect('login')
    
    user_id = request.session['user_id']
    my_complaints = Complaint.objects.filter(user_id=user_id).order_by('-complaint_id')
    other_complaints = Complaint.objects.exclude(user_id=user_id).order_by('-complaint_id')[:20]
    
    ctx = {
        'my_complaints': my_complaints,
        'other_complaints': other_complaints
    }
    return render(request, 'user_view_complaints.html', ctx)


def user_view_feedback(request):
    if not _require_role(request, 'user'):
        return redirect('login')
    
    user_id = request.session['user_id']
    agencies = Agency.objects.filter(status__iexact='approved')
    
    my_feedback = Feedback.objects.filter(user_id=user_id).order_by('-feedback_id')
    for f in my_feedback:
        f.sentiment = get_sentiment(f.description)
        
    other_feedback = Feedback.objects.exclude(user_id=user_id).order_by('-feedback_id')[:20]
    for fo in other_feedback:
        fo.sentiment = get_sentiment(fo.description)
        
    ctx = {
        'agencies': agencies,
        'my_feedback': my_feedback,
        'other_feedback': other_feedback
    }
    return render(request, 'user_view_feedback.html', ctx)


def admin_category_add(request):
    if not _require_role(request, 'admin'):
        return redirect('login')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Category.objects.create(name=name, status='approved')
            messages.success(request, 'Category added.')
    return redirect('admin_view_categories')


def admin_category_approve(request, category_id):
    if not _require_role(request, 'admin'):
        return redirect('login')
    cat = get_object_or_404(Category, category_id=category_id)
    cat.status = 'approved'
    cat.save()
    messages.success(request, f'Category {cat.name} approved.')
    return redirect('admin_view_categories')


def admin_category_reject(request, category_id):
    if not _require_role(request, 'admin'):
        return redirect('login')
    cat = get_object_or_404(Category, category_id=category_id)
    name = cat.name
    cat.delete()
    messages.warning(request, f'Category {name} rejected.')
    return redirect('admin_view_categories')


def agency_add_category(request):
    if not _require_role(request, 'agency'):
        return redirect('login')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Category.objects.create(name=name, status='pending')
            messages.info(request, f'Category "{name}" submitted for admin approval.')
    return redirect('dashboard')


def admin_agency_approve(request, agency_id):
    if not _require_role(request, 'admin'):
        return redirect('login')
    agency = get_object_or_404(Agency, agency_id=agency_id)
    agency.status = 'approved'
    agency.save()
    messages.success(request, 'Agency approved.')
    return redirect('admin_view_agencies')


def admin_agency_reject(request, agency_id):
    if not _require_role(request, 'admin'):
        return redirect('login')
    agency = get_object_or_404(Agency, agency_id=agency_id)
    agency.status = 'rejected'
    agency.save()
    messages.success(request, 'Agency rejected.')
    return redirect('admin_view_agencies')


def admin_agency_block(request, agency_id):
    if not _require_role(request, 'admin'):
        return redirect('login')
    agency = get_object_or_404(Agency, agency_id=agency_id)
    agency.status = 'blocked'
    agency.save()
    messages.warning(request, f'Agency {agency.name} has been BLOCKED.')
    return redirect('admin_view_agencies')


def agency_view_workers(request):
    if not _require_role(request, 'agency'):
        return redirect('login')
    agency_id = request.session['user_id']
    agency = Agency.objects.get(agency_id=agency_id)
    try: cat_id = int(agency.category_id)
    except: cat_id = 0
    
    workers_pending = Workers.objects.filter(agency_id=agency_id, status__iexact='pending')
    workers_approved = Workers.objects.filter(agency_id=agency_id, status__iexact='approved')
    workers_blocked = Workers.objects.filter(agency_id=agency_id, status__iexact='blocked')
    
    return render(request, 'agency_view_workers.html', {
        'workers_pending': workers_pending,
        'workers_approved': workers_approved,
        'workers_blocked': workers_blocked
    })


def agency_manage_availability(request):
    if not _require_role(request, 'agency'):
        return redirect('login')
    agency_id = request.session['user_id']
    workers = Workers.objects.filter(agency_id=agency_id, status__iexact='approved')
    worker_ids = workers.values_list('worker_id', flat=True)
    availabilities = WorkerAvailability.objects.filter(worker_id__in=worker_ids).order_by('-available_date')
    
    if request.method == 'POST':
        worker_id = request.POST.get('worker_id')
        date = request.POST.get('available_date')
        slots = request.POST.getlist('time_slots')
        
        for slot in slots:
            WorkerAvailability.objects.create(
                worker_id=worker_id,
                available_date=date,
                time_slot=slot,
                status='available'
            )
        messages.success(request, 'Availability slots updated.')
        return redirect('agency_manage_availability')

    return render(request, 'agency_manage_availability.html', {
        'workers': workers,
        'availabilities': availabilities
    })


def worker_upload_completion_photo(request, request_work_id):
    if not _require_role(request, 'worker'):
        return redirect('login')
    if request.method == 'POST' and request.FILES.get('task_photo'):
        photo = request.FILES['task_photo']
        fs = FileSystemStorage()
        filename = fs.save(f'task_photos/{photo.name}', photo)
        photo_url = fs.url(filename)
        
        WorkPhotos.objects.create(
            request_work_id=request_work_id,
            photo_path=photo_url
        )
        
        # Optionally update status to something like 'finished_by_worker'
        RequestWork.objects.filter(request_work_id=request_work_id).update(status='finished_by_worker')
        
        messages.success(request, 'Completion photo uploaded.')
    return redirect('worker_view_assignments')

def agency_mark_completed(request, request_work_id):
    if not _require_role(request, 'agency'):
        return redirect('login')
    RequestWork.objects.filter(request_work_id=request_work_id).update(status='completed')
    messages.success(request, 'Job marked as completed.')
    return redirect('agency_view_assignments')


def agency_view_jobs(request):
    if not _require_role(request, 'agency'):
        return redirect('login')
    agency_id = request.session['user_id']
    job_requests = RequestWork.objects.filter(agency_id=agency_id).order_by('-request_work_id')
    workers_approved = Workers.objects.filter(agency_id=agency_id, status__iexact='approved')
    return render(request, 'agency_view_jobs.html', {
        'job_requests': job_requests,
        'workers_approved': workers_approved
    })


def agency_manage_work(request):
    if not _require_role(request, 'agency'):
        return redirect('login')
    agency_id = request.session['user_id']
    works = AgencyWork.objects.filter(agency_id=agency_id).order_by('-work_id')
    return render(request, 'agency_manage_work.html', {'works': works})

def agency_add_work(request):
    if not _require_role(request, 'agency'):
        return redirect('login')
    agency = Agency.objects.get(agency_id=request.session['user_id'])
    
    # Define specifications based on category
    specs_map = {
        '1': ['Wiring Type', 'Load Capacity', 'Warranty Period'],
        '2': ['Pipe Material', 'Service Type', 'Fixture Brand'],
        '3': ['AC Type', 'Cooling Capacity', 'Gas Refill Included'],
        '4': ['Brick Type', 'Cement Grade', 'Finish Style'],
        '5': ['Wood Type', 'Polish Style', 'Hardware Brand'],
        '6': ['Cleaning Kit used', 'Duration', 'No. of Personnel'],
    }
    
    my_specs = specs_map.get(str(agency.category_id), ['Detailed Spec 1', 'Detailed Spec 2', 'Delivery Time'])

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        
        # Collect dynamic specs into JSON string
        collected_specs = {}
        for s in my_specs:
            collected_specs[s] = request.POST.get(s)
        
        import json
        specs_json = json.dumps(collected_specs)

        img_url = None
        if 'work_image' in request.FILES:
            from django.core.files.storage import FileSystemStorage
            fs = FileSystemStorage()
            img = request.FILES['work_image']
            filename = fs.save(f'agency_work/{agency.agency_id}_{img.name}', img)
            img_url = fs.url(filename)

        AgencyWork.objects.create(
            agency_id=agency.agency_id,
            category_id=int(agency.category_id),
            title=title,
            description=description,
            price=price,
            work_image=img_url,
            specifications=specs_json
        )
        messages.success(request, 'Service added successfully to your catalog!')
        return redirect('agency_manage_work')

    return render(request, 'agency_add_work.html', {
        'agency': agency,
        'my_specs': my_specs
    })


def agency_view_assignments(request):
    if not _require_role(request, 'agency'):
        return redirect('login')
    agency_id = request.session['user_id']
    
    assignments = AssignWorker.objects.filter(agency_id=agency_id).order_by('-assign_id')
    for a in assignments:
        try:
            rw = RequestWork.objects.get(request_work_id=a.request_work_id)
            a.status = rw.status
            a.work_description = rw.work_description
            a.worker = Workers.objects.get(worker_id=a.worker_id)
            a.photos = WorkPhotos.objects.filter(request_work_id=a.request_work_id)
        except:
            pass
            
    return render(request, 'agency_view_assignments.html', {'assignments': assignments})


def worker_view_categories(request):
    if not _require_role(request, 'worker'):
        return redirect('login')
    worker_id = request.session['user_id']
    categories = Category.objects.filter(
        category_id__in=WorkerWorkCategory.objects.filter(worker_id=worker_id).values_list('category_id', flat=True)
    )
    return render(request, 'worker_view_categories.html', {'categories': categories})


def worker_view_assignments(request):
    if not _require_role(request, 'worker'):
        return redirect('login')
    worker_id = request.session['user_id']
    assignments = AssignWorker.objects.filter(worker_id=worker_id).order_by('-assign_id')
    for a in assignments:
        try:
            rw = RequestWork.objects.get(request_work_id=a.request_work_id)
            user = UserRegister.objects.get(user_id=rw.user_id)
            a.customer_name = user.name
            a.customer_phone = user.phone
        except:
            a.customer_name = 'Unknown'
            a.customer_phone = 'N/A'
    return render(request, 'worker_view_assignments.html', {'assignments': assignments})


def worker_view_training(request):
    if not _require_role(request, 'worker'):
        return redirect('login')
    worker_id = request.session['user_id']
    training_videos = TrainingVideos.objects.all().order_by('training_video_id')
    
    # Check payments for this worker
    paid_video_ids = list(VideoPayment.objects.filter(worker_id=worker_id).values_list('training_video_id', flat=True))
    
    for video in training_videos:
        # First video (smallest ID) is free. User said "one video id=s for free" 
        # I'll assume the first uploaded video (lowest ID) is the free one.
        if video == training_videos[0]:
            video.is_free = True
            video.is_paid = True # Effectively paid since it's free
        else:
            video.is_free = False
            video.is_paid = video.training_video_id in paid_video_ids
            
    return render(request, 'worker_view_training.html', {'training_videos': training_videos})


def worker_create_video_payment_order(request, video_id):
    if not _require_role(request, 'worker'):
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    video = get_object_or_404(TrainingVideos, training_video_id=video_id)
    
    try:
        amount = 500 * 100 # Fixed price 500 INR in paise
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'video_{video_id}',
            'payment_capture': 1
        }
        order = RAZORPAY_CLIENT.order.create(data=order_data)
        return JsonResponse({
            'success': True,
            'order_id': order['id'],
            'amount': amount,
            'key': "rzp_test_SROSnyInFv81S4"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def worker_video_payment_success(request, video_id):
    if not _require_role(request, 'worker'):
        return redirect('login')
    
    worker_id = request.session['user_id']
    VideoPayment.objects.create(
        worker_id=worker_id,
        training_video_id=video_id,
        amount=500,
        payment_date=timezone.now().strftime("%Y-%m-%d")
    )
    
    messages.success(request, 'Payment successful! You can now watch the video.')
    return redirect('worker_view_training')


def agency_worker_approve(request, worker_id):
    if not _require_role(request, 'agency'):
        return redirect('login')
    worker = get_object_or_404(Workers, worker_id=worker_id)
    worker.agency_id = request.session['user_id']
    worker.status = 'approved'
    worker.save()
    messages.success(request, 'Worker approved.')
    return redirect('dashboard')


def agency_worker_reject(request, worker_id):
    if not _require_role(request, 'agency'):
        return redirect('login')
    worker = get_object_or_404(Workers, worker_id=worker_id)
    worker.status = 'rejected'
    worker.save()
    messages.success(request, 'Worker rejected.')
    return redirect('dashboard')


def agency_worker_block(request, worker_id):
    if not _require_role(request, 'agency'):
        return redirect('login')
    worker = get_object_or_404(Workers, worker_id=worker_id, agency_id=request.session['user_id'])
    worker.status = 'blocked'
    worker.save()
    messages.warning(request, f'Worker {worker.name} has been BLOCKED.')
    return redirect('dashboard')


def agency_set_amount(request, request_work_id):
    if not _require_role(request, 'agency'):
        return redirect('login')
    rw = get_object_or_404(RequestWork, request_work_id=request_work_id)
    if rw.agency_id != request.session['user_id']:
        return redirect('dashboard')
    if request.method == 'POST':
        amount = request.POST.get('amount', '').strip()
        if amount.isdigit():
            rw.amount = int(amount)
            rw.status = 'quoted'
            rw.save()
            messages.success(request, 'Amount set.')
        return redirect('dashboard')
    return redirect('dashboard')


def agency_assign_worker(request, request_work_id):
    if not _require_role(request, 'agency'):
        return redirect('login')
    rw = get_object_or_404(RequestWork, request_work_id=request_work_id)
    if rw.agency_id != request.session['user_id']:
        return redirect('dashboard')
    if request.method == 'POST':
        worker_id = request.POST.get('worker_id', '').strip()
        if worker_id and Workers.objects.filter(worker_id=worker_id, agency_id=request.session['user_id'], status__iexact='approved').exists():
            AssignWorker.objects.create(
                request_work_id=rw.request_work_id,
                worker_id=worker_id,
                assign_date=timezone.now().strftime('%Y-%m-%d'),
                work_description=rw.work_description or '',
                status='assigned',
            )
            rw.status = 'assigned'
            rw.save()
            messages.success(request, 'Worker assigned.')
        return redirect('dashboard')
    return redirect('dashboard')


def user_request_work(request):
    if not _require_role(request, 'user'):
        return redirect('login')
    if request.method != 'POST':
        return redirect('dashboard')
    user_id = request.session['user_id']
    agency_id = request.POST.get('agency_id', '').strip()
    category_id = request.POST.get('category_id', '').strip()
    work_description = request.POST.get('work_description', '').strip()
    if not agency_id or not work_description:
        messages.error(request, 'Agency and work description required.')
        return redirect('dashboard')
    RequestWork.objects.create(
        user_id=user_id,
        request_date=timezone.now().strftime('%Y-%m-%d'),
        agency_id=agency_id,
        category_id=int(category_id) if category_id.isdigit() else None,
        work_description=work_description,
        amount=None,
        status='pending',
    )
    messages.success(request, 'Work request sent.')
    return redirect('user_view_my_requests')


def user_confirm_work(request, request_work_id):
    if not _require_role(request, 'user'):
        return redirect('login')
    rw = get_object_or_404(RequestWork, request_work_id=request_work_id)
    if rw.user_id != request.session['user_id']:
        return redirect('dashboard')
    rw.status = 'confirmed'
    rw.save()
    messages.success(request, 'Work confirmed.')
    return redirect('user_view_my_requests')


def user_complaint(request):
    if not _require_role(request, 'user'):
        return redirect('login')
    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        if description:
            Complaint.objects.create(
                user_id=request.session['user_id'],
                complaint_date=timezone.now().strftime('%Y-%m-%d'),
                description=description[:50],
            )
            messages.success(request, 'Complaint submitted.')
        return redirect('user_view_complaints')
    return redirect('user_view_complaints')


def user_feedback(request):
    if not _require_role(request, 'user'):
        return redirect('login')
    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        agency_id = request.POST.get('agency_id', '').strip()
        if description and agency_id:
            Feedback.objects.create(
                user_id=request.session['user_id'],
                feedback_date=timezone.now().strftime('%Y-%m-%d'),
                description=description[:500],
            )
            update_feedback_nltk_for_agency(agency_id, description)
            messages.success(request, 'Feedback submitted (NLP sentiment recorded).')
        return redirect('user_view_feedback')
    return redirect('user_view_feedback')


def user_outside_work_request(request):
    if not _require_role(request, 'user'):
        return redirect('login')
    if request.method == 'POST':
        worker_id = request.POST.get('worker_id', '').strip()
        work_details = request.POST.get('work_details', '').strip()
        if worker_id and work_details:
            OutSideWork.objects.create(
                worker_id=worker_id,
                user_id=request.session['user_id'],
                work_details=work_details[:500],
                request_date=timezone.now().strftime('%Y-%m-%d'),
                status='pending',
            )
            messages.success(request, 'Work request sent to worker.')
        return redirect('user_view_outside_work')
    return redirect('user_view_outside_work')


def chat_page(request):
    if not request.session.get('user_id'):
        return redirect('login')
    return render(request, 'chat.html')


@require_http_methods(['POST'])
def chat_api(request):
    try:
        if not request.session.get('user_id'):
            return JsonResponse({'reply': 'Please log in first.'})
        try:
            data = __import__('json').loads(request.body)
            msg = (data.get('message') or '').strip()
        except Exception:
            msg = request.POST.get('message', '').strip()
        
        intent, reply = chat_get_response_rnn(msg)
        workers_list = []
        
        # 1. Handle Worker Listing (Dynamic lookup)
        intent_map = {
            'workers_electrical': 'electrical', 'workers_plumbing': 'plumbing', 
            'workers_climate': 'climate', 'workers_masonry': 'masonry', 
            'workers_carpentry': 'carpentry', 'workers_cleaning': 'cleaning',
        }
        cat_name = intent_map.get(intent)
        if cat_name:
            cat = Category.objects.filter(name__icontains=cat_name, status__iexact='approved').first()
            if cat and cat.category_id:
                worker_ids = WorkerWorkCategory.objects.filter(category_id=cat.category_id).values_list('worker_id', flat=True)
                matching_workers = Workers.objects.filter(worker_id__in=worker_ids, status__iexact='approved')[:10]
                for w in matching_workers:
                    # Calculate 'Expertise Level' based on completed jobs since rating table is separate
                    completed_jobs = OutSideWork.objects.filter(worker_id=w.worker_id, status__iexact='completed').count()
                    # Assign a mock rating for display based on experience (e.g., 4.0 + 0.1 for every 5 jobs, up to 5.0)
                    rating_val = min(5.0, 4.0 + (completed_jobs // 5) * 0.1)
                    workers_list.append({'id': w.worker_id, 'name': w.name, 'phone': w.phone, 'rating': rating_val, 'jobs': completed_jobs})
                
                if workers_list:
                    reply = f"I found the following verified professionals for {cat.name}. You can contact them directly or book through me:\n" + "\n".join([f"- {w['name']} (📞 {w['phone']}) — {w['rating']} ★" for w in workers_list])
                    reply += "\n\nWould you like me to book one for you? Just type 'Book [Name]'."
                else:
                    reply = f"I'm sorry, I couldn't find any approved {cat_name} workers at the moment. Would you like to check another category?"
            else:
                reply = f"I'm sorry, I couldn't find a service category matching '{cat_name}'. Please try typing the exact name from the list above."

        # 2. Handle Booking Info (Process explanation)
        elif intent == 'booking_info':
            cats = Category.objects.filter(status__iexact='approved')
            cat_list = "\n".join([f"{i+1}. {c.name}" for i, c in enumerate(cats)])
            reply = f"Booking a worker is simple! 1. Find a service type. 2. Choose a verified professional from the list. 3. Confirm the date.\n\nHere are some categories active now:\n{cat_list}\n\nShall I pick the best one for you?"
        # 3. Handle All Services Available
        elif intent == 'all_services':
            cats = Category.objects.filter(status__iexact='approved')
            if cats.exists():
                cat_names = ", ".join([c.name for c in cats])
                reply = f"Nex-Gen Service connects you with specialists in: {cat_names}. We focus on quality and verified expertise across all these domains."
            else:
                reply = "We offer Plumbing, Electrical, Cleaning, and Construction services. New categories are added every week!"

        # 4. Handle Best Worker & Comparison
        elif intent == 'best_worker' or intent == 'comparison':
            # Check if it's a specific comparison between two people
            names = re.findall(r"(?:between|compare|and|with)\s+([\w]{3,})", msg, re.I)
            if len(names) >= 2:
                w1_name, w2_name = names[0], names[1]
                w1 = Workers.objects.filter(name__icontains=w1_name).first()
                w2 = Workers.objects.filter(name__icontains=w2_name).first()
                if w1 and w2:
                    c1 = OutSideWork.objects.filter(worker_id=w1.worker_id, status__iexact='completed').count()
                    c2 = OutSideWork.objects.filter(worker_id=w2.worker_id, status__iexact='completed').count()
                    better = w1.name if c1 >= c2 else w2.name
                    r1 = min(5.0, 4.0 + (c1 // 5) * 0.1)
                    r2 = min(5.0, 4.0 + (c2 // 5) * 0.1)
                    reply = f"Comparing {w1.name} ({round(r1,1)} ★) and {w2.name} ({round(r2,1)} ★): {better} currently holds the lead in successful job completions and reliability."
                else:
                    reply = "I couldn't find both workers for a side-by-side comparison. Generally, our top performers have 4.5+ stars."
            else:
                # General 'best worker' query by completion count
                from django.db.models import Count
                best_w_data = OutSideWork.objects.filter(status__iexact='completed').values('worker_id').annotate(count=Count('out_side_work_id')).order_by('-count').first()
                if best_w_data:
                    w = Workers.objects.filter(worker_id=best_w_data['worker_id']).first()
                    if w:
                        reply = f"The top-performing worker across our platform right now is {w.name}, with {best_w_data['count']} successfully completed jobs and a very high reliability score."
                else:
                    reply = "Arun and Sinu are currently among our most requested professionals. Arun has a perfect record in Electrical works!"

        # 4. Handle Request Status
        elif intent == 'request_status':
            req = RequestWork.objects.filter(user_id=request.session['user_id']).order_by('-request_work_id').first()
            if req:
                # Find associated worker if any
                assign = AssignWorker.objects.filter(request_work_id=req.request_work_id).first()
                worker_info = ""
                if assign and assign.worker_id:
                    worker = Workers.objects.filter(worker_id=assign.worker_id).first()
                    if worker:
                        worker_info = f" Worker {worker.name} has been assigned to help you."
                
                reply = f"Your latest request for '{req.work_description[:40]}...' is currently **{req.status.upper()}**.{worker_info} I will notify you of further updates."
            else:
                reply = "I couldn't find any recent service requests for your account. Would you like to book one now?"

        # 5. Handle Best Agency with Location Awareness
        elif intent == 'best_agency':
            location_match = re.search(r'in\s+([\w]+)', msg, re.I)
            location = location_match.group(1) if location_match else ""
            
            q = Agency.objects.filter(status__iexact='approved')
            if location:
                q = q.filter(address__icontains=location)
                loc_txt = f"in {location.capitalize()}"
            else:
                loc_txt = "on our platform"
                
            best_a = q.first() # Or sort by some metric
            if best_a:
                w_count = Workers.objects.filter(agency_id=best_a.agency_id).count()
                reply = f"{loc_txt}, '{best_a.name}' is highly recommended. They are a verified partner with {w_count} registered professionals."
            else:
                reply = f"We have several verified partners {loc_txt}. 'Nexgen' and 'Apex Home' are currently top-rated."

        # 6. Handle Specific Agency Verification
        elif intent == 'agency_verification':
            name_match = re.search(r"is\s+'?([\w\s]+)'?\s+verified", msg, re.I)
            if not name_match:
                name_match = re.search(r"verification\s+of\s+([\w\s]+)", msg, re.I)
            
            if name_match:
                a_name = name_match.group(1).strip()
                a = Agency.objects.filter(name__icontains=a_name).first()
                if a:
                    status_txt = "a verified partner" if a.status == 'approved' else "currently under verification"
                    reply = f"Yes, '{a.name}' is {status_txt}. All their workers have completed background checks and training."
                else:
                    reply = f"I couldn't find '{a_name}' in our verified registry. Please double-check the name."
            else:
                reply = "Yes, our top partners are fully verified. All their workers have completed rigorous background checks."

        # 7. Handle Agencies for Specific Service
        elif intent == 'agency_for_service':
            cat_match = re.search(r'provides\s+([\w\s]+)', msg, re.I)
            if not cat_match:
                cat_match = re.search(r'for\s+([\w\s]+)', msg, re.I)
            
            if cat_match:
                service_req = cat_match.group(1).strip().replace(' services', '').replace(' service', '')
                # Find category
                cat = Category.objects.filter(name__icontains=service_req).first()
                if cat:
                    # Find agencies that have workers in this category
                    worker_ids = WorkerWorkCategory.objects.filter(category_id=cat.category_id).values_list('worker_id', flat=True)
                    agency_ids = Workers.objects.filter(worker_id__in=worker_ids).values_list('agency_id', flat=True).distinct()
                    agencies = Agency.objects.filter(agency_id__in=agency_ids, status__iexact='approved')[:3]
                    
                    if agencies.exists():
                        list_txt = "\n".join([f"- {a.name}" for a in agencies])
                        reply = f"There are {agencies.count()} verified agencies providing {cat.name} services near you:\n{list_txt}"
                    else:
                        reply = f"We have multiple independent workers for {cat.name}. Would you like me to find one for you?"
                else:
                    reply = f"I'm checking our agency directory for {service_req} specialists..."
            else:
                reply = "Several agencies provide specialized cleaning, plumbing, and electrical services. Which one do you need?"

        # 8. Handle Worker Comparison
        elif intent == 'comparison':
            names = re.findall(r"(?:between|compare|and|with)\s+([\w]{3,})", msg, re.I)
            if len(names) >= 2:
                w1_name, w2_name = names[0], names[1]
                w1 = Workers.objects.filter(name__icontains=w1_name).first()
                w2 = Workers.objects.filter(name__icontains=w2_name).first()
                if w1 and w2:
                    r1 = Feedback.objects.filter(worker_id=w1.worker_id).aggregate(s=Sum('rating'), c=Count('feedback_id'))
                    r2 = Feedback.objects.filter(worker_id=w2.worker_id).aggregate(s=Sum('rating'), c=Count('feedback_id'))
                    avg1 = float(r1['s']/r1['c']) if r1['c'] and r1['s'] else 4.0
                    avg2 = float(r2['s']/r2['c']) if r2['c'] and r2['s'] else 4.0
                    better = w1.name if avg1 >= avg2 else w2.name
                    reply = f"Comparing {w1.name} ({round(avg1,1)} ★) and {w2.name} ({round(avg2,1)} ★): {better} currently holds the lead in customer satisfaction."
                else:
                    reply = "I couldn't find both workers for a detailed comparison. Generally, our top performers have 4.5+ stars."
            else:
                reply = "I can compare any two workers! Just ask 'Who is better between Arun and Sinu?'"

        # 9. Handle Feedback/Rating Info
        elif intent == 'rate_service':
            reply = "Customer feedback is vital! To give a rating: Go to your Dashboard -> My Requests -> Find 'Completed' job -> Click 'Rate'. This helps our AI suggest better workers for you."

        # 9. Handle Final Booking by Name
        elif intent == 'final_booking':
            name_match = re.search(r'(?:book|hire|reserve|okay I will book|i want to book)\s+(?:a |the )?([\w\s]{2,})', msg, re.I)
            if name_match:
                w_name = name_match.group(1).strip()
                worker = Workers.objects.filter(name__icontains=w_name, status__iexact='approved').first()
                if worker:
                    OutSideWork.objects.create(
                        worker_id=worker.worker_id,
                        user_id=request.session['user_id'],
                        work_details='Booked automatically via AI Chat.',
                        request_date=timezone.now().strftime('%Y-%m-%d'),
                        status='pending',
                    )
                    reply = f"Great choice! I have sent your booking request to {worker.name}. They will be notified immediately."
                else:
                    reply = f"I couldn't find an approved worker named '{w_name}'. Please make sure the name is correct or choose from the list above."
            else:
                reply = "Sure! Which worker would you like to book? Please type their name clearly."

        return JsonResponse({
            'reply': reply,
            'intent': intent,
            'workers': workers_list
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'reply': f"Chatbot Error: {str(e)}", 'intent': 'error', 'workers': []})



@require_http_methods(['POST'])
def chat_book_worker(request):
    if not _require_role(request, 'user'):
        return JsonResponse({'success': False, 'message': 'Auth required.'})
    try:
        data = __import__('json').loads(request.body)
        worker_id = data.get('worker_id')
        if not worker_id:
             return JsonResponse({'success': False, 'message': 'No worker selected.'})
        
        worker = get_object_or_404(Workers, worker_id=worker_id, status__iexact='approved')
        
        OutSideWork.objects.create(
            worker_id=worker_id,
            user_id=request.session['user_id'],
            work_details='Booked via AI Chat support.',
            request_date=timezone.now().strftime('%Y-%m-%d'),
            status='pending',
        )
        return JsonResponse({'success': True, 'message': f'Request sent to {worker.name}!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def user_payment_success(request, request_work_id):
    if not _require_role(request, 'user'):
        return redirect('login')
    
    rw = get_object_or_404(RequestWork, request_work_id=request_work_id, user_id=request.session['user_id'])
    rw.status = 'confirmed'
    rw.save()
    
    AssignWorker.objects.filter(request_work_id=request_work_id).update(status='confirmed')
    
    messages.success(request, f"Payment successful! Work request #{request_work_id} is now confirmed.")
    return redirect('user_view_my_requests')


def user_create_payment_order(request, request_work_id):
    if not _require_role(request, 'user'):
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    rw = get_object_or_404(RequestWork, request_work_id=request_work_id, user_id=request.session['user_id'])
    
    try:
        amount = int(rw.amount) * 100 # In paise
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'rcpt_{request_work_id}',
            'payment_capture': 1
        }
        order = RAZORPAY_CLIENT.order.create(data=order_data)
        return JsonResponse({
            'success': True, 
            'order_id': order['id'], 
            'amount': amount,
            'key': "rzp_test_SROSnyInFv81S4"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
def user_view_payment_history(request):
    if not _require_role(request, 'user'):
        return redirect('login')
    
    payments = RequestWork.objects.filter(user_id=request.session['user_id'], status__iexact='confirmed').order_by('-request_work_id')
    
    for p in payments:
        try:
            assign = AssignWorker.objects.filter(request_work_id=p.request_work_id).first()
            if assign:
                worker = Workers.objects.get(worker_id=assign.worker_id)
                p.assigned_worker_name = worker.name
        except:
            pass
            
    return render(request, 'user_view_payment_history.html', {'payments': payments})


def user_profile(request):
    if not _require_role(request, 'user'):
        return redirect('login')
    user = get_object_or_404(UserRegister, user_id=request.session['user_id'])
    if request.method == 'POST':
        user.name = request.POST.get('name', user.name)
        user.address = request.POST.get('address', user.address)
        user.phone = request.POST.get('phone', user.phone)
        user.email = request.POST.get('email', user.email)
        
        # Handle Profile Image Update
        if 'user_image' in request.FILES:
            from django.core.files.storage import FileSystemStorage
            fs = FileSystemStorage()
            img = request.FILES['user_image']
            filename = fs.save(f'user_pics/profile_{user.user_id}_{img.name}', img)
            user.user_image = fs.url(filename)
            
        # Handle Password Change
        curr_pwd = request.POST.get('current_password')
        new_pwd = request.POST.get('new_password')
        conf_pwd = request.POST.get('confirm_password')
        
        if curr_pwd:
            if curr_pwd != user.password:
                messages.error(request, 'Verification Failed: Incorrect current password.')
                return redirect('user_profile')
            if not new_pwd or new_pwd != conf_pwd:
                messages.error(request, 'Validation Failed: New passwords do not match.')
                return redirect('user_profile')
            user.password = new_pwd
            
        user.save()
        request.session['user_name'] = user.name
        messages.success(request, 'Profile updated successfully.')
        return redirect('user_profile')
    return render(request, 'user_profile.html', {'user': user})


def worker_profile(request):
    if not _require_role(request, 'worker'):
        return redirect('login')
    worker = get_object_or_404(Workers, worker_id=request.session['user_id'])
    categories = Category.objects.filter(status__iexact='approved')
    my_category_ids = WorkerWorkCategory.objects.filter(worker_id=worker.worker_id).values_list('category_id', flat=True)
    
    if request.method == 'POST':
        worker.name = request.POST.get('name', worker.name)
        worker.address = request.POST.get('address', worker.address)
        worker.phone = request.POST.get('phone', worker.phone)
        worker.email = request.POST.get('email', worker.email)
        worker.password = request.POST.get('password', worker.password)
        worker.availability = request.POST.get('availability', 'active')
        worker.save()
        
        # Update Categories
        selected_cats = request.POST.getlist('categories')
        if selected_cats:
            WorkerWorkCategory.objects.filter(worker_id=worker.worker_id).delete()
            for cid in selected_cats:
                WorkerWorkCategory.objects.create(worker_id=worker.worker_id, category_id=int(cid))

        request.session['user_name'] = worker.name
        messages.success(request, 'Profile, availability and categories updated.')
        return redirect('worker_profile')
        
    return render(request, 'worker_profile.html', {
        'worker': worker,
        'categories': categories,
        'my_category_ids': list(my_category_ids)
    })

def worker_view_payments(request):
    if not _require_role(request, 'worker'):
        return redirect('login')
    worker_id = request.session['user_id']
    assignments = AssignWorker.objects.filter(worker_id=worker_id)
    req_ids = assignments.values_list('request_work_id', flat=True)
    payments = RequestWork.objects.filter(request_work_id__in=req_ids, status__iexact='confirmed').order_by('-request_work_id')
    
    total_earned = sum([p.amount for p in payments if p.amount])
    return render(request, 'worker_payment_history.html', {'payments': payments, 'total_earned': total_earned})


def agency_profile(request):
    if not _require_role(request, 'agency'):
        return redirect('login')
    agency = get_object_or_404(Agency, agency_id=request.session['user_id'])
    if request.method == 'POST':
        agency.name = request.POST.get('name', agency.name)
        agency.address = request.POST.get('address', agency.address)
        agency.phone = request.POST.get('phone', agency.phone)
        agency.email = request.POST.get('email', agency.email)
        agency.password = request.POST.get('password', agency.password)
        
        # Handle Profile Image Update
        if 'agency_image' in request.FILES:
            from django.core.files.storage import FileSystemStorage
            fs = FileSystemStorage()
            img = request.FILES['agency_image']
            # Save with a prefix to indicate profile update
            filename = fs.save(f'agency_pics/profile_{agency.agency_id}_{img.name}', img)
            agency.agency_image = fs.url(filename)
            
        agency.save()
        request.session['user_name'] = agency.name
        messages.success(request, 'Profile updated successfully.')
        return redirect('agency_profile')
    return render(request, 'agency_profile.html', {'agency': agency})


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Please enter your email.')
            return render(request, 'forgot_password.html')
            
        # Check all 3 roles
        u = UserRegister.objects.filter(email=email).first()
        if u: return redirect('reset_password', role='user', uid=u.user_id)
        
        w = Workers.objects.filter(email=email).first()
        if w: return redirect('reset_password', role='worker', uid=w.worker_id)
        
        a = Agency.objects.filter(email=email).first()
        if a: return redirect('reset_password', role='agency', uid=a.agency_id)
        
        messages.error(request, 'Email not found in our database.')
    return render(request, 'forgot_password.html')


def reset_password_view(request, role, uid):
    context = {'role': role, 'uid': uid}
    if request.method == 'POST':
        new_pass = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        
        if not new_pass or new_pass != confirm:
            messages.error(request, 'Passwords mismatch or empty.')
            return render(request, 'reset_password.html', context)
            
        if role == 'user':
            obj = get_object_or_404(UserRegister, user_id=uid)
        elif role == 'worker':
            obj = get_object_or_404(Workers, worker_id=uid)
        elif role == 'agency':
            obj = get_object_or_404(Agency, agency_id=uid)
        else:
            return redirect('login')
            
        obj.password = new_pass
        obj.save()
        messages.success(request, 'Success! Password updated.')
        return redirect('login')
        
    return render(request, 'reset_password.html', context)



def upload_form(request):
    return render(request, 'user/upload.html')




from django.core.files.storage import default_storage

import json
import numpy as np
from django.http import JsonResponse
from django.core.files.storage import default_storage
from tensorflow.keras.preprocessing import image

import json
import numpy as np
import tensorflow as tf
from django.http import JsonResponse
from django.core.files.storage import default_storage
from tensorflow.keras.preprocessing import image


model = tf.keras.models.load_model('problem_detector_model.h5')


with open('labels.json') as f:
    class_indices = json.load(f)

labels = {v: k for k, v in class_indices.items()}

THRESHOLD = 0.6


def predict(request):
    if request.method == 'POST' and request.FILES.get('image'):

        try:

            f = request.FILES['image']
            file_name = default_storage.save(f.name, f)
            file_path = default_storage.path(file_name)

            request.session['file_loc'] = file_name


            img = image.load_img(file_path, target_size=(150, 150))
            arr = image.img_to_array(img) / 255.0
            arr = np.expand_dims(arr, axis=0)


            pred = model.predict(arr)
            idx = int(np.argmax(pred))
            confidence = float(np.max(pred))

            print("Raw Prediction:", pred)
            print("Predicted Index:", idx)
            print("Confidence:", confidence)


            if confidence < THRESHOLD:
                result = "unknown"
            else:
                result = labels.get(idx, "unknown")

            return JsonResponse({
                'prediction': result,
                'confidence': round(confidence * 100, 2)
            })

        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)

    return JsonResponse({
        'error': 'Invalid request'
    }, status=400)


