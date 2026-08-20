# HelpHub — Medical Crowdfunding Platform

## Problem

Many patients are unable to afford medical treatment due to financial limitations. Existing fundraising options — social media, individual charity organizations, offline fundraising — are not centralized, lack proper monitoring, and have no structured way to verify patient requirements or track where donations actually go.

## Solution

HelpHub is a web-based medical crowdfunding platform that connects hospitals and patients in need of financial support with donors willing to contribute toward treatment costs, with a structured approval process in between.

**Modules:**
- **Admin** — approves and monitors fund requests, views donation details and funding progress, manages donors and receivers
- **Hospital** — registers on the platform, registers patients with treatment details, forwards fund requests to Admin for approval, and tracks funded patients
- **Public User (Donor)** — views active campaigns, donates, sends feedback, and tracks donation history

**Key features:**
- Centralized, structured fund request flow: Hospital submits → Admin verifies and records → Donors give → Admin confirms and analyzes
- Real-time donation tracking and a centralized database for campaigns and donations

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Django Framework
- **Database:** MySQL Server

## Screenshots
**Home Page**
<img width="600" alt="image" src="https://github.com/user-attachments/assets/d29fbd07-59a5-42b7-973e-59c59f33e575" />
**Login**
<img width="600" alt="image" src="https://github.com/user-attachments/assets/15eaec22-6c59-47d1-a1a6-2718d48f8ac7" />
**Admin Dashboard**
<img width="600" alt="image" src="https://github.com/user-attachments/assets/eaeee670-b3c2-4273-823d-9abb2c7c6e61" />
**Patient Funding Approval**
<img width="600" alt="image" src="https://github.com/user-attachments/assets/35aeeef5-adb1-4edb-afff-7f57d7e1e551" />
**Registered Donors**
<img width="600" alt="image" src="https://github.com/user-attachments/assets/9077dfde-701b-491b-af7e-d96ae2addb13" />
**Hospital Dashboard**
<img width="600" alt="image" src="https://github.com/user-attachments/assets/87a9f87f-7b7f-4063-8039-69619574277c" />
**Patient Details**
<img width="600" alt="image" src="https://github.com/user-attachments/assets/4567526d-c1ee-4459-a52d-d3e6defdb8f5" />
**Donor Registration**
<img width="600" alt="image" src="https://github.com/user-attachments/assets/b6518f12-efe4-4988-aa68-134817c7f9cc" />
**Patient Portal Dashboard**
<img width="600" alt="image" src="https://github.com/user-attachments/assets/404b6c84-55e9-43c1-b467-14a6ee6c8117" />


## Future Improvements

- Mobile application (Android and iOS) for easier access
- Real-time notification system — SMS and email alerts for donation updates
- Multilingual support for wider reach
- Chatbot assistance — AI chatbot to guide users during donation
- Subscription-based donations (monthly or yearly recurring)
- Emergency case prioritization — auto-highlight urgent medical cases

### How to Run
pip install django
python manage.py runserver

Then open http://127.0.0.1:8000

-- Academic Project --
