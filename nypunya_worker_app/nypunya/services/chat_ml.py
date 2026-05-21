"""
Simple ML-style chat: intent classification and response generation.
Uses keyword/intent matching; can be extended with sklearn TF-IDF + classifier.
"""
import re

# Intent patterns (keyword/regex) -> response
INTENTS = [
    (r'\b(hi|hello|hey|good morning|good afternoon)\b', 'greeting', 
     "Hello! I'm your Nex-Gen Assistant. How can I help you today? You can ask about work categories, or how to hire a worker."),
    (r'\b(help|support|what can you do)\b', 'help',
     "I can help with: finding plumbers, electricians, or other workers. Try typing 'my light is broken' or 'tap is leaking'."),
    (r'\b(all service|list services|available services|what work|what services)\b', 'all_services',
     "I'm checking our current service catalog for you..."),
    (r'\b(service|categor(y|ies)|type of work|work type)\b', 'categories',
     "We offer various services including Plumbing, Electrical works, Cleaning, and Carpentry. Which one are you looking for?"),
    (r'\b(leakage|leaking|leak|plumber|plumbing|faucet|water|tap|sink|flush)\b', 'workers_plumbing',
     "It sounds like you have a plumbing issue. I'll check for available plumbers for you..."),
    (r'\b(electricity|light|switch|fan|short circuit|wire|plug|electrician)\b', 'workers_electrical',
     "I found some electricians near your location. Here are the top-rated ones:"),
    (r'\b(ac|air condition|cooler|heater|vent|heating|cooling)\b', 'workers_climate',
     "It seems you have a climate control issue. I'll find a technician for you..."),
    (r'\b(brick|wall|cement|floor|plaster|tiles|mason|masonry)\b', 'workers_masonry',
     "It sounds like you need masonry work. I'll find a mason for you..."),
    (r'\b(wood|table|chair|door|window|furniture|jammed|carpenter|carpentry)\b', 'workers_carpentry',
     "It looks like you need a carpenter. I'll check for one for you..."),
    (r'\b(cleaning|sweeping|mop|dust|sweeper|cleaner|maintenance)\b', 'workers_cleaning',
     "It seems you need cleaning or maintenance. I'll find a worker for you..."),
    (r'\b(how to book|booking|book a worker|hire a worker|process)\b', 'booking_info',
     "To book a worker, go to the 'Worker List' page, select your preferred worker, and click the 'Book Now' button. OR I can do it for you! Shall I proceed?"),
    (r'\b(best worker|top rated worker|highest rating)\b', 'best_worker',
     "I'm checking our database for the highest-rated workers..."),
    (r'\b(better|comparison|compare|who is good|which is good|among)\b', 'comparison',
     "I'll compare the ratings and performance based on user history for you..."),
    (r'\b(status|my request|request status|track my job)\b', 'request_status',
     "Checking your recent job requests..."),
    (r'\b(best agency|top agency|highest rated agency)\b', 'best_agency',
     "In this location, we have several top-rated agencies. Checking the leaders..."),
    (r'\b(verify|verified|legit|nexgen|agency verified)\b', 'agency_verification',
     "Yes, our top partners are fully verified. All their workers have completed background checks."),
    (r'\b(which agency|agencies for|who provides)\b', 'agency_for_service',
     "There are several agencies providing specialized services. Checking the list for you..."),
    (r'\b(rate|feedback|review|give rating)\b', 'rate_service',
     "Sure! You can rate your recent services from your dashboard history. Would you like me to help you find your last worker?"),
    (r'\b(register|sign up|registration)\b', 'register',
     "You can register as a User, Agency, or Worker from our Register page."),
    (r'\b(thank|thanks|bye|goodbye)\b', 'bye',
     "You're welcome! Let me know if you need anything else."),
    (r'\b(book|hire|reserve|okay I will book|i want to book)\s+(?:a |the )?([\w\s]{2,})\b', 'final_booking',
     "Processing your booking request..."),
]


def get_response_rnn(user_message):
    """
    Simulated RNN-based intent classifier.
    In a real RNN, word embeddings would be processed sequentially.
    Here we simulate this by analyzing keywords with weighted probabilities.
    """
    if not user_message or not str(user_message).strip():
        return 'unknown', "Please type a message."
    
    text = str(user_message).strip().lower()
    
    # Simulate RNN confidence scores
    best_intent = 'unknown'
    best_score = 0.0
    
    for pattern, intent, response in INTENTS:
        if re.search(pattern, text, re.I):
            # Simulate a high confidence score for matching pattern
            score = 0.85 
            if intent == 'workers_plumbing' and 'leakage' in text:
                score = 0.98 # Higher confidence for specific request
            
            if score > best_score:
                best_score = score
                best_intent = intent
                best_response = response
                
    if best_score > 0.5:
        return best_intent, best_response
        
    return 'unknown', "I'm not sure. Try asking about plumbing, categories, or registration."
