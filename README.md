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


##  Architecture Diagram

```mermaid
graph TD
  %% === Frontend ===
  subgraph Frontend
    A[Upload UI<br>(Browser)]
  end

  %% === AWS S3 Upload Flow ===
  subgraph AWS
    A -->|Pre-signed URL| B[S3 Bucket<br>uploads/]
    B --> C[Lambda: ocrProcessor]
    C -->|OCR Analysis| D[Textract<br>analyze_expense]
    C -->|Save Parsed JSON| E[S3 Bucket<br>parsed/]
    C -->|Save Summary| F[(DynamoDB<br>ReceiptlyReceipts)]

    %% === API Flow for Dashboard ===
    subgraph API
      G[API Gateway<br>/receipts] --> H[Lambda: getReceipts]
      H -->|Query GSIs| F
    end
  end
```


