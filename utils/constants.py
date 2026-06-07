DEFAULT_LANGUAGE = 'en'
SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de', 'zh', 'ar']
CLINICAL_FIELDS = ['symptoms', 'diagnosis', 'triage', 'notes']

MEDICINE_DB = {
	"Dengue": [
		{"name": "Paracetamol", "dose": "500mg every 4-6h (max 4g/day)"},
		{"name": "Oral Rehydration Salts", "dose": "As needed"}
	],
	"Malaria": [
		{"name": "Artemisinin-based combo", "dose": "Follow local guidelines"},
		{"name": "Paracetamol", "dose": "500mg every 4-6h"}
	],
	"Typhoid": [
		{"name": "Azithromycin", "dose": "500mg once daily (adult)"},
		{"name": "Oral Rehydration", "dose": "As needed"}
	],
	"COVID-19": [
		{"name": "Paracetamol", "dose": "500mg every 4-6h"},
		{"name": "Rest & Hydration", "dose": "Supportive"}
	],
	"Viral Fever": [
		{"name": "Paracetamol", "dose": "500mg every 4-6h"}
	],
	"Pneumonia": [
		{"name": "Amoxicillin", "dose": "500mg every 8h (adult)"}
	],
	"Tuberculosis": [
		{"name": "Isoniazid/Rifampicin/Ethambutol/Pyrazinamide", "dose": "Per national TB program"}
	],
	"Diabetes": [
		{"name": "Metformin", "dose": "500mg twice daily"}
	],
	"Hypertension": [
		{"name": "Amlodipine", "dose": "5mg once daily"}
	],
	"Heart Disease": [
		{"name": "Aspirin", "dose": "75-100mg once daily (if indicated)"}
	],
	"Stroke": [
		{"name": "Aspirin", "dose": "75-100mg once daily (if indicated)"}
	],
	"Asthma": [
		{"name": "Salbutamol inhaler", "dose": "2 puffs as needed"}
	],
	"Kidney Disease": [
		{"name": "ACE inhibitor (specialist)", "dose": "Per specialist"}
	],
	"Liver Disease": [
		{"name": "Avoid hepatotoxic drugs", "dose": "Supportive care"}
	],
	"Gastroenteritis": [
		{"name": "Oral Rehydration Salts", "dose": "As needed"}
	],
	"Migraine": [
		{"name": "Ibuprofen", "dose": "400mg as needed"}
	],
	"Anemia": [
		{"name": "Ferrous sulfate", "dose": "200mg once or twice daily"}
	],
	"Arthritis": [
		{"name": "Ibuprofen", "dose": "200-400mg as needed"}
	],
	"Depression": [
		{"name": "Refer to mental health specialist", "dose": "N/A"}
	],
	"Skin Allergy": [
		{"name": "Antihistamine (Cetirizine)", "dose": "10mg once daily"},
		{"name": "Topical hydrocortisone", "dose": "Apply as directed"}
	]
}

SPECIALIST_MAP = {
	"Dengue": "Infectious Disease",
	"Malaria": "Infectious Disease",
	"Typhoid": "Infectious Disease",
	"COVID-19": "Infectious Disease",
	"Viral Fever": "Primary Care",
	"Pneumonia": "Respiratory",
	"Tuberculosis": "Respiratory",
	"Diabetes": "Endocrinology",
	"Hypertension": "Cardiology",
	"Heart Disease": "Cardiology",
	"Stroke": "Neurology",
	"Asthma": "Respiratory",
	"Kidney Disease": "Nephrology",
	"Liver Disease": "Hepatology",
	"Gastroenteritis": "Gastroenterology",
	"Migraine": "Neurology",
	"Anemia": "Hematology",
	"Arthritis": "Rheumatology",
	"Depression": "Psychiatry",
	"Skin Allergy": "Dermatology"
}

EMERGENCY_SYMPTOMS = [
	"chest pain", "shortness of breath", "severe bleeding", "loss of consciousness",
	"sudden weakness", "slurred speech", "facial droop", "severe abdominal pain",
	"severe allergic reaction", "uncontrolled bleeding"
]

LANGUAGE_CODES = {
	"English": "en",
	"Spanish": "es",
	"French": "fr",
	"Hindi": "hi",
	"Bengali": "bn",
	"Arabic": "ar",
	"Portuguese": "pt",
	"Swahili": "sw",
	"Mandarin": "zh",
	"Tamil": "ta"
}

TRIAGE_RULES = {
	# Scores or thresholds used by the triage component
	"high": {
		"min_severity": 8,
		"emergency_symptoms": EMERGENCY_SYMPTOMS
	},
	"medium": {
		"min_severity": 4
	},
	"low": {
		"min_severity": 0
	}
}
