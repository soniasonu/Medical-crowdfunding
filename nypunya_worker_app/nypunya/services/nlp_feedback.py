"""
Feedback sentiment analysis using NLP (positive/negative count).
Uses TextBlob when available; fallback to simple keyword-based sentiment.
"""
import re

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False

# Fallback: simple positive/negative word lists for sentiment
POSITIVE_WORDS = {
    'good', 'great', 'excellent', 'awesome', 'happy', 'satisfied', 'love',
    'best', 'nice', 'perfect', 'amazing', 'wonderful', 'helpful', 'fast',
    'professional', 'recommend', 'thank', 'thanks', 'pleased', 'quality'
}
NEGATIVE_WORDS = {
    'bad', 'poor', 'terrible', 'worst', 'slow', 'unhappy', 'disappointed',
    'hate', 'awful', 'horrible', 'never', 'waste', 'problem', 'issue',
    'complaint', 'refund', 'cancel', 'delay', 'rude', 'unprofessional'
}


def get_sentiment(text):
    """
    Return 'positive', 'negative', or 'neutral' for the given feedback text.
    """
    if not text or not str(text).strip():
        return 'neutral'
    text = str(text).lower().strip()
    if HAS_TEXTBLOB:
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            if polarity > 0.1:
                return 'positive'
            if polarity < -0.1:
                return 'negative'
            return 'neutral'
        except Exception:
            pass
    # Fallback: count positive/negative words
    words = set(re.findall(r'\b\w+\b', text))
    pos_count = len(words & POSITIVE_WORDS)
    neg_count = len(words & NEGATIVE_WORDS)
    if pos_count > neg_count:
        return 'positive'
    if neg_count > pos_count:
        return 'negative'
    return 'neutral'


def update_feedback_nltk_for_agency(agency_id, feedback_description):
    """
    Update feedback_nltk counts for the given agency based on new feedback.
    Call from views after saving feedback; creates or updates FeedbackNltk row.
    """
    from nypunya.models import FeedbackNltk
    sentiment = get_sentiment(feedback_description)
    row, _ = FeedbackNltk.objects.get_or_create(
        agency_id=agency_id,
        defaults={'positive_count': 0, 'negative_count': 0}
    )
    if sentiment == 'positive':
        row.positive_count = (row.positive_count or 0) + 1
    elif sentiment == 'negative':
        row.negative_count = (row.negative_count or 0) + 1
    row.save()
    return sentiment
