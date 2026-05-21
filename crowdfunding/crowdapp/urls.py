
from django.urls import path, include

from crowdapp import views
import crowdapp
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('login1', views.login1, name='login1'),
    path('AdminHomePage/', views.AdminHomePage, name='AdminHomePage'),
    path('HospitalHome/', views.HospitalHome, name='HospitalHome'),
    path('addCategory', views.addCategory, name='addCategory'),
    path('view_approved_panchayat', views.view_approved_panchayat, name='view_approved_panchayat'),
    path('viewCategory', views.viewCategory, name='viewCategory'),
    # path('get_amount_details/<str:id>', views.get_amount_details, name='get_amount_details'),
    path('editCategory/<int:id>', views.editCategory, name='editCategory'),
    path('deleteCategory/<int:id>', views.deleteCategory, name='deleteCategory'),
    path('approvehos/<int:id>', views.approvehos, name='approvehos'),
    path('rejecthos/<int:id>', views.rejecthos, name='rejecthos'),
    path('viewAllHospitalRequest', views.viewAllHospitalRequest, name='viewAllHospitalRequest'),
    path('link_completion', views.link_completion, name='link_completion'),
    path('viewapprovedHospital/<int:id>', views.viewapprovedHospital, name='viewapprovedHospital'),
    path('viewFeedback', views.viewFeedback, name='viewFeedback'),
    path('viewDist', views.viewDist, name='viewDist'),
    path('view_hospital_approved_request', views.view_hospital_approved_request, name='view_hospital_approved_request'),
    path('view_admin_approved_request', views.view_admin_approved_request, name='view_admin_approved_request'),
    path('approveadmin/<int:id>', views.approveadmin, name='approveadmin'),
    path('delete_hospital_request/<int:id>', views.delete_hospital_request, name='delete_hospital_request'),
    path('selectReply/<int:id>', views.selectReply, name='selectReply'),
    path('view_approved_request', views.view_approved_request, name='view_approved_request'),
    path('view_approved', views.view_approved, name='view_approved'),
    path('approveadminsreq', views.approveadminsreq, name='approveadminsreq'),
    path('viewamountcollection', views.viewamountcollection, name='viewamountcollection'),
    path('view_status/<int:patient_id>',views.view_status,name='view_status'),
    path('approve_patient/<int:id>',views.approve_patient),
    path('delete_patient/<int:id>', views.delete_patient, name='delete_patient'),
    path('view_all_completed_amount', views.view_all_completed_amount, name='view_all_completed_amount'),
    path('stop_funding/<id>',views.stop_funding),

    path('stop_amount/<int:id>', views.stop_amount, name='stop_amount'),
#-------------------------------------------HOSPITAL--------------------------------------------------------------------#

    path('register_patient',views.register_patient,name='register_patient'),
    path('view_patients', views.view_patients, name='view_patients'),
    path('hospital_delete_patient/<int:id>', views.hospital_delete_patient, name='hospital_delete_patient'),
    path('view_patient_amount/<int:patient_id>',views.view_patient_amount,name='view_patient_amount'),


    path('viewDistHOSPitAL', views.viewDistHOSPitAL, name='viewDistHOSPitAL'),
    path('addHospital/<int:id>', views.addHospital, name='addHospital'),
    path('approve_req/<int:id>', views.approve_req, name='approve_req'),
    path('complete_request/<int:id>', views.complete_request, name='complete_request'),
    path('reject_req/<int:id>', views.reject_req, name='reject_req'),
    path('approverequirementH/<int:id>', views.approverequirementH, name='approverequirementH'),
    path('approve_cnfirm_req/<int:id>', views.approve_cnfirm_req, name='approve_cnfirm_req'),
    path('view_hospital_requierment', views.view_hospital_requierment, name='view_hospital_requierment'),
    path('view_request', views.view_request, name='view_request'),
    path('viewamountcollectiondetails', views.viewamountcollectiondetails, name='viewamountcollectiondetails'),
    path('view_Hospital_approved_request', views.view_Hospital_approved_request, name='view_Hospital_approved_request'),
    path('view_confirmed_request', views.view_confirmed_request, name='view_confirmed_request'),
    path('view_confirmed', views.view_confirmed, name='view_confirmed'),
    path('delete_requirementH/<int:id>', views.delete_requirementH, name='delete_requirementH'),
    path('viewadminapprovedrequestH', views.viewadminapprovedrequestH, name='viewadminapprovedrequestH'),
    path('hospital_delete_fund_request/<int:id>', views.hospital_delete_fund_request, name='hospital_delete_fund_request'),



path('view_hospital_approved', views.view_hospital_approved, name='view_hospital_approved'),
path('hospital_view_hospital_approved_request', views.hospital_view_hospital_approved_request, name='hospital_view_hospital_approved_request'),
path('link_add_expense/<int:id>', views.link_add_expense, name='link_add_expense'),
path('link_view_category/<int:id>', views.link_view_category, name='link_view_category'),

path('expense_action', views.expense_action, name='expense_action'),
path('resume_fund/<int:id>', views.resume_fund, name='resume_fund'),
path('stop_fund/<int:id>', views.stop_fund, name='stop_fund'),

path('view_completed_funding', views.view_completed_funding, name='view_completed_funding'),

path('next_link', views.next_link, name='next_link'),
path('approve_patient_list',views.approve_patient_list,name='approve_patient_list'),
path('approve_patient/<int:id>',views.approve_patient,name='approve_patient'),
path('hospital_view_donations',views.hospital_view_donations,name='hospital_view_donations'),
path('complete_funding_list',views.complete_funding_list,name='complete_funding_list'),
    path('complete_funding/<int:id>',views.complete_funding,name='complete_funding'),

#---------------------------------------------------------------Donor-----------------------------------------------------------#
    path('DonorHome/',views.DonorHome,name='DonorHome'),
    path('donor_register',views.donor_register,name='donor_registerr'),
    path('view_hospitals',views.view_hospitals,name='view_hospitals'),
    path('donor_view_patients/<int:hospital_id>',views.donor_view_patients,name='donor_view_patitents'),
    path('donor_view_requests',views.donor_view_requests,name='donor_view_requests'),
    path('donate_amount/<int:patient_id>',views.donate_amount),
path('donor_payment',views.donor_payment),

path('payment_success',views.payment_success),
path('admin_view_donors',views.admin_view_donors,name='admin_view_donors'),
path('PatientHome/',views.PatientHome,name='PatientHome'),
path('patient_view_donors',views.patient_view_donors,name='patient_view_donors'),
path('patient_view_collected',views.patient_view_collected,name='patient_view_collected'),
path('patient_send_feedback', views.patient_send_feedback, name='patient_send_feedback'),
path('patient_view_feedback', views.patient_view_feedback, name='patient_view_feedback'),
path('forgot_password', views.forgot_password, name='forgot_password'),
]


