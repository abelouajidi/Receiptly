import boto3
import os
import json
import urllib.parse

s3 = boto3.client("s3", region_name="us-east-1")
BUCKET = "elo-receipts"
ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png')

def lambda_handler(event, context):
    params = event.get("queryStringParameters", {})
    filename = params.get("filename")

    if not filename:
        return {
            "statusCode": 400,
            "body": json.dumps({ "error": "Missing 'filename' query parameter" })
        }

    filename = urllib.parse.unquote(filename)
    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        return {
            "statusCode": 400,
            "body": json.dumps({ "error": "Only .jpg, .jpeg, .png files are allowed." })
        }

    object_key = f"uploads/{filename}"

    try:
        # Generate presigned URL without specifying ContentType
        upload_url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': BUCKET,
                'Key': object_key
            },
            ExpiresIn=300
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Allow CORS
                "Content-Type": "application/json"
            },
            "body": json.dumps({ "upload_url": upload_url })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({ "error": str(e) })
        }
