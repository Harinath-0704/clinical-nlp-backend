import io
import csv
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, make_response
from firebase.firebase_admin import get_firestore

admin_bp = Blueprint('admin', __name__)


def serialize_document(doc):
    data = doc.to_dict() or {}
    data['id'] = doc.id
    return data


@admin_bp.route('/stats', methods=['GET'])
def stats():
    try:
        db = get_firestore()
        users = list(db.collection('users').stream())
        predictions = list(db.collection('patient_records').stream())
        emergencies = list(db.collection('emergency_cases').stream())

        return jsonify({
            'totalPatients': len(users),
            'totalPredictions': len(predictions),
            'activeEmergencies': len(emergencies),
            'activeUsers': len(users),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/patients', methods=['GET'])
def patients():
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        search = request.args.get('search', '').lower()

        db = get_firestore()
        docs = list(db.collection('users').stream())
        all_patients = [serialize_document(doc) for doc in docs]

        if search:
            all_patients = [
                p for p in all_patients
                if search in str(p.get('name', '')).lower()
                or search in str(p.get('email', '')).lower()
            ]

        start = (page - 1) * size
        end = start + size
        return jsonify({
            'page': page,
            'size': size,
            'total': len(all_patients),
            'patients': all_patients[start:end],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/records', methods=['GET'])
def records():
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        search = request.args.get('search', '').lower()

        db = get_firestore()
        docs = list(db.collection('patient_records').stream())
        all_records = [serialize_document(doc) for doc in docs]
        all_records.sort(key=lambda r: r.get('timestamp', ''), reverse=True)

        if search:
            all_records = [
                r for r in all_records
                if search in str(r.get('name', '')).lower()
                or search in str(r.get('disease', '')).lower()
            ]

        start = (page - 1) * size
        end = start + size
        return jsonify({
            'page': page,
            'size': size,
            'total': len(all_records),
            'records': all_records[start:end],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/record/<record_id>', methods=['DELETE'])
def delete_record(record_id):
    try:
        db = get_firestore()
        doc_ref = db.collection('patient_records').document(record_id)
        if not doc_ref.get().exists:
            return jsonify({'error': 'Record not found'}), 404
        doc_ref.delete()
        return jsonify({'message': 'Record deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/analytics', methods=['GET'])
def analytics():
    try:
        db = get_firestore()
        all_records = [doc.to_dict() or {} for doc in db.collection('patient_records').stream()]

        disease_counts = {}
        language_counts = {}
        monthly_counts = {}
        triage_counts = {}
        symptom_counts = {}

        for record in all_records:
            disease = record.get('disease', 'Unknown')
            language = record.get('language', 'en')
            triage = record.get('triage', 'UNKNOWN')
            symptoms = record.get('symptoms', [])
            timestamp = record.get('timestamp', '')

            disease_counts[disease] = disease_counts.get(disease, 0) + 1
            language_counts[language] = language_counts.get(language, 0) + 1
            triage_counts[triage] = triage_counts.get(triage, 0) + 1

            if not isinstance(symptoms, list):
                symptoms = [s.strip() for s in str(symptoms).split(',') if s.strip()]
            for symptom in symptoms:
                symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1

            try:
                record_date = datetime.fromisoformat(timestamp)
                month_key = record_date.strftime('%Y-%m')
                monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
            except Exception:
                pass

        return jsonify({
            'diseaseDistribution': disease_counts,
            'languageUsage': language_counts,
            'monthlyPredictions': monthly_counts,
            'triageDistribution': triage_counts,
            'symptomCounts': symptom_counts,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/export-csv', methods=['GET'])
def export_csv():
    try:
        db = get_firestore()
        all_records = [serialize_document(doc) for doc in db.collection('patient_records').stream()]
        if not all_records:
            return jsonify({'error': 'No records to export'}), 404

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(all_records[0].keys()))
        writer.writeheader()
        writer.writerows(all_records)

        response = make_response(output.getvalue())
        response.headers.set('Content-Type', 'text/csv')
        response.headers.set('Content-Disposition', 'attachment; filename=patient_records.csv')
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500