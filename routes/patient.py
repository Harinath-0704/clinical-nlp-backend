import io
import csv
from flask import Blueprint, jsonify, request, make_response
from fpdf import FPDF
from firebase.firebase_admin import get_firestore

patient_bp = Blueprint('patient', __name__)


def serialize_document(doc):
    data = doc.to_dict() or {}
    data['id'] = doc.id
    return data


@patient_bp.route('/history/<uid>', methods=['GET'])
def history(uid):
    db = get_firestore()
    docs = db.collection('patient_records').where('patientId', '==', uid).stream()
    records = [serialize_document(doc) for doc in docs]
    return jsonify({'records': records})


@patient_bp.route('/save-record', methods=['POST'])
def save_record():
    payload = request.json or {}
    required = ['patientId', 'name', 'age', 'gender', 'symptoms', 'duration', 'language', 'disease']
    missing = [field for field in required if field not in payload]
    if missing:
        return jsonify({'error': f'Missing fields: {missing}'}), 400

    db = get_firestore()
    record = {
        'patientId': payload['patientId'],
        'name': payload['name'],
        'age': payload['age'],
        'gender': payload['gender'],
        'symptoms': payload['symptoms'],
        'duration': payload['duration'],
        'freeText': payload.get('freeText', ''),
        'language': payload['language'],
        'disease': payload['disease'],
        'confidence': payload.get('confidence', 0),
        'triage': payload.get('triage', ''),
        'specialist': payload.get('specialist', ''),
        'medicines': payload.get('medicines', []),
        'audioUrl': payload.get('audioUrl', ''),
        'timestamp': payload.get('timestamp') or request.args.get('timestamp') or None,
    }
    doc_ref = db.collection('patient_records').add(record)
    return jsonify({'id': doc_ref[1].id, 'record': record})


@patient_bp.route('/download-pdf/<recordId>', methods=['GET'])
def download_pdf(recordId):
    db = get_firestore()
    doc = db.collection('patient_records').document(recordId).get()
    if not doc.exists:
        return jsonify({'error': 'Record not found'}), 404

    record = doc.to_dict() or {}
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Patient Record', ln=True)
    pdf.set_font('Arial', '', 12)

    for key, value in record.items():
        pdf.multi_cell(0, 8, f'{key}: {value}')

    pdf_data = pdf.output(dest='S').encode('latin-1')
    response = make_response(pdf_data)
    response.headers.set('Content-Type', 'application/pdf')
    response.headers.set('Content-Disposition', f'attachment; filename=record_{recordId}.pdf')
    return response


@patient_bp.route('/download-csv/<uid>', methods=['GET'])
def download_csv(uid):
    db = get_firestore()
    docs = db.collection('patient_records').where('patientId', '==', uid).stream()
    records = [serialize_document(doc) for doc in docs]
    if not records:
        return jsonify({'error': 'No records found for patient'}), 404

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(records[0].keys()))
    writer.writeheader()
    writer.writerows(records)

    response = make_response(output.getvalue())
    response.headers.set('Content-Type', 'text/csv')
    response.headers.set('Content-Disposition', f'attachment; filename=patient_{uid}_records.csv')
    return response
