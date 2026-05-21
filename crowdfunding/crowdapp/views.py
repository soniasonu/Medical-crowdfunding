from urllib import request

from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render, redirect
from requests import session


def index(request):
    return render(request,'HomePage.html')

def AdminHomePage(request):
    return render(request,'Admin/AdminHomePage.html')

def HospitalHome(request):
    return render(request,'Hospital/HospitalHomePage.html')

def UserHome(request):
    return render(request,'User/UserHomePage.html')

def DonorHome(request):
    return render(request,'donor/DonorHomePage.html')
def next_link(request):
    return HttpResponse("<script>alert('ok');window.location='/AdminHomePage';</script>")




def link_completion(request):
    cursor = connection.cursor()
    cursor.execute("select user_fund_request.*,requirements.*,hospitals.name from user_fund_request join requirements join hospitals on user_fund_request.idrequirements=requirements.idrequirements and user_fund_request.idhospitals=hospitals.idhospitals  ")
    pin = cursor.fetchall()
    print(pin)
    return render(request, "Admin/ViewAllApprovedRequest.html", {'data': pin})



def login(request):
    return render(request, "login.html")


# Process login form
from django.shortcuts import redirect
from django.http import HttpResponse
from django.db import connection

def login1(request):
    if request.method == "POST":
        username = request.POST.get('un')
        password = request.POST.get('pass')

        cursor = connection.cursor()

        # -------------------------
        # 1️⃣ Check Admin Login
        # -------------------------
        cursor.execute(
            "SELECT * FROM login WHERE admin_id=%s AND password=%s",
            [username, password]
        )
        admin = cursor.fetchone()

        if admin:
            request.session.flush()
            request.session['lid'] = admin[0]
            request.session['role'] = 'admin'
            return redirect("/AdminHomePage/")

        # -------------------------
        # 2️⃣ Check Hospital Login
        # -------------------------
        cursor.execute(
            "SELECT * FROM hospitals WHERE hospital_id=%s AND password=%s AND status='approve'",
            [username, password]
        )
        hospital = cursor.fetchone()

        if hospital:
            request.session.flush()
            request.session['hid'] = hospital[0]
            request.session['role'] = 'hospital'
            return redirect("/HospitalHome/")

        # -------------------------
        # 3️⃣ Check Donor Login
        # -------------------------
        cursor.execute(
            "SELECT * FROM donor WHERE email=%s AND password=%s",
            [username, password]
        )
        donor = cursor.fetchone()

        if donor:
            request.session.flush()
            request.session['did'] = donor[0]
            request.session['role'] = 'donor'
            return redirect("/DonorHome/")

        # -------------------------
        # 4️⃣ Check Patient Login
        # -------------------------
        cursor.execute(
            "SELECT * FROM patients WHERE name=%s AND password=%s",
            [username, password]
        )
        patient = cursor.fetchone()

        if patient:
            request.session.flush()
            request.session['pid'] = patient[0]
            request.session['role'] = 'patient'
            return redirect("/PatientHome/")

        # -------------------------
        # Invalid Login
        # -------------------------
        return HttpResponse(
            "<script>alert('Invalid Login');window.location='/login/';</script>"
        )

    return redirect("/login/")


def logout(request):
    request.session.flush()
    return redirect('/')


def addCategory(request):
    if request.method == "POST":
        name = request.POST['TxtName']
        cursor = connection.cursor()
        cursor.execute ("insert into category values(null,'" + name + "')")
        
        return HttpResponse("<script>alert('Category Added');window.location='/viewCategory';</script>")
    return render(request,"Admin/addCategory.html")


def viewCategory(request):
    cursor = connection.cursor()
    cursor.execute("select * from category")
    pin = cursor.fetchall()
    print(pin)
    return render(request,"Admin/viewCategory.html",{'data':pin})


# def get_amount_details(request,id):
#     cursor = connection.cursor()
#     request.session["rid"]=id
#     cursor.execute("SELECT SUM(collected_amount.AMOUNT),user_fund_request.required_amount FROM collected_amount join user_fund_request on user_fund_request.iduser_fund_request =collected_amount.iduser_fund_request where collected_amount.iduser_fund_request = '"+id+"' ")
#     pin = cursor.fetchone()
#     d1=pin[0]
#     d2=pin[1]
#     d3=float(d2)-float(d1)
#     print(d3)
#     request.session["b"]=d3
#     print(pin)
#     return render(request,"Admin/ViewAmountStatus.html",{'data':pin} )


def view_status(request, patient_id):

    cursor = connection.cursor()

    # Patient total needed amount
    cursor.execute("""
    SELECT name, amount
    FROM patients
    WHERE patients_id=%s
    """,[patient_id])

    patient = cursor.fetchone()

    if patient is None:
        return HttpResponse("<script>alert('Patient not found');window.location='/AdminHomePage';</script>")

    # Collected amount
    cursor.execute("""
    SELECT IFNULL(SUM(amount),0)
    FROM donation
    WHERE patient_id=%s
    """,[patient_id])

    collected = cursor.fetchone()[0]


    needed = patient[1]

    remaining = int(needed) - int(collected)


    return render(request,
    "Admin/view_status.html",
    {
    'name':patient[0],
    'needed':needed,
    'collected':collected,
    'remaining':remaining
    })


def deleteCategory(request,id):
    cursor = connection.cursor()
    cursor.execute ("delete from category where idcategory='"+str(id)+"'")
    return HttpResponse( "<script>alert('Deleted Successfully');window.location='/viewCategory';</script>")


def stop_amount(request,id):
    cursor = connection.cursor()
    cursor.execute ("update user_fund_request set status='completed' where idcategory='"+str(id)+"'")
    return HttpResponse( "<script>alert('Stopped Successfully...');window.location='/AdminHomePage';</script>")


def view_all_completed_amount(request):
    cursor = connection.cursor()
    cursor.execute("select * from user_fund_request where status='completed'")
    pin = cursor.fetchall()
    print(pin)
    return render(request,"Admin/viewAllHospitalRequest.html",{'data':pin})



def editCategory(request,id):
    cursor = connection.cursor()
    cursor.execute("select name from category where idcategory='" + str(id) + "'")
    pin = cursor.fetchone()
    d=pin[0]
    request.session["d"]=d
    if request.method == "POST":
        name = request.POST['TxtName']
        cursor = connection.cursor()
        cursor.execute("update category set name='" + name + "' where idcategory='" + str(id) + "'")
        return HttpResponse("<script>alert('Updated');window.location='/viewCategory';</script>")
    return render(request,"Admin/editCategory.html")



def viewAllHospitalRequest(request):
    cursor = connection.cursor()
    cursor.execute("select * from hospitals where status='pending'")
    pin = cursor.fetchall()
    print(pin)
    return render(request,"Admin/viewAllHospitalRequest.html",{'data':pin})


def approvehos(request,id):
    cursor = connection.cursor()
    cursor.execute("update hospitals set status='approve' where idhospitals='" + str(id) + "'")
    return redirect("/viewAllHospitalRequest")

def rejecthos(request,id):
    cursor = connection.cursor()
    cursor.execute("update hospitals set status='reject' where idhospitals='" + str(id) + "'")
    return redirect("/viewAllHospitalRequest")



def viewDist(request):
    cursor = connection.cursor()
    cursor.execute("select * from district")
    pin = cursor.fetchall()
    print(pin)
    return render(request,"Admin/viewDist.html",{'data':pin})




def viewapprovedHospital(request,id):
    cursor = connection.cursor()
    cursor.execute("select h.hospital_id,h.name,h.address,h.phone,d.name as district ,h.location from hospitals as h join district as d on h.iddistrict=d.iddistrict where h.status='approve' and h.iddistrict='"+str(id)+"' ")
    pin = cursor.fetchall()
    print(pin)
    return render(request,"Admin/viewapprovedHospital.html",{'data':pin})


def link_add_expense(request,id):
    request.session["cid"]=id
    return render(request,'Hospital/RegisterExpense.html')


def expense_action(request):
    title = request.POST['title']
    details = request.POST['details']
    amount = request.POST['amount']
    req_id=request.session["req_id"]
    cate_id=request.session["cid"]
    hid=request.session['hid']
    cursor = connection.cursor()
    cursor.execute ("insert into user_fund_request values(null,'" + str(req_id) + "',curdate(),'"+ str(cate_id) +"','" + title +"','"+details+"','expense request','not approved','"+str(hid)+"','Hospital approved','"+amount+"' )")
    cursor.execute("update requirements set status='Hospital approved' where idrequirements='" + str(req_id) + "'")

    return HttpResponse("<script>alert('Success...!');window.location='/HospitalHome';</script>")


