import os
from flask import Blueprint, request, jsonify
from services.triage_service import classify_triage, get_specialist, is_emergency
from services.voice_service import generate_voice
from services.nlp_service import extract_symptoms_from_text
from predict import predict_disease

predict_bp = Blueprint('predict', __name__)

MEDICINE_SUGGESTIONS = {
    'covid-19': ['Paracetamol 500mg', 'Vitamin C 1000mg', 'Zinc 50mg', 'Rest and hydration'],
    'flu': ['Oseltamivir 75mg', 'Paracetamol 500mg', 'Cetirizine 10mg', 'Warm fluids'],
    'common cold': ['Cetirizine 10mg', 'Paracetamol 500mg', 'Steam inhalation', 'Warm fluids'],
    'bronchitis': ['Salbutamol inhaler', 'Ambroxol 30mg', 'Paracetamol 500mg', 'Rest'],
    'asthma': ['Salbutamol inhaler 100mcg', 'Budesonide inhaler', 'Montelukast 10mg', 'Avoid triggers'],
    'malaria': ['Chloroquine 250mg', 'Paracetamol 500mg', 'ORS for hydration', 'Rest'],
    'typhoid': ['Azithromycin 500mg', 'Paracetamol 500mg', 'ORS fluids', 'Soft diet'],
    'dengue': ['Paracetamol 500mg', 'ORS for hydration', 'Rest', 'Avoid aspirin'],
    'diabetes': ['Metformin 500mg', 'Glibenclamide 5mg', 'Diet control', 'Regular exercise'],
    'heart disease': ['Aspirin 75mg', 'Atorvastatin 20mg', 'Metoprolol 25mg', 'Low salt diet'],
    'heart attack': ['Aspirin 300mg', 'Nitroglycerin', 'Call emergency immediately', 'Oxygen therapy'],
    'hypertension': ['Amlodipine 5mg', 'Losartan 50mg', 'Low salt diet', 'Regular exercise'],
    'gastroenteritis': ['ORS sachets', 'Metronidazole 400mg', 'Probiotics', 'Light diet'],
    'food poisoning': ['ORS sachets', 'Metronidazole 400mg', 'Domperidone 10mg', 'Light diet'],
    'tuberculosis': ['Rifampicin 600mg', 'Isoniazid 300mg', 'Pyrazinamide 1500mg', 'Complete full course'],
    'pneumonia': ['Amoxicillin 500mg', 'Azithromycin 500mg', 'Paracetamol 500mg', 'Rest'],
    'migraine': ['Sumatriptan 50mg', 'Ibuprofen 400mg', 'Rest in dark room', 'Avoid triggers'],
    'arthritis': ['Ibuprofen 400mg', 'Diclofenac gel', 'Calcium supplements', 'Physiotherapy'],
    'hepatitis': ['Tenofovir 300mg', 'Vitamin B complex', 'Avoid alcohol', 'Rest'],
    'kidney disease': ['Furosemide 40mg', 'Amlodipine 5mg', 'Low protein diet', 'Limit fluid intake'],
    'anemia': ['Ferrous sulphate 200mg', 'Folic acid 5mg', 'Vitamin B12 1000mcg', 'Iron rich diet'],
    'thyroid': ['Levothyroxine 50mcg', 'Regular thyroid tests', 'Healthy diet', 'Regular exercise'],
    'viral fever': ['Paracetamol 500mg', 'Cetirizine 10mg', 'ORS fluids', 'Rest'],
    'skin allergy': ['Cetirizine 10mg', 'Hydrocortisone cream 1%', 'Calamine lotion', 'Avoid allergens'],
    'depression': ['Sertraline 50mg', 'Counselling therapy', 'Regular exercise', 'Healthy sleep'],
    'anxiety': ['Alprazolam 0.25mg', 'Counselling therapy', 'Meditation', 'Regular exercise'],
    'urinary tract infection': ['Nitrofurantoin 100mg', 'Ciprofloxacin 500mg', 'Drink plenty of water', 'Cranberry juice'],
    'appendicitis': ['Immediate surgery required', 'Do not take painkillers', 'Go to emergency immediately'],
    'stroke': ['Aspirin 300mg', 'Call emergency immediately', 'Do not give food or water', 'Oxygen therapy'],
}


def validate_analyze_payload(payload):
    required = ['patientInfo', 'duration', 'language']
    for field in required:
        if field not in payload:
            raise ValueError(f'Missing required field: {field}')


