🔹 Title & Description

    Receipt OCR + Auto Expense Tracker
    Upload a grocery receipt and get back a parsed JSON summary with merchant, items, total, tax, and date—using AWS Textract and Lambda.

🔹 Demo

    Link to live frontend (S3)
    "Optional GIF or screenshot"

🔹 Architecture Overview
   
    1. Upload receipt image to S3 via frontend
    2. Triggers Lambda (`ocrProcessor`)
    3. Textract extracts text
    4. Custom parser formats it into structured JSON
    5. Parsed JSON saved to `parsed/` folder in same S3 bucket
    
🔹 Technologies Used

    AWS S3
    AWS Lambda
    AWS Textract
    GitHub Actions (CI/CD)
    HTML/CSS frontend
    IAM, CloudWatch, etc.

🔹 Example Output
  
    {
      "merchant": "LiDL",
      "total": "19.96",
      "currency": "EUR",
      "date": "17.08.10",
      "line_items": [...]
    }
    
🔹 Future Enhancements

    Add a DynamoDB-backed history page
    User authentication
    Mobile-optimized UI
    Real-time upload progress

