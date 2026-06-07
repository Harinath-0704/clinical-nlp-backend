import json
import os
import pickle
import numpy as np
from services.nlp_service import extract_symptoms_from_text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'best_model.pkl')
LABEL_ENCODER_PATH = os.path.join(BASE_DIR, 'models', 'label_encoder.pkl')
FEATURES_PATH = os.path.join(BASE_DIR, 'models', 'features.json')


def load_model():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(LABEL_ENCODER_PATH) or not os.path.exists(FEATURES_PATH):
        raise FileNotFoundError('Model, encoder, or features file not found. Run train_model.py first.')

    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)

    with open(LABEL_ENCODER_PATH, 'rb') as f:
        encoder = pickle.load(f)

    with open(FEATURES_PATH, 'r', encoding='utf-8') as f:
        features = json.load(f)

    return model, encoder, features


def build_feature_vector(symptoms_list, duration_days, features):
    symptom_set = {symptom.lower().replace(' ', '_') for symptom in symptoms_list}
    values = []
    for feature in features:
        if feature == 'duration':
            values.append(float(duration_days or 0))
        else:
            values.append(1.0 if feature in symptom_set else 0.0)
    return np.array(values).reshape(1, -1)


def predict_disease(symptoms_list, duration_days=0):
    model, encoder, features = load_model()
    x = build_feature_vector(symptoms_list, duration_days, features)

    probabilities = model.predict_proba(x)[0]
    top5_idx = np.argsort(probabilities)[::-1][:5]
    top_diseases = encoder.inverse_transform(top5_idx)
    confidences = probabilities[top5_idx] * 100

    return format_predictions(top_diseases, confidences)


def format_predictions(diseases, confidences):
    return {
        'predictions': [
            {
                'disease': disease,
                'confidence': round(float(confidence), 2),
            }
            for disease, confidence in zip(diseases, confidences)
        ]
    }


if __name__ == '__main__':
    sample_symptoms = ['fever', 'cough', 'fatigue']
    print(predict_disease(sample_symptoms, 4))
