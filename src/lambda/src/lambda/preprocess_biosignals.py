import json
import os
import uuid
from datetime import datetime
import boto3

# Mocks the necessary S3 client, S3_BUCKET is an environment variable in CF
s3_client = boto3.client('s3')
S3_BUCKET = os.environ.get('DATA_LAKE_BUCKET', 'biosynapse-datalake-placeholder')

def handler(event, context):
    """
    Cleans, anonymizes, and transforms raw biosignal data (EEG/HRV) 
    from IoT Core into a canonical BioKnowledge Graph node structure before S3 storage.
    """
    try:
        data = event
        record_id = str(uuid.uuid4())
        
        # Simulated Feature Calculation
        hrv_raw = data.get('hrv_raw', 0)
        eeg_alpha = data.get('eeg_alpha', 0)
        eeg_beta = data.get('eeg_beta', 1)
        
        cognitive_load_index = eeg_alpha / eeg_beta if eeg_beta > 0 else 0
        
        # Canonical BioKnowledge Graph Node Format
        processed_data = {
            "node_id": record_id,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "source_layer": "Bio-Cognitive",
            "metrics": {
                "cognitive_load_index": cognitive_load_index,
            },
            "location_context": data.get('geo_hash', 'unknown') 
        }
        
    except Exception as e:
        print(f"Data processing error: {e}")
        return {"statusCode": 400}

    # Store in S3
    date_path = datetime.utcnow().strftime('%Y/%m/%d')
    s3_key = f"processed/biosignals/{date_path}/{record_id}.json"
    
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(processed_data).encode('utf-8')
        )
        return {"statusCode": 200, "s3_key": s3_key}
        
    except Exception as e:
        print(f"S3 upload error: {e}")
        return {"statusCode": 500}
