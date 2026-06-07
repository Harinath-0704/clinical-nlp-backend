import re
from deep_translator import GoogleTranslator

SUPPORTED_LANGUAGES = {
    'ta': 'tamil',
    'te': 'telugu',
    'hi': 'hindi',
    'kn': 'kannada',
    'ml': 'malayalam',
    'en': 'english',
}

SYMPTOM_KEYWORDS = [
    'fever', 'cough', 'headache', 'fatigue', 'shortness of breath', 'chest pain', 'nausea',
    'vomiting', 'diarrhea', 'dizziness', 'sore throat', 'runny nose', 'muscle pain', 'joint pain',
    'loss of taste', 'loss of smell', 'chills', 'night sweats', 'weight loss', 'weight gain',
    'rash', 'itching', 'abdominal pain', 'back pain', 'swelling', 'palpitations', 'confusion',
    'anxiety', 'depression', 'insomnia', 'blurred vision', 'ear pain', 'nose bleed', 'urinary pain',
    'frequent urination', 'constipation', 'heartburn', 'tremor', 'seizures', 'breathlessness',
    'fainting', 'cold sweats', 'high blood pressure', 'low blood pressure', 'high blood sugar',
    'low blood sugar', 'swollen lymph nodes', 'dry mouth', 'difficulty swallowing', 'chest tightness',
    'excessive thirst', 'abnormal bleeding'
]

TRANSLATION_MAP = {
    'ta': 'tamil',
    'te': 'telugu',
    'hi': 'hindi',
    'kn': 'kannada',
    'ml': 'malayalam',
    'en': 'english',
}


def detect_language(text):
    if not text or not text.strip():
        return 'en'
    try:
        detected = GoogleTranslator(source='auto', target='en').detect(text)
        for code, name in SUPPORTED_LANGUAGES.items():
            if name.lower() in detected.lower() or code == detected:
                return code
    except Exception:
        pass

    text_lower = text.lower()
    if re.search(r'[கஙசஞடணதநபமயரலவஷஸஹ]', text_lower):
        return 'ta'
    if re.search(r'[టఠడఢణతథదధనపఫబభమయరలవశషసహ]', text_lower):
        return 'te'
    if re.search(r'[अआइईउऊएऐओऔ]', text_lower):
        return 'hi'
    if re.search(r'[ಅಆಇಈಉಊಋಎಏಐಒಓಔ]', text_lower):
        return 'kn'
    if re.search(r'[അആഇഈഉഊഎഐഒഓഔ]', text_lower):
        return 'ml'
    return 'en'


def translate_to_english(text, source_lang='en'):
    if not text or source_lang == 'en':
        return text

    try:
        translator = GoogleTranslator(source=source_lang, target='en')
        return translator.translate(text)
    except Exception:
        return text


def clean_text(text):
    cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def extract_symptoms_from_text(text):
    if not text:
        return []

    language = detect_language(text)
    english_text = translate_to_english(text, language)
    cleaned = clean_text(english_text)

    found = set()
    for keyword in SYMPTOM_KEYWORDS:
        pattern = re.escape(keyword.lower())
        if re.search(rf'\b{pattern}\b', cleaned):
            found.add(keyword)

    return sorted(found)


def detect_severity(symptoms_list):
    if not symptoms_list:
        return 'LOW'

    high_risk = {'chest pain', 'shortness of breath', 'palpitations', 'confusion', 'seizures', 'fainting'}
    medium_risk = {'fever', 'dizziness', 'vomiting', 'diarrhea', 'abdominal pain', 'breathlessness'}

    if any(symptom in high_risk for symptom in symptoms_list):
        return 'CRITICAL'
    if any(symptom in medium_risk for symptom in symptoms_list):
        return 'HIGH'
    if len(symptoms_list) >= 4:
        return 'MEDIUM'
    return 'LOW'