@predict_bp.route('/analyze', methods=['POST'])
def analyze():
    payload = request.json or {}
    validate_analyze_payload(payload)

    patient_info = payload.get('patientInfo', {})
    symptoms = payload.get('symptoms') or []
    duration = payload.get('duration', 0)
    free_text = payload.get('freeText', '')
    language = payload.get('language', 'en')

    if not symptoms and free_text:
        symptoms = extract_symptoms_from_text(free_text)

    result = predict_disease(symptoms, duration)
    predictions = result.get('predictions', [])
    top_prediction = predictions[0] if predictions else {}
    disease = top_prediction.get('disease', 'Unknown')
    confidence = top_prediction.get('confidence', 0)
    triage = classify_triage(symptoms, disease, confidence)
    specialist = get_specialist(disease)
    emergency = is_emergency(symptoms)

    audio_url = None
    try:
        medicines_list = MEDICINE_SUGGESTIONS.get(disease.lower(), [])
        medicines_str = ', '.join(medicines_list) if medicines_list else ''
        voice_texts = {
            'ta': f"நோய் கண்டறிதல்: {disease}. நம்பிக்கை: {round(confidence)} சதவீதம். தீவிரநிலை: {triage}. பரிந்துரைக்கப்பட்ட மருத்துவர்: {specialist}. பரிந்துரைக்கப்பட்ட மருந்துகள்: {medicines_str}. தயவுசெய்து தகுதிவாய்ந்த மருத்துவரை அணுகவும்.",
            'te': f"రోగనిర్ధారణ: {disease}. నమ్మకం: {round(confidence)} శాతం. తీవ్రత: {triage}. సిఫార్సు చేయబడిన వైద్యుడు: {specialist}. సిఫార్సు చేయబడిన మందులు: {medicines_str}. దయచేసి అర్హత కలిగిన వైద్యుడిని సంప్రదించండి.",
            'hi': f"निदान: {disease}. विश्वास: {round(confidence)} प्रतिशत. गंभीरता: {triage}. अनुशंसित चिकित्सक: {specialist}. अनुशंसित दवाएं: {medicines_str}. कृपया किसी योग्य चिकित्सक से मिलें।",
            'kn': f"ರೋಗನಿರ್ಣಯ: {disease}. ವಿಶ್ವಾಸ: {round(confidence)} ಶೇಕಡಾ. ತೀವ್ರತೆ: {triage}. ಶಿಫಾರಸು ಮಾಡಲಾದ ವೈದ್ಯರು: {specialist}. ಶಿಫಾರಸು ಮಾಡಲಾದ ಔಷಧಗಳು: {medicines_str}. ದಯವಿಟ್ಟು ಅರ್ಹ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
            'ml': f"രോഗനിർണ്ണയം: {disease}. ആത്മവിശ്വാസം: {round(confidence)} ശതമാനം. തീവ്രത: {triage}. ശുപാർശ ചെയ്യുന്ന ഡോക്ടർ: {specialist}. ശുപാർശ ചെയ്യുന്ന മരുന്നുകൾ: {medicines_str}. ദയവായി യോഗ്യനായ ഡോക്ടറെ സമീപിക്കുക.",
            'en': f"Diagnosis: {disease}. Confidence: {round(confidence)} percent. Triage level: {triage}. Recommended specialist: {specialist}. Recommended medicines: {medicines_str}. Please consult a qualified healthcare professional.",
        }
        voice_text = voice_texts.get(language, voice_texts['en'])
        voice_payload = generate_voice(voice_text, language)
        audio_url = voice_payload.get('audioUrl')
    except Exception:
        audio_url = None

    return jsonify({
        'patientInfo': patient_info,
        'disease': disease,
        'confidence': confidence,
        'top5': predictions,
        'triage': triage,
        'specialist': specialist,
        'medicines': MEDICINE_SUGGESTIONS.get(disease.lower(), []),
        'audioUrl': audio_url,
        'isEmergency': emergency,
    })


@predict_bp.route('/voice-analyze', methods=['POST'])
def voice_analyze():
    payload = request.json or {}
    free_text = payload.get('freeText', '')
    language = payload.get('language', 'en')
    if not free_text:
        return jsonify({'error': 'freeText is required for voice analyze'}), 400

    symptoms = extract_symptoms_from_text(free_text)
    result = predict_disease(symptoms, payload.get('duration', 0))
    predictions = result.get('predictions', [])
    top_prediction = predictions[0] if predictions else {}
    disease = top_prediction.get('disease', 'Unknown')
    confidence = top_prediction.get('confidence', 0)
    triage = classify_triage(symptoms, disease, confidence)
    specialist = get_specialist(disease)

    audio_url = None
    try:
        voice_text = f"Diagnosis: {disease}. Confidence: {round(confidence)} percent. Triage level: {triage}. Please consult a {specialist}."
        audio_payload = generate_voice(voice_text, language)
        audio_url = audio_payload.get('audioUrl')
    except Exception:
        audio_url = None

    return jsonify({
        'disease': disease,
        'confidence': confidence,
        'top5': predictions,
        'triage': triage,
        'specialist': specialist,
        'audioUrl': audio_url,
        'isEmergency': is_emergency(symptoms),
    })


@predict_bp.route('/nlp-extract', methods=['POST'])
def nlp_extract():
    payload = request.json or {}
    free_text = payload.get('freeText', '')
    language = payload.get('language', 'en')
    if not free_text:
        return jsonify({'error': 'freeText is required for NLP extraction'}), 400

    symptoms = extract_symptoms_from_text(free_text)
    return jsonify({'symptoms': symptoms, 'language': language})