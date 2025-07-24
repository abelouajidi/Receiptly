import boto3
import json
import urllib.parse

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')


def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    # Get S3 bucket and file key
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(record['s3']['object']['key'])

    # Download image
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response['Body'].read()

    # Call Rekognition OCR
    text_result = rekognition.detect_text(Image={'Bytes': image_bytes})
    lines = [d['DetectedText'] for d in text_result['TextDetections'] if d['Type'] == 'LINE']

    print("RECEIPT TEXT:")
    for line in lines:
        print(line)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'lines': lines
        })
    }

