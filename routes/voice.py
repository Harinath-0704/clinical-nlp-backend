import os
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file
from services.voice_service import generate_voice
from firebase.firebase_admin import get_firestore

voice_bp = Blueprint('voice', __name__)

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
VOICE_DIR = BASE_DIR / 'voice'


@voice_bp.route('/generate', methods=['POST'])
def generate():
    payload = request.json or {}
    text = payload.get('text', '')
    language = payload.get('language', 'en')
    if not text:
        return jsonify({'error': 'Text is required to generate audio'}), 400

    result = generate_voice(text, language)
    audio_url = result.get('audioUrl')

    try:
        db = get_firestore()
        db.collection('voice_records').add({
            'patientId': payload.get('patientId', ''),
            'language': language,
            'audioUrl': audio_url,
            'text': text,
            'timestamp': payload.get('timestamp') or None,
        })
    except Exception:
        pass

    return jsonify({'audioUrl': audio_url})


@voice_bp.route('/file/<filename>', methods=['GET'])
def serve_audio(filename):
    file_path = VOICE_DIR / filename
    if not file_path.exists():
        return jsonify({'error': 'Audio file not found'}), 404
    return send_file(str(file_path), mimetype='audio/mpeg')


@voice_bp.route('/download/<record_id>', methods=['GET'])
def download(record_id):
    try:
        db = get_firestore()
        doc = db.collection('voice_records').document(record_id).get()
        if not doc.exists:
            return jsonify({'error': 'Voice record not found'}), 404
        audio_url = doc.to_dict().get('audioUrl')
        if not audio_url:
            return jsonify({'error': 'Audio URL not available'}), 404
        return jsonify({'audioUrl': audio_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500