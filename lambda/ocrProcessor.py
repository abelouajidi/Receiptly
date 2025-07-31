import boto3
import json
import urllib.parse
import uuid

s3 = boto3.client('s3')
textract = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ReceiptlyReceipts')

def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    # 1️⃣ Extract bucket & object key from S3 event
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(record['s3']['object']['key'])

    # 2️⃣ Read uploaded image from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response['Body'].read()

    # 3️⃣ Call Textract AnalyzeExpense API for structured receipt extraction
    textract_response = textract.analyze_expense(Document={'Bytes': image_bytes})
    print("RAW TEXTRACT RESPONSE:", json.dumps(textract_response, indent=2))

    # 4️⃣ Extract summary fields
    summary_fields = {}
    for doc in textract_response.get("ExpenseDocuments", []):
        for field in doc.get("SummaryFields", []):
            field_type = field.get("Type", {}).get("Text", "")
            field_value = field.get("ValueDetection", {}).get("Text", "")
            summary_fields[field_type] = field_value

    merchant = summary_fields.get("VENDOR_NAME", "N/A")
    total = summary_fields.get("TOTAL", "N/A")
    currency = summary_fields.get("CURRENCY", "N/A")
    date = summary_fields.get("INVOICE_RECEIPT_DATE", "N/A")  # ✅ No 1970 fallback

    # 5️⃣ Extract line items
    line_items = []
    for doc in textract_response.get("ExpenseDocuments", []):
        for group in doc.get("LineItemGroups", []):
            for item in group.get("LineItems", []):
                entry = {}
                for field in item.get("LineItemExpenseFields", []):
                    f_type = field.get("Type", {}).get("Text", "")
                    f_value = field.get("ValueDetection", {}).get("Text", "")
                    entry[f_type] = f_value
                if entry:
                    line_items.append(entry)

    # 6️⃣ Create final structured JSON
    parsed = {
        "merchant": merchant,
        "total": total,
        "currency": currency,
        "date": date,
        "line_items": line_items
    }

    print("🧾 Parsed Receipt:", json.dumps(parsed, indent=2))

    # 7️⃣ Save JSON in parsed/ folder in S3
    output_key = "parsed/" + key.split("/")[-1].rsplit(".", 1)[0] + ".json"
    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=json.dumps(parsed, indent=2).encode("utf-8"),
        ContentType="application/json"
    )

    # 8️⃣ Save summary in DynamoDB
    try:
        table.put_item(Item={
            "user_id": "default",
            "id": str(uuid.uuid4()),
            "merchant": merchant,
            "total": total,
            "currency": currency,
            "date": date
        })
    except Exception as e:
        print("❌ DynamoDB Error:", str(e))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Receipt processed successfully",
            "output": output_key
        })
    }
