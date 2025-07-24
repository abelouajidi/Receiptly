import boto3
import json
import urllib.parse
import re

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    # Extract S3 info
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(record['s3']['object']['key'])

    # Get image from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response['Body'].read()

    # Detect text
    text_result = rekognition.detect_text(Image={'Bytes': image_bytes})
    lines = [d['DetectedText'] for d in text_result['TextDetections'] if d['Type'] == 'LINE']

    print("🔍 LINES:", lines)

    # ---- Extract Fields ----

    # Merchant (first line)
    merchant = lines[0] if lines else "Unknown"

    # Total amount
    total = next((l for l in lines if re.search(r'\b(19[,.]96|Total[: ]*19[,.]96)', l, re.IGNORECASE)), None)
    if total:
        total_amount = re.search(r'(\d+[,.]\d{2})', total).group(1).replace(",", ".")
    else:
        total_amount = "Unknown"

    # Date (matches dd.mm.yy or dd-mm-yy)
    date_match = next((re.search(r'\d{2}[./-]\d{2}[./-]\d{2,4}', l) for l in lines if re.search(r'\d{2}[./-]\d{2}[./-]\d{2,4}', l)), None)
    receipt_date = date_match.group(0) if date_match else "Unknown"

    # Return structured result
    result = {
        'merchant': merchant,
        'total': total_amount,
        'date': receipt_date,
        'currency': 'EUR',
        'lines': lines
    }

    print("🧾 Parsed Receipt:", json.dumps(result, indent=2))
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
