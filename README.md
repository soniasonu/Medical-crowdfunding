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
