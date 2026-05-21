# Nypunya Worker App

Django app for connecting public users with agencies and workers. Single dashboard view with role-based content, ML chat, and NLP feedback sentiment.

## Modules

- **Admin**: Register categories; approve/reject agencies; view complaints; view feedback with positive/negative counts (NLP).
- **Agency**: View categories; approve/reject workers; view job requests; set amount; assign workers.
- **Worker**: View categories; register with work category; view assigned work.
- **Public User**: Register/login; view categories and agencies; send work requests; view quotation and confirm; send ratings (feedback) and complaints; view workers and send work request.

## Setup

1. **Python & DB**: Python 3.10+, MySQL with existing tables (see your schema).
2. **Install deps**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Admin login**: Ensure table `login` has at least one row, e.g.:
   ```sql
   INSERT INTO login (admin_id, password) VALUES ('admin', 'admin');
   ```
4. **Run**:
   ```bash
   python manage.py runserver
   ```
   Open http://127.0.0.1:8000/

## URLs (single view / dashboard)

- `/` – Home (login/register links)
- `/login/` – Login (role: admin / agency / worker / user)
- `/register/` – Choose role then register (user / agency / worker)
- `/dashboard/` – **Single dashboard** (content depends on role)
- `/chat/` – Chat box (ML intent-based responses)

## Tech

- **Backend**: Django 5, MySQL
- **Chat**: Intent-based ML (keyword/regex → response)
- **Feedback NLP**: Sentiment (positive/negative) via TextBlob or fallback word lists; counts stored in `feedback_nltk`

## Note

Tables `agency` and `assign_worker` are required for the agency module. Add them if not in your DB.
