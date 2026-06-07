import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

SYMPTOM_FEATURES = [
    'fever', 'cough', 'headache', 'fatigue', 'shortness_of_breath', 'chest_pain', 'nausea', 'vomiting',
    'diarrhea', 'dizziness', 'sore_throat', 'runny_nose', 'muscle_pain', 'joint_pain', 'loss_of_taste',
    'loss_of_smell', 'chills', 'night_sweats', 'weight_loss', 'weight_gain', 'rash', 'itching', 'abdominal_pain',
    'back_pain', 'swelling', 'palpitations', 'confusion', 'anxiety', 'depression', 'insomnia', 'blurred_vision',
    'ear_pain', 'nose_bleed', 'infertility', 'urinary_pain', 'frequent_urination', 'constipation',
    'heartburn', 'short_term_memory_loss', 'tremor', 'seizures', 'breathlessness', 'fainting',
    'cold_sweats', 'high_blood_pressure', 'low_blood_pressure', 'high_blood_sugar', 'low_blood_sugar',
    'swollen_lymph_nodes', 'dry_mouth', 'chest_tightness', 'difficulty_swallowing', 'excessive_thirst',
    'head_pressure', 'abnormal_bleeding'
]

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
BEST_MODEL_PATH = os.path.join(MODEL_DIR, 'best_model.pkl')
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, 'label_encoder.pkl')
FEATURES_PATH = os.path.join(MODEL_DIR, 'features.json')

MODEL_CLASSES = {
    'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
    'RandomForest': RandomForestClassifier(n_estimators=200, random_state=42),
}


def build_features(df):
    for symptom in SYMPTOM_FEATURES:
        df[symptom] = df['symptoms'].apply(lambda text: int(symptom.replace('_', ' ') in text.lower()))

    if 'duration' not in df.columns:
        df['duration'] = 0

    df['duration'] = pd.to_numeric(df['duration'], errors='coerce').fillna(0)
    return df[SYMPTOM_FEATURES + ['duration']]


def load_dataset(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), 'dataset', 'clinical_reports.csv')
    df = pd.read_csv(path)
    if 'symptoms' not in df.columns or 'disease' not in df.columns:
        raise ValueError('Dataset must contain symptoms and disease columns')

    df['symptoms'] = df['symptoms'].astype(str)
    df = df.fillna({'duration': 0})
    X = build_features(df)
    y = df['disease'].astype(str)
    return X, y


def train_model(dataset_path=None):
    if dataset_path is None:
        dataset_path = os.path.join(os.path.dirname(__file__), 'dataset', 'clinical_reports.csv')
    os.makedirs(MODEL_DIR, exist_ok=True)
    X, y = load_dataset(dataset_path)
    encoder = LabelEncoder().fit(y)
    y_encoded = encoder.transform(y)
    y_encoded = y_encoded - y_encoded.min()

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    results = []
    best_score = -1
    best_model = None
    best_name = None

    for name, model in MODEL_CLASSES.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        score = accuracy_score(y_test, preds)
        results.append((name, score))

        if score > best_score:
            best_score = score
            best_model = model
            best_name = name

    print('Model Accuracy Comparison')
    print('---------------------------')
    for name, score in results:
        print(f'{name:20s} {score:.4f}')
    print('---------------------------')
    print(f'Best model: {best_name} with accuracy {best_score:.4f}')

    model_path = BEST_MODEL_PATH
    encoder_path = LABEL_ENCODER_PATH
    features_path = FEATURES_PATH

    import pickle
    with open(model_path, 'wb') as f:
        pickle.dump(best_model, f)

    with open(encoder_path, 'wb') as f:
        pickle.dump(encoder, f)

    with open(features_path, 'w', encoding='utf-8') as f:
        json.dump(SYMPTOM_FEATURES + ['duration'], f, indent=2)

    return best_model, encoder


if __name__ == '__main__':
    train_model()
