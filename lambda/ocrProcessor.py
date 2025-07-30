import boto3
import json
import urllib.parse
import uuid
from datetime import datetime

s3 = boto3.client('s3')
textract = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ReceiptlyReceipts')

def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    # Extract bucket and object key
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(record['s3']['object']['key'])

    # Get the uploaded image
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response['Body'].read()

    # Use Textract to extract text
    textract_response = textract.detect_document_text(Document={'Bytes': image_bytes})

    lines = [
        block["Text"]
        for block in textract_response["Blocks"]
        if block["BlockType"] == "LINE"
    ]

    print("🔍 LINES:", lines)

    # Basic parsing logic (can be enhanced)
    merchant = lines[0] if lines else "Unknown"
    total = next((line for line in lines if "total" in line.lower()), "Unknown")
    currency = next((line for line in lines if "eur" in line.upper() or "usd" in line.upper()), "EUR")
    date = next((line for line in lines if any(c.isdigit() for c in line) and ("/" in line or "." in line)), "Unknown")

    # Normalize values
    total_clean = total.replace(",", ".").replace("EUR", "").strip()
    date_clean = date.replace(".", "-").replace("/", "-")
    try:
        parsed_date = datetime.strptime(date_clean, "%d-%m-%y").strftime("%Y-%m-%d")
    except Exception:
        parsed_date = "1970-01-01"

    parsed = {
        "merchant": merchant,
        "total": total_clean,
        "currency": currency.strip(),
        "date": parsed_date,
        "lines": lines
    }

    print("🧾 Parsed Receipt:", json.dumps(parsed, indent=2))

    # Save JSON to parsed/ folder
    output_key = "parsed/" + key.split("/")[-1].replace(".jpg", ".json")
    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=json.dumps(parsed, indent=2).encode("utf-8"),
        ContentType="application/json"
    )

    # Save summary to DynamoDB
    try:
        table.put_item(Item={
            "user_id": "default",  # Replace with actual user context if needed
            "date": parsed_date,
            "merchant": merchant,
            "total": total_clean,
            "currency": currency.strip(),
            "id": str(uuid.uuid4())
        })
    except Exception as e:
        print("❌ Failed to write to DynamoDB:", str(e))

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Receipt processed", "output": output_key})
    }