def link_view_category(request,id):
    cursor = connection.cursor()
    request.session["req_id"]=id
    cursor.execute("select * from category ")
    pin = cursor.fetchall()
    return render(request,'Hospital/SelectCategory.html',{'data':pin})


def viewFeedback(request):
    cursor = connection.cursor()
    cursor.execute("select f.idfeedback,f.user_id,f.title,f.feedback_date,f.reply,f.decsription,u.description,u.title from feedback as f join user_fund_request as u on f.iduser_fund_request=u.iduser_fund_request")
    pin = cursor.fetchall()
    print(pin)
    return render(request,"Admin/viewFeedback.html",{'data':pin})

def selectReply(request,id):
    if request.method == "POST":
        reply = request.POST['TxtReply']
        cursor = connection.cursor()
        cursor.execute ("update feedback set reply='" + reply + "'  where idfeedback='" + str(id) + "'")
        return HttpResponse("<script>alert('Reply Sended');window.location='/viewFeedback';</script>")
    return render(request,"Admin/selectReply.html")


def hospital_view_hospital_approved_request(request):
    cursor = connection.cursor()
    cursor.execute("select * from requirements where status='approved' ")
    pin = cursor.fetchall()
    print(pin)
    return render(request,"Hospital/view_Hospital_approved_request.html",{'data':pin})


def view_hospital_approved_request(request):
    cursor = connection.cursor()
    cursor.execute("SELECT user_fund_request.*,requirements.* FROM user_fund_request join requirements on user_fund_request.idrequirements=requirements.idrequirements where user_fund_request.hospital_status='Hospital approved' and user_fund_request.status='expense request' ")
    pin = cursor.fetchall()
    print(pin)
    return render(request,"Admin/hospitalrequest.html",{'data':pin})


def approveadmin(request,id):
    cursor = connection.cursor()
    cursor.execute("update user_fund_request set status='approved',approved_date=curdate() where iduser_fund_request='" + str(id) + "'")
    return redirect("/view_hospital_approved_request")

def delete_hospital_request(request,id):
    cursor = connection.cursor()
    cursor.execute("delete from user_fund_request where iduser_fund_request='" + str(id) + "'")
    return redirect("/view_hospital_approved_request")


def stop_fund(request,id):
    cursor = connection.cursor()
    cursor.execute("update user_fund_request set status='Completed' where iduser_fund_request='" + str(id) + "'")
    return redirect("/view_hospital_approved_request")


def view_completed_funding(request):
    cursor = connection.cursor()
    cursor.execute("SELECT user_fund_request.*,requirements.* FROM user_fund_request join requirements on user_fund_request.idrequirements=requirements.idrequirements where user_fund_request.status='Completed' ")
    pin = cursor.fetchall()
    print(pin)
    return render(request,"Admin/ViewCompletedFunding.html",{'data':pin})


def resume_fund(request,id):
    cursor = connection.cursor()
    cursor.execute("update user_fund_request set status='approved' where iduser_fund_request='" + str(id) + "'")
    return redirect("/view_completed_funding")


# def view_admin_approved_request(request):
#     cursor = connection.cursor()
#     cursor.execute("SELECT user_fund_request.*,requirements.* FROM user_fund_request join requirements on user_fund_request.idrequirements=requirements.idrequirements where user_fund_request.hospital_status='approved' and user_fund_request.status='Admin approved' ")
#     pin = cursor.fetchall()
#     print(pin)
#     return render(request,"Admin/adminapprovedrequests.html",{'data':pin})

def view_admin_approved_request(request):

    cursor = connection.cursor()

    cursor.execute("""
    SELECT *
    FROM patients
    """)

    data = cursor.fetchall()

    return render(request,
    "Admin/adminapprovedrequests.html",
    {'data':data})

def approve_patient(request,id):

    cursor = connection.cursor()

    cursor.execute("""
    UPDATE patients
    SET funding_status='approved'
    WHERE patients_id=%s
    """,[id])

    return redirect(view_admin_approved_request)

def delete_patient(request,id):

    cursor = connection.cursor()

    cursor.execute("""
    DELETE FROM patients
    WHERE patients_id=%s
    """,[id])

    return redirect(view_admin_approved_request)
def view_approved_request(request):
    cursor = connection.cursor()
    cursor.execute("select * from user_fund_request where hospital_status='Approved' ")
    pin = cursor.fetchall()
    print(pin)
    return render(request,"Admin/view_approved_request.html",{'data':pin})



