import json
import os
import uuid
from datetime import datetime
import boto3

s3_client = boto3.client('s3')
# In a real stack, the bucket name would be passed via environment variables
S3_BUCKET = os.environ.get('DATA_LAKE_BUCKET', 'biosynapse-datalake-placeholder')

def handler(event, context):
    """
    Cleans, anonymizes, and transforms raw biosignal data (EEG/HRV) 
    from IoT Core into a canonical BioKnowledge Graph node structure.
    """
    
    try:
        data = event
        
        # 1. PII Removal / Anonymization
        record_id = str(uuid.uuid4())
        
        # 2. Feature Calculation (Simulated)
        hrv_raw = data.get('hrv_raw', 0)
        eeg_alpha = data.get('eeg_alpha', 0)
        eeg_beta = data.get('eeg_beta', 1)
        
        # Derived metrics
        cognitive_load_index = eeg_alpha / eeg_beta if eeg_beta > 0 else 0
        stress_index = 100 / (hrv_raw + 1)
        
        # 3. Canonical BioKnowledge Graph Node Format
        processed_data = {
            "node_id": record_id,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "source_layer": "Bio-Cognitive",
            "metrics": {
                "cognitive_load_index": cognitive_load_index,
                "stress_index_hrv": stress_index,
            },
            # Use anonymized location/device ID
            "location_context": data.get('geo_hash', 'unknown') 
        }
        
    except Exception as e:
        print(f"Data processing error: {e}")
        return {"statusCode": 400, "body": json.dumps({"error": "Signal failed preprocessing."})}

    # 4. Store in S3 (Data Core)
    date_path = datetime.utcnow().strftime('%Y/%m/%d')
    s3_key = f"processed/biosignals/{date_path}/{record_id}.json"
    
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(processed_data).encode('utf-8')
        )
        print(f"Successfully stored BioKnowledge Node: {s3_key}")
        return {"statusCode": 200, "body": json.dumps({"message": "Node stored."})}
        
    except Exception as e:
        print(f"S3 upload error: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": "S3 upload failed."})}
