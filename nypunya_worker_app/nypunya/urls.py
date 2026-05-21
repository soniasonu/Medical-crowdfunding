from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<str:role>/<str:uid>/', views.reset_password_view, name='reset_password'),
    path('logout/', views.logout_view, name='logout_view'),
    path('register/', views.register_select, name='register_select'),
    path('register/user/', views.register_user_view, name='register_user'),
    path('register/agency/', views.register_agency_view, name='register_agency'),
    path('register/worker/', views.register_worker_view, name='register_worker'),
    
    # Agency Dashboard
    path('dashboard/agency/workers/', views.agency_view_workers, name='agency_view_workers'),
    path('dashboard/agency/jobs/', views.agency_view_jobs, name='agency_view_jobs'),
    path('dashboard/agency/assignments/', views.agency_view_assignments, name='agency_view_assignments'),
    path('dashboard/agency/services/', views.agency_manage_work, name='agency_manage_work'),
    path('dashboard/agency/services/add/', views.agency_add_work, name='agency_add_work'),
    path('dashboard/agency/availability/', views.agency_manage_availability, name='agency_manage_availability'),
    path('dashboard/agency/profile/', views.agency_profile, name='agency_profile'),
    
    # Worker Dashboard
    path('dashboard/worker/categories/', views.worker_view_categories, name='worker_view_categories'),
    path('dashboard/worker/assignments/', views.worker_view_assignments, name='worker_view_assignments'),
    path('dashboard/worker/training/', views.worker_view_training, name='worker_view_training'),
    path('dashboard/worker/payments/', views.worker_view_payments, name='worker_view_payments'),
    path('dashboard/worker/profile/', views.worker_profile, name='worker_profile'),
    
    # User Dashboard
    path('dashboard/user/profile/', views.user_profile, name='user_profile'),
    path('dashboard/user/agencies/<str:agency_id>/services/', views.user_view_agency_services, name='user_view_agency_services'),
    path('dashboard/user/services/<int:work_id>/book/', views.user_book_service_card, name='user_book_service_card'),
    path('dashboard/user/services/<int:work_id>/enquiry/', views.user_send_enquiry, name='user_send_enquiry'),
    path('user/dashboard/payment-history/', views.user_view_payment_history, name='user_view_payment_history'),
    path('user/request/<int:request_work_id>/rebook/', views.user_rebook_service, name='user_rebook_service'),
    path('user/request/<int:request_work_id>/cancel/', views.user_cancel_booking, name='user_cancel_booking'),
    path('user/request/<int:request_work_id>/reschedule/', views.user_reschedule_booking, name='user_reschedule_booking'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('chat/', views.chat_page, name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/chat/book/', views.chat_book_worker, name='chat_book_worker'),
    
    # Admin
    path('portal-admin/categories/', views.admin_view_categories, name='admin_view_categories'),
    path('portal-admin/category/add/', views.admin_category_add, name='admin_category_add'),
    path('portal-admin/category/<int:category_id>/approve/', views.admin_category_approve, name='admin_category_approve'),
    path('portal-admin/category/<int:category_id>/reject/', views.admin_category_reject, name='admin_category_reject'),
    path('portal-admin/category/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
    path('portal-admin/agencies/', views.admin_view_agencies, name='admin_view_agencies'),
    path('portal-admin/complaints/', views.admin_view_complaints, name='admin_view_complaints'),
    path('portal-admin/complaints/<int:complaint_id>/resolve/', views.admin_complaint_resolve, name='admin_complaint_resolve'),
    path('portal-admin/feedback/', views.admin_view_feedback, name='admin_view_feedback'),
    path('portal-admin/users/', views.admin_view_users, name='admin_view_users'),
    path('portal-admin/workers/', views.admin_view_workers, name='admin_view_workers'),
    path('portal-admin/all-requests/', views.admin_view_requests, name='admin_view_requests'),
    path('portal-admin/agency/<str:agency_id>/approve/', views.admin_agency_approve, name='admin_agency_approve'),
    path('portal-admin/agency/<str:agency_id>/reject/', views.admin_agency_reject, name='admin_agency_reject'),
    path('portal-admin/agency/<str:agency_id>/block/', views.admin_agency_block, name='admin_agency_block'),
    
    path('portal-admin/training-videos/', views.admin_view_training_videos, name='admin_view_training_videos'),
    path('portal-admin/training-videos/add/', views.admin_add_training_video, name='admin_add_training_video'),
    path('portal-admin/training-videos/<int:video_id>/delete/', views.admin_delete_training_video, name='admin_delete_training_video'),
    
    # Actions
    path('agency/worker/<str:worker_id>/approve/', views.agency_worker_approve, name='agency_worker_approve'),
    path('agency/worker/<str:worker_id>/reject/', views.agency_worker_reject, name='agency_worker_reject'),
    path('agency/worker/<str:worker_id>/block/', views.agency_worker_block, name='agency_worker_block'),
    path('agency/add-category/', views.agency_add_category, name='agency_add_category'),
    path('agency/request/<int:request_work_id>/amount/', views.agency_set_amount, name='agency_set_amount'),
    path('agency/request/<int:request_work_id>/assign/', views.agency_assign_worker, name='agency_assign_worker'),
    path('agency/request/<int:request_work_id>/reply/', views.agency_reply_enquiry, name='agency_reply_enquiry'),
    path('agency/request/<int:request_work_id>/complete/', views.agency_mark_completed, name='agency_mark_completed'),
    path('worker/request/<int:request_work_id>/upload-photo/', views.worker_upload_completion_photo, name='worker_upload_completion_photo'),
    
    path('user/dashboard/request-work/', views.user_view_request_work, name='user_view_request_work'),
    path('user/dashboard/my-requests/', views.user_view_my_requests, name='user_view_my_requests'),
    path('user/dashboard/outside-work/', views.user_view_outside_work, name='user_view_outside_work'),
    path('user/dashboard/complaints/', views.user_view_complaints, name='user_view_complaints'),
    path('user/dashboard/feedback/', views.user_view_feedback, name='user_view_feedback'),
    path('user/dashboard/upload-image/', views.user_upload_image, name='user_upload_image'),
    path('user/request-work/', views.user_request_work, name='user_request_work'),
    path('user/request/<int:request_work_id>/confirm/', views.user_confirm_work, name='user_confirm_work'),
    path('user/complaint/', views.user_complaint, name='user_complaint'),
    path('user/feedback/', views.user_feedback, name='user_feedback'),
    path('user/outside-work/', views.user_outside_work_request, name='user_outside_work_request'),
    path('user/payment/<int:request_work_id>/success/', views.user_payment_success, name='user_payment_success'),
    path('api/user/payment/order/<int:request_work_id>/', views.user_create_payment_order, name='user_create_payment_order'),
    path('worker/payment/<int:video_id>/success/', views.worker_video_payment_success, name='worker_video_payment_success'),
    path('api/worker/payment/order/<int:video_id>/', views.worker_create_video_payment_order, name='worker_create_video_payment_order'),
    path('upload_form', views.upload_form),
    path('predict', views.predict),


]