def approveadminsreq(request,id):
    cursor = connection.cursor()
    cursor.execute("update user_fund_request set status='Approved',approved_date=curdate() where iduser_fund_request='" + str(id) + "'")
    return redirect("/viewAllHospitalRequest")

#
# def view_approved(request):
#     cursor = connection.cursor()
#     cursor.execute("SELECT user_fund_request.*,requirements.* FROM user_fund_request join requirements on user_fund_request.idrequirements=requirements.idrequirements where user_fund_request.hospital_status='Hospital approved' and user_fund_request.status='approved' ")
#     pin = cursor.fetchall()
#     print(pin)
#     return render(request, "Admin/ViewOnGoing.html", {'data': pin})

def view_approved(request):

    cursor = connection.cursor()

    cursor.execute("""
    SELECT 
        p.patients_id,
        p.name,
        p.OT_details,
        p.amount,
        IFNULL(SUM(d.amount),0) as collected,
        p.funding_status
    FROM patients p
    LEFT JOIN donation d
    ON p.patients_id = d.patient_id
    GROUP BY p.patients_id,p.name,p.OT_details,p.amount,p.funding_status
    HAVING collected < p.amount
    """)

    rows = cursor.fetchall()

    data = []

    for row in rows:

        patient_id = row[0]
        name = row[1]
        ot = row[2]

        needed = float(row[3])
        collected = float(row[4])

        remaining = needed - collected
        status = row[5]

        data.append((patient_id,name,ot,needed,collected,remaining,status))


    return render(request,
    "Admin/ViewOnGoing.html",
    {'data':data})

def stop_funding(request,id):

    cursor = connection.cursor()

    cursor.execute("""
    UPDATE patients
    SET funding_status='closed'
    WHERE patients_id=%s
    """,[id])

    return redirect('/view_approved')
def view_approved_panchayat(request):
    cursor = connection.cursor()
    cursor.execute("SELECT user_fund_request.*,requirements.*, hospitals.name FROM user_fund_request join requirements JOIN hospitals ON user_fund_request.idrequirements=requirements.idrequirements AND requirements.idhospitals= hospitals.idhospitals  where user_fund_request.hospital_status='Hospital approved' and user_fund_request.status='approved' ")
    pin = cursor.fetchall()
    print(pin)
    return render(request, "PanchayatHome.html", {'data': pin})





# def viewamountcollection(request):
#     cursor = connection.cursor()
#     cursor.execute("select collected_amount.*,user_fund_request.*,hospitals.name,requirements.name,requirements.address from collected_amount join user_fund_request join hospitals join requirements on collected_amount.iduser_fund_request=user_fund_request.iduser_fund_request and user_fund_request.idhospitals=hospitals.idhospitals and user_fund_request.idrequirements=requirements.idrequirements ")
#     pin = cursor.fetchall()
#     print(pin)
#     return render(request, "Admin/viewamountcollection.html", {'data': pin})

def viewamountcollection(request):

    cursor = connection.cursor()

    cursor.execute("""
    SELECT d.donation_id, p.name, h.name, d.donor_name, d.amount, d.date, d.patient_id
    FROM donation d
    JOIN patients p ON d.patient_id = p.patients_id
    JOIN hospitals h ON p.hospital_id = h.idhospitals
    """)

    data = cursor.fetchall()

    return render(request,
    "Admin/viewamountcollection.html",
    {'data': data})

#---------------------------------------------------------------------------Hospital-----------------------------------------------#

def register_patient(request):
    if 'hid' not in request.session:
        return redirect('/login/')

    if request.method == "POST":
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        ot_details = request.POST.get('ot_details')
        amount= request.POST.get('amount')
        password= request.POST.get('password')

        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO patients (hospital_id, name, age, gender, OT_details, amount, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [request.session['hid'], name, age, gender, ot_details, amount, password])

        return HttpResponse("<script>alert('Patient registered successfully');window.location='/view_patients/';</script>")

    return render(request, 'Hospital/register_patient.html')

def view_patients(request):
    if 'hid' not in request.session:
        return redirect('/login/')

    cursor = connection.cursor()
    cursor.execute("SELECT patients_id, name, age, gender, OT_details,amount FROM patients WHERE hospital_id=%s", [request.session['hid']])
    patients = cursor.fetchall()

    return render(request, 'Hospital/view_patients.html', {'patients': patients})

