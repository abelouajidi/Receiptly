🔹 Title & Description

    Receiptly — Smart Receipt OCR + Expense Tracker:
    
        - Upload any receipt through a modern web UI and instantly get a structured JSON summary with merchant, items, 
          total, currency, and date — powered by AWS Textract’s analyze_expense API, serverless Lambda functions, and DynamoDB storage.
        - Future‑ready with CI/CD, history tracking, and planned analytics dashboard.

🔹 Demo

    - Live frontend: [S3 Hosted Frontend Link]

🔹 Architecture Overview

    - Upload receipt via web frontend
    - Frontend requests a pre‑signed S3 URL from API Gateway
    - Receipt image uploaded directly to S3 (uploads/)
    - S3 event triggers ocrProcessor Lambda
    - AWS Textract (analyze_expense) extracts structured receipt data
    - Custom parser cleans and formats data into structured JSON
    - Parsed JSON saved to parsed/ folder in the same S3 bucket
    - Summary record (merchant, date, total, currency) stored in DynamoDB
    - getReceipts Lambda fetches receipts by merchant/date using GSIs
    - Planned: Dashboard for analytics, filtering, and CSV export

🔹 Technologies Used

    - AWS S3 — Receipt storage (uploads & parsed data)
    - AWS Lambda — Serverless OCR processing (ocrProcessor) + query API (getReceipts)
    - AWS Textract — analyze_expense for structured OCR data
    - AWS DynamoDB — Persistent structured receipt data + GSIs (Merchant & Date)
    - AWS API Gateway — REST API for upload & receipt queries
    - GitHub Actions — CI/CD for automated Lambda deployments
    - IAM & CloudWatch — Permissions and logging
    - HTML/CSS/JavaScript — Responsive upload UI

🔹 Example Output

        {
          "merchant": "Berghotel",
          "total": "54.50",
          "currency": "CHF",
          "date": "30-07-2007",
          "line_items": [
            { "item": "Latte Macchiato", "price": "4.50" },
            { "item": "Schweinschnitzel", "price": "22.00" }
          ]
        }

🔹 Future Enhancements

    - Dashboard UI: KPIs, filters, and Chart.js analytics
    - CSV export from dashboard
    - User authentication for multi‑user history tracking
    - Mobile‑optimized responsive UI
    - Real‑time upload progress tracking in frontend
