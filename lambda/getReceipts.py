import boto3
import json
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("ReceiptlyReceipts")

def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    # Queryy string parameters (from API Gateway GET request)
    params = event.get("queryStringParameters") or {}
    merchant = params.get("merchant") if params else None
    date = params.get("date") if params else None

    receipts = []

    try:
        if merchant:
            # Query by merchant
            response = table.query(
                IndexName="MerchantIndex",
                KeyConditionExpression=Key("merchant").eq(merchant)
            )
            receipts = response.get("Items", [])

        elif date:
            # Query by date
            response = table.query(
                IndexName="DateIndex",
                KeyConditionExpression=Key("date").eq(date)
            )
            receipts = response.get("Items", [])

        else:
            # No filter → scan the table (not as fast as GSI query)
            response = table.scan()
            receipts = response.get("Items", [])

        # Optional: Sort by date (latest first)
        receipts.sort(key=lambda x: x.get("date", ""), reverse=True)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "count": len(receipts),
                "items": receipts
            })
        }

    except Exception as e:
        print("❌ Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