def hospital_delete_patient(request, id):
    if 'hid' not in request.session:
        return redirect('/login/')
        
    cursor = connection.cursor()
    cursor.execute("DELETE FROM patients WHERE patients_id=%s", [id])
    return redirect("/view_patients")
def view_patient_amount(request, patient_id):

    cursor = connection.cursor()

    # Donation details
    cursor.execute("""
        SELECT donor_name, amount, date
        FROM donation
        WHERE patient_id = %s
    """, [patient_id])

    data = cursor.fetchall()


    # Total amount
    cursor.execute("""
        SELECT SUM(amount)
        FROM donation
        WHERE patient_id = %s
    """, [patient_id])

    total = cursor.fetchone()[0]

    if total is None:
        total = 0


    # Patient name
    cursor.execute("""
        SELECT name
        FROM patients
        WHERE patients_id = %s
    """, [patient_id])

    patient = cursor.fetchone()

    return render(request,"Hospital/view_patient_amount.html",{
        'data':data,
        'total':total,
        'patient':patient
    })

def viewDistHOSPitAL(request):
    cursor = connection.cursor()
    cursor.execute("select * from district")
    pin = cursor.fetchall()
    print(pin)
    return render(request,"Hospital/viewDistHOSPitAL.html",{'data':pin})


def addHospital(request,id):
    if request.method == "POST":
        name = request.POST['TxtName']
        address = request.POST['TxtAddress']
        phone = request.POST['TxtPhone']
        location = request.POST['location']
        hospital_id = request.POST['hospital_id']
        password = request.POST['password']
        cursor = connection.cursor()
        cursor.execute ("insert into hospitals values(null,'" + name + "','" + address + "','" + phone + "','" + str(id) + "','" + location + "','pending','" + hospital_id + "','" + password + "')")
        return HttpResponse("<script>alert('Hospital Registered');window.location='/login';</script>")
    return render(request,"Hospital/addHospital.html")


def view_hospital_requierment(request):
    if 'hid' not in request.session:
        return redirect('/login/')
    x = request.session['hid']
    cursor = connection.cursor()
    cursor.execute("SELECT user_fund_request.*,requirements.* FROM  user_fund_request join requirements on user_fund_request.idrequirements=requirements.idrequirements where user_fund_request.idhospitals='" + str(x) + "' and user_fund_request.hospital_status='Hospital approved' ")
    pin = cursor.fetchall()
    print(pin)
    connection.close()
    return render(request,"Hospital/view_Hospital_approved_request.html",{'data':pin})

def approverequirementH(request,id):
    cursor = connection.cursor()
    cursor.execute("update requirements set status='approved' where idrequirements='" + str(id) + "'")
    connection.close()
    return redirect("/view_hospital_requierment")

def view_Hospital_approved_request(request):
    x = request.session['hid']
    cursor = connection.cursor()
    cursor.execute("select * from requirements where status='hospital approved' and idhospitals='" + str(x) + "' ")
    pin = cursor.fetchall()
    print(pin)
    connection.close()
    return render(request,"Hospital/view_Hospital_approved_request.html",{'data':pin})

def delete_requirementH(request, id):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM requirements WHERE idrequirements=%s", [id])
    return redirect("/view_request")


def viewadminapprovedrequestH(request):
    if 'hid' not in request.session:
        return redirect('/login/')
    x = request.session['hid']
    cursor = connection.cursor()
    cursor.execute("SELECT user_fund_request.*,requirements.* FROM  user_fund_request join requirements on user_fund_request.idrequirements=requirements.idrequirements where user_fund_request.idhospitals='" + str(x) + "' and user_fund_request.status='approved' ")
    pin = cursor.fetchall()
    print(pin)
    connection.close()
    return render(request,"Hospital/viewadminapprovedrequestH.html",{'data':pin})

def hospital_delete_fund_request(request, id):
    if 'hid' not in request.session:
        return redirect('/login/')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM user_fund_request WHERE iduser_fund_request=%s", [id])
    return redirect("/viewadminapprovedrequestH")




def view_hospital_approved(request):
    cursor = connection.cursor()
    x = request.session['hid']
    cursor.execute("select * from requirements where status='hospital approved' and idhospitals='" + str(x) + "'  ")
    pin = cursor.fetchall()
    print(pin)
    connection.close()
    return render(request,"Hospital/viewadminapprovedrequestH.html",{'data':pin})



def view_request(request):
    if 'hid' not in request.session:
        return redirect('/login/')
    x=request.session['hid']
    print(x)
    cursor = connection.cursor()
    print("select * from requirements where status='request' and idhospitals='" + str(x) + "' ")
    cursor.execute("select * from requirements where status='request' and idhospitals='" + str(x) + "' ")
    pin = cursor.fetchall()
    print(pin)
    connection.close()
    return render(request,"Hospital/view_hospital_requierment_approved.html",{'data':pin})


def approve_req(request,id):
    cursor = connection.cursor()
    cursor.execute("update user_fund_request set hospital_status='Hospital approved' where iduser_fund_request='" + str(id) + "'")
    return redirect("/view_request")

def complete_request(request,id):
    cursor = connection.cursor()
    cursor.execute("update user_fund_request set status='complete' where iduser_fund_request='" + str(id) + "'")
    return redirect("/AdminHomePage")



def reject_req(request,id):
    cursor = connection.cursor()
    cursor.execute("delete from  user_fund_request where iduser_fund_request='" + str(id) + "'")
    return redirect("/view_request")



def view_confirmed_request(request):
    if 'hid' not in request.session:
        return redirect('/login/')
    x=request.session['hid']
    cursor = connection.cursor()
    cursor.execute("select * from requirements where status='approved' and idhospitals='" + str(x) + "' ")
    pin = cursor.fetchall()
    print(pin)
    return render(request,"Hospital/view__confirmed_request.html",{'data':pin})

def approve_cnfirm_req(request,id):
    cursor = connection.cursor()
    cursor.execute("update user_fund_request set hospital_status='confirmed' where iduser_fund_request='" + str(id) + "'")
    return redirect("/view_confirmed_request")


def view_confirmed(request):
    x=request.session['hid']
    cursor = connection.cursor()
    cursor.execute("select * from requirements where status='Hospital approved' and idhospitals='" + str(x) + "' ")
    pin = cursor.fetchall()
    print(pin)
    return render(request,"Hospital/view_confirmed.html",{'data':pin})


def viewamountcollectiondetails(request):
    if 'hid' not in request.session:
        return redirect('/login/')
        
    hid = request.session['hid']
    query = request.GET.get('q', '')
    
    cursor = connection.cursor()
    
    sql = """
        SELECT p.name, d.date, d.donor_name, d.amount 
        FROM donation d 
        JOIN patients p ON d.patient_id = p.patients_id 
        WHERE p.hospital_id = %s
    """
    params = [hid]
    
    if query:
        sql += " AND p.name LIKE %s"
        params.append('%' + query + '%')
        
    sql += " ORDER BY d.date DESC"
    
    cursor.execute(sql, params)
    pin = cursor.fetchall()
    return render(request, "Hospital/viewamountcollectiondetails.html", {'data': pin, 'query': query})


def approve_patient_list(request):
    if 'hid' not in request.session:
        return redirect('/login/')
    hid = request.session['hid']

    cursor = connection.cursor()

    cursor.execute("""
    SELECT *
    FROM patients
    WHERE hospital_id=%s
    AND funding_status='pending'
    """,[hid])

    data = cursor.fetchall()

    return render(request,
    'Hospital/approve_patient.html',
    {'data':data})

def approve_patient(request,id):

    cursor = connection.cursor()

    cursor.execute("""
    UPDATE patients
    SET funding_status='open'
    WHERE patients_id=%s
    """,[id])

    return redirect(approve_patient_list)

def hospital_view_donations(request):
    if 'hid' not in request.session:
        return redirect('/login/')
    hid = request.session['hid']

    cursor = connection.cursor()

    cursor.execute("""
    SELECT d.*,p.name
    FROM donation d
    JOIN patients p
    ON d.patient_id=p.patients_id
    WHERE p.hospital_id=%s
    """,[hid])

    data = cursor.fetchall()

    return render(request,
    'Hospital/view_donations.html',
    {'data':data})

def complete_funding_list(request):
    if 'hid' not in request.session:
        return redirect('/login/')
    hid = request.session['hid']

    cursor = connection.cursor()

    cursor.execute("""
    SELECT 
    p.patients_id,
    p.name,
    p.amount,
    IFNULL(SUM(d.amount),0)
    FROM patients p
    LEFT JOIN donation d
    ON p.patients_id=d.patient_id
    WHERE p.hospital_id=%s AND p.funding_status != 'completed'
    GROUP BY p.patients_id,p.name,p.amount
    HAVING SUM(d.amount)>=p.amount
    """,[hid])

    data = cursor.fetchall()

    return render(request,
    'Hospital/complete_funding.html',
    {'data':data})

def complete_funding(request,id):

    cursor = connection.cursor()

    cursor.execute("""
    UPDATE patients
    SET funding_status='completed'
    WHERE patients_id=%s
    """,[id])

    return redirect(complete_funding_list)
#----------------------------------------------------------------------------------Donor--------------------------------------------------------------------------------------------------------#

from datetime import date


def donor_register(request):
    if request.method == "POST":
        name = request.POST['name']
        phone=request.POST['phone']
        email = request.POST['email']
        password = request.POST['password']

        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO donor (name,phone, email, password)
            VALUES (%s, %s, %s,%s)
        """, [name,phone, email, password])

        return redirect('login/')

    return render(request, "donor/donor_register.html")

def donor_home(request):
    if 'did' not in request.session:
        return redirect('/donor_login/')
    return render(request, "donor/home.html")

def view_hospitals(request):

    cursor = connection.cursor()

    cursor.execute("""
    SELECT * FROM hospitals
    WHERE status='approve'
    """)

    data = cursor.fetchall()

    return render(request,'donor/view_hospitals.html',{'data':data})

def donor_view_patients(request,hospital_id):

    cursor = connection.cursor()

    cursor.execute("""
    SELECT * FROM patients
    WHERE hospital_id=%s
    """, [hospital_id])

    data = cursor.fetchall()

    return render(request,'donor/view_patients.html',{'data':data})

def donor_view_requests(request):
    cursor = connection.cursor()
    cursor.execute("""
    SELECT p.patients_id, p.name, p.OT_details, p.amount, h.name 
    FROM patients p 
    JOIN hospitals h ON p.hospital_id = h.idhospitals 
    WHERE p.funding_status='approved'
    """)
    data = cursor.fetchall()
    return render(request,'donor/view_patients.html',{'data':data})

# removed razorpay import


def donate_amount(request, patient_id):

    return render(request,'donor/donate.html',{'patient_id':patient_id})

# razorpay removed - mock payment used instead

def donor_payment(request):
    if request.method == "POST":
        patient_id = request.POST['patient_id']
        amount = request.POST['amount']

        return render(request, 'donor/payment.html', {
            'amount': amount,
            'patient_id': patient_id,
        })
def payment_success(request):

    patient_id = request.POST['patient_id']
    amount = request.POST['amount']
    donor_id = request.session.get('did')

    cursor = connection.cursor()

    # Get donor name
    cursor.execute("""
    SELECT name
    FROM donor
    WHERE donor_id=%s
    """,[donor_id])

    donor_name = cursor.fetchone()[0]


    # Get hospital name using patient_id
    cursor.execute("""
    SELECT h.name
    FROM hospitals h
    JOIN patients p ON p.hospital_id = h.idhospitals
    WHERE p.patients_id=%s
    """,[patient_id])

    hospital_name = cursor.fetchone()[0]


    # Insert donation
    cursor.execute("""
    INSERT INTO donation
    (patient_id, donor_name, hospital_name, amount, date)
    VALUES(%s,%s,%s,%s,CURDATE())
    """,[patient_id, donor_name, hospital_name, amount])


    return render(request,'donor/success.html')

def admin_view_donors(request):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM donor")
    data = cursor.fetchall()
    return render(request, "Admin/view_donors.html", {'data': data})

def PatientHome(request):
    if 'pid' not in request.session:
        return redirect('/login/')
    
    patient_id = request.session['pid']
    cursor = connection.cursor()
    
    # Get total needed
    cursor.execute("SELECT amount FROM patients WHERE patients_id=%s", [patient_id])
    patient_data = cursor.fetchone()
    needed = float(patient_data[0]) if patient_data and patient_data[0] else 0.0
    
    # Get total collected
    cursor.execute("SELECT IFNULL(SUM(CAST(amount AS DECIMAL(10,2))), 0) FROM donation WHERE patient_id=%s", [patient_id])
    collected = float(cursor.fetchone()[0])
    
    remaining = max(0.0, needed - collected)
    
    return render(request, "Patient/PatientHomePage.html", {
        'needed': needed,
        'collected': collected,
        'remaining': remaining
    })

def patient_view_donors(request):
    if 'pid' not in request.session:
        return redirect('/login/')
        
    patient_id = request.session['pid']
    cursor = connection.cursor()
    cursor.execute("SELECT donor_name, amount, date FROM donation WHERE patient_id=%s", [patient_id])
    data = cursor.fetchall()
    
    return render(request, "Patient/view_donors.html", {'data': data})

def patient_view_collected(request):
    if 'pid' not in request.session:
        return redirect('/login/')
        
    patient_id = request.session['pid']
    cursor = connection.cursor()
    
    # Get total collected
    cursor.execute("SELECT IFNULL(SUM(amount), 0) FROM donation WHERE patient_id=%s", [patient_id])
    collected = cursor.fetchone()[0]
    
    # Get specific donations
    cursor.execute("SELECT donor_name, amount, date FROM donation WHERE patient_id=%s ORDER BY date DESC", [patient_id])
    data = cursor.fetchall()
    
    return render(request, "Patient/view_collected_amount.html", {
        'collected': collected,
        'data': data
    })

def patient_send_feedback(request):
    if 'pid' not in request.session:
        return redirect('/login/')
    
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        pid = request.session['pid']
        
        cursor = connection.cursor()
        # Create table if not exists for robustness in this raw-SQL project
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient_feedback (
                feedback_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT,
                title VARCHAR(255),
                description TEXT,
                feedback_date DATE,
                reply TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO patient_feedback (patient_id, title, description, feedback_date, reply)
            VALUES (%s, %s, %s, CURDATE(), 'pending')
        """, [pid, title, description])
            
        return HttpResponse("<script>alert('Feedback sent successfully');window.location='/PatientHome/';</script>")
    
    return render(request, 'Patient/send_feedback.html')

def patient_view_feedback(request):
    if 'pid' not in request.session:
        return redirect('/login/')
    
    pid = request.session['pid']
    cursor = connection.cursor()
    # Check if table exists to prevent crash
    cursor.execute("SHOW TABLES LIKE 'patient_feedback'")
    if cursor.fetchone():
        cursor.execute("SELECT title, description, feedback_date, reply FROM patient_feedback WHERE patient_id=%s", [pid])
        data = cursor.fetchall()
    else:
        data = []
    
    return render(request, "Patient/view_feedback.html", {'data': data})

def forgot_password(request):
    if request.method == "POST":
        username = request.POST['un']
        role = request.POST['role']
        new_pass = request.POST['new_pass']
        verify = request.POST['verify']
        
        cursor = connection.cursor()
        success = False
        
        if role == "Admin":
            # For admin, we just check username and a secret or just reset if we're simple
            cursor.execute("UPDATE login SET password=%s WHERE admin_id=%s", [new_pass, username])
            success = True
        elif role == "Hospital":
            # Verify with phone
            cursor.execute("UPDATE hospitals SET password=%s WHERE hospital_id=%s AND phone=%s", [new_pass, username, verify])
            if cursor.rowcount > 0: success = True
        elif role == "Donor":
            # Verify with phone or email
            cursor.execute("UPDATE donor SET password=%s WHERE email=%s AND phone=%s", [new_pass, username, verify])
            if cursor.rowcount > 0: success = True
        elif role == "Patient":
            # Verify with age (since mobile is missing)
            cursor.execute("UPDATE patients SET password=%s WHERE name=%s AND age=%s", [new_pass, username, verify])
            if cursor.rowcount > 0: success = True
            
        if success:
            return HttpResponse("<script>alert('Password reset successfully');window.location='/login/';</script>")
        else:
            return HttpResponse("<script>alert('Verification failed. Please check your details.');window.location='/forgot_password';</script>")
            
    return render(request, 'forgot_password.html')


import json
from django.http import JsonResponse

def voice_input(request):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text")

        print("User said:", text)

        return JsonResponse({"status": "ok", "text": text})




def voice_form(request):
    return render(request, 'user/SendVoice.html')


import json
from django.http import JsonResponse

def view_agency(request):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text")

        print("Agency request:", text)


        if "plumber" in text.lower():
            result = "Showing plumber agencies"
        else:
            result = "Showing all agencies"

        return JsonResponse({"status": "ok", "message": result})
