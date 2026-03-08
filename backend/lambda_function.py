import json
import boto3
import urllib.parse
import uuid
import datetime
import hashlib
import re
from boto3.dynamodb.conditions import Key

# AWS Clients
textract = boto3.client('textract')
comprehend = boto3.client('comprehendmedical')
bedrock = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('SamgrahaPatients')


# -------------------------------
# Generate Stable Patient ID
# -------------------------------

def generate_patient_id(name, age):

    cleaned_name = re.sub(r'[^a-zA-Z ]', '', name).lower().strip()
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)

    patient_key = f"{cleaned_name}_{age}"

    hash_value = hashlib.md5(patient_key.encode()).hexdigest()[:8]

    return f"SGH-{hash_value}"


# -------------------------------
# Extract Visit Number
# -------------------------------

def extract_visit_number(lines):

    for line in lines:
        match = re.search(r'consultation\s*#?\s*(\d+)', line.lower())
        if match:
            return int(match.group(1))

    return None


# -------------------------------
# Detect Hospital Name
# -------------------------------

def extract_hospital(lines):

    for line in lines:
        lower = line.lower()

        if "hospital" in lower or "clinic" in lower:
            return line.strip()

    return "Unknown Facility"


# -------------------------------
# Diagnosis Detection
# -------------------------------

def detect_diagnosis(conditions, lines):

    if conditions:
        return ", ".join(conditions)

    keywords = [
        "infection",
        "pain",
        "ache",
        "fever",
        "inflammation",
        "discomfort",
        "syndrome",
        "disease",
        "gastric",
        "respiratory",
        "fracture"
    ]

    for line in lines:
        lower = line.lower()

        for k in keywords:
            if k in lower:
                return line

    return "Diagnosis not clearly detected"


# -------------------------------
# Timeline Change Detection
# -------------------------------

def detect_changes(visits):

    changes = []

    for i in range(1, len(visits)):

        previous = visits[i-1]
        current = visits[i]

        if previous.get("diagnosis") != current.get("diagnosis"):
            changes.append("Diagnosis updated")

        if previous.get("tests") != current.get("tests"):
            changes.append("New diagnostic test added")

        if previous.get("treatment") != current.get("treatment"):
            changes.append("Treatment plan modified")

    return changes


# -------------------------------
# Doctor Insight Mode
# -------------------------------

def generate_doctor_insights(visits):

    insights = []
    diagnosis_text = " ".join([v.get("diagnosis","").lower() for v in visits])

    if diagnosis_text.count("cough") >= 2:
        insights.append("Recurring respiratory symptoms detected")

    if diagnosis_text.count("stomach") >= 2:
        insights.append("Recurring gastrointestinal complaints detected")

    return insights


# -------------------------------
# Clinical Risk Flag
# -------------------------------

def detect_risk(visits):

    diagnosis_text = " ".join([v.get("diagnosis","").lower() for v in visits])

    if diagnosis_text.count("cough") >= 3:
        return "Persistent respiratory symptoms detected — recommend pulmonary evaluation"

    if diagnosis_text.count("abdominal") >= 3 or diagnosis_text.count("stomach") >= 3:
        return "Recurring gastrointestinal symptoms detected — consider gastroenterology evaluation"

    return None


# -------------------------------
# AI Clinical Briefing
# -------------------------------

def generate_clinical_briefing(visits):

    try:

        prompt = f"""
You are assisting a physician.

Based on the following patient visit history,
produce a short clinical briefing.

Focus on:
• Current patient condition
• Key symptoms across visits
• Overall trend
• Recommended follow-up considerations

Patient visit history:

{json.dumps(visits, indent=2)}
"""

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=json.dumps(body)
        )

        result = json.loads(response["body"].read())

        return result["content"][0]["text"]

    except Exception as e:

        print("Bedrock error:", str(e))
        return "Clinical briefing unavailable."


# -------------------------------
# Lambda Handler
# -------------------------------

def lambda_handler(event, context):

    try:

        print("Incoming Event:", json.dumps(event))

        # ===================================================
        # MODE 1 — API Gateway Request
        # ===================================================

        if "Records" not in event:

            print("API Request Mode")

            response = table.scan()
            visits = response.get("Items", [])

            # Ensure timestamp exists for sorting
            for v in visits:
                if "visitTimestamp" not in v:
                    v["visitTimestamp"] = ""

            visits = sorted(visits, key=lambda x: x["visitTimestamp"])

            timeline_changes = detect_changes(visits)
            doctor_insights = generate_doctor_insights(visits)
            risk_flag = detect_risk(visits)
            clinical_briefing = generate_clinical_briefing(visits)

            clinical_alert = None

            if timeline_changes:
                clinical_alert = "New clinical change detected since last visit"

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "timeline_changes": timeline_changes,
                    "doctor_insights": doctor_insights,
                    "risk_flag": risk_flag,
                    "clinical_briefing": clinical_briefing,
                    "clinical_alert": clinical_alert,
                    "visits": visits
                })
            }

        # ===================================================
        # MODE 2 — S3 Prescription Processing
        # ===================================================

        print("S3 Document Processing Mode")

        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

        print(f"Processing document: {key}")

        response = textract.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            }
        )

        lines = []

        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                lines.append(block['Text'])

        print("Extracted Lines:", lines)

        full_text = " ".join(lines)

        conditions = []
        medications = []
        tests = []

        try:

            medical_entities = comprehend.detect_entities_v2(Text=full_text)

            for entity in medical_entities['Entities']:

                category = entity['Category']
                text = entity['Text']

                if category == "MEDICAL_CONDITION":
                    conditions.append(text)

                elif category == "MEDICATION":
                    medications.append(text)

                elif category == "TEST_TREATMENT_PROCEDURE":
                    tests.append(text)

        except Exception as e:
            print("Comprehend Medical error:", str(e))

        patient_name = ""
        age = ""
        follow_up = ""

        for line in lines:

            lower = line.lower()

            if "patient" in lower:

                parts = line.split(":")
                if len(parts) > 1:
                    patient_name = parts[1].strip()

            elif "age" in lower:

                parts = line.split(":")
                if len(parts) > 1:
                    age = parts[1].strip()

            elif "follow" in lower:

                parts = line.split(":")
                if len(parts) > 1:
                    follow_up = parts[1].strip()

        hospital = extract_hospital(lines)
        visit_number = extract_visit_number(lines)
        diagnosis = detect_diagnosis(conditions, lines)
        treatment = medications

        timestamp = datetime.datetime.utcnow().isoformat()
        patient_id = generate_patient_id(patient_name, age)
        visit_id = str(uuid.uuid4())

        table.put_item(
            Item={
                "patientId": patient_id,
                "visitTimestamp": timestamp,
                "visitId": visit_id,
                "visit_number": visit_number,
                "hospital": hospital,
                "patient_name": patient_name,
                "age": age,
                "diagnosis": diagnosis,
                "tests": tests,
                "treatment": treatment,
                "follow_up": follow_up,
                "source_document": key
            }
        )

        print("Visit stored successfully")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Document processed successfully",
                "patientId": patient_id
            })
        }

    except Exception as e:

        print("Lambda execution error:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Samgraha processing failed",
                "details": str(e)
            })
        }
