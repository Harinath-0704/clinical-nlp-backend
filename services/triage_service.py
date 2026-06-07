def is_emergency(symptoms_list):
    emergency_indicators = {
        'heart attack', 'stroke', 'shortness of breath', 'chest pain', 'palpitations',
        'confusion', 'fainting', 'seizures', 'breathlessness', 'chest tightness'
    }
    return any(symptom.lower() in emergency_indicators for symptom in symptoms_list)


def get_specialist(disease):
    disease = disease.lower()
    if 'cardiac' in disease or 'heart' in disease or 'stroke' in disease:
        return 'Cardiologist'
    if 'lung' in disease or 'respiratory' in disease or 'asthma' in disease:
        return 'Pulmonologist'
    if 'diabetes' in disease or 'endocrine' in disease:
        return 'Endocrinologist'
    if 'infection' in disease or 'fever' in disease or 'viral' in disease:
        return 'Infectious Disease Specialist'
    if 'skin' in disease or 'dermat' in disease or 'rash' in disease:
        return 'Dermatologist'
    if 'mental' in disease or 'anxiety' in disease or 'depression' in disease:
        return 'Psychiatrist'
    return 'General Practitioner'


def classify_triage(symptoms, disease, confidence):
    urgency_score = 0
    if is_emergency(symptoms):
        urgency_score += 3
    if confidence >= 85:
        urgency_score += 2
    if disease and any(keyword in disease.lower() for keyword in ['stroke', 'heart attack', 'sepsis', 'pneumonia']):
        urgency_score += 2
    if any(symptom.lower() in {'fever', 'vomiting', 'diarrhea', 'chest pain'} for symptom in symptoms):
        urgency_score += 1

    if urgency_score >= 5:
        return 'EMERGENCY'
    if urgency_score >= 3:
        return 'HIGH'
    if urgency_score >= 1:
        return 'MODERATE'
    return 'NON_URGENT'
