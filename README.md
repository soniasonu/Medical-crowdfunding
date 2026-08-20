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
![Home Page](https://github.com/user-attachments/assets/14a2b613-e8d8-4b2f-b5a4-eb4a22ce30d5)
![Login](https://github.com/user-attachments/assets/5e396c57-7883-41ba-bd88-688b1aee27f5)
![Admin dashboard](https://github.com/user-attachments/assets/ab77f50f-c35d-4f13-939d-3579d7ecada9)
![Patient Funding Approval](https://github.com/user-attachments/assets/0e2e0691-88fc-41ee-ac91-da0f857bf4e8)
![Registered Donors](https://github.com/user-attachments/assets/8b12fc67-92a6-412e-b5e9-8c19798ca1a7)
![Hospital dashboard](https://github.com/user-attachments/assets/ae37b9fa-60e5-43f9-b307-a6df66942887)
![Patient Details](https://github.com/user-attachments/assets/0357dd1e-2d79-446f-b039-8b6632b566cd)
![Donor Registration](https://github.com/user-attachments/assets/6b4f020c-017e-4d33-9b2e-ce4df3d73fc8)
![Patient Portal Dashboard](https://github.com/user-attachments/assets/b26530ee-b6ef-4b3d-ae38-76a81f919a41)



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
