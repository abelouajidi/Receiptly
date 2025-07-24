import boto3
import json
import urllib.parse

s3 = boto3.client('s3')
textract = boto3.client('textract')

def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    # Get bucket and file info
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(record['s3']['object']['key'])

    # Get image bytes
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response['Body'].read()

    # Run OCR
    textract_response = textract.detect_document_text(Document={'Bytes': image_bytes})

    # Extract lines
    lines = [
        item["DetectedText"]
        for item in textract_response.get("Blocks", [])
        if item["BlockType"] == "LINE"
    ]
    print("🔍 LINES:", lines)

    # Rough parsing
    parsed = {
        "merchant": lines[0] if lines else "Unknown",
        "total": next((line for line in lines if "total" in line.lower()), "Unknown"),
        "date": "Unknown",  # you can improve this later with regex
        "currency": "EUR" if "EUR" in " ".join(lines) else "Unknown",
        "lines": lines
    }
    print("🧾 Parsed Receipt:", json.dumps(parsed, indent=2))

    # Output to S3
    output_key = "parsed/" + key.split("/")[-1].replace(".jpg", ".json")
    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=json.dumps(parsed, indent=2).encode('utf-8'),
        ContentType='application/json'
    )

    return {
        "statusCode": 200,
        "body": f"Parsed receipt saved to s3://{bucket}/{output_key}"
    }
