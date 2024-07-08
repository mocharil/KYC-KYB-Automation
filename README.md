```markdown
# KYC and KYB Processing API

This repository contains a FastAPI-based application for performing KYC (Know Your Customer) and KYB (Know Your Business) processes using provided URLs for ID cards, selfies, and various business documents. The API leverages OCR to evaluate the quality of ID card images and performs face comparison to verify identity. For KYB processing, it analyzes documents to determine their types and validate their contents.

## Features

- **KYC Processing**:
  - Evaluates the quality of ID card images using OCR.
  - Compares faces in ID card images with selfie images to verify identity.
  - Provides detailed results including face detection, comparison scores, and status.

- **KYB Processing**:
  - Analyzes business documents (NPWP, NIB, Company Deed, Decree) to determine document types and validate contents.
  - Uses Google's Vertex AI for document analysis.
  - Provides detailed results including document types, confidence scores, and similarity scores for names and addresses.

## Endpoints

### POST /kyc/

#### Request

Form data parameters:

- `url_ktp`: URL of the ID card image.
- `url_selfie`: URL of the selfie image.
- `url_npwp`: URL of the NPWP document.
- `url_nib`: URL of the NIB document.
- `url_akta`: URL of the Company Deed document.
- `url_sk`: URL of the Kementerian Hukum dan HAM decree document.

#### Response

The response is a JSON object containing the results of the KYC and KYB processes.

```json
{
  "kyc": {
    "details": [...],
    "avg_score": 85.0,
    "face_detected_in_id_card": 1,
    "face_detected_in_person_pict": 1,
    "status": "Accept",
    "summary": "Accepted: User is holding the ID card, and the face matches.",
    "id_card_detected": true,
    "id_card_coordinates": [...]
  },
  "kyb": {
    "result": {
      "image_1": {...},
      "image_2": {...},
      "image_3": {...},
      "image_4": {...},
      "match_score_name": 90.0,
      "match_score_address": 85.0,
      "explanation": "All documents are valid"
    },
    "usage": {
      "prompt_token_count": 100,
      "candidates_token_count": 200,
      "total_token_count": 300
    }
  }
}
```

## Installation

1. Clone the repository:
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```
2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Run the FastAPI application:
    ```sh
    uvicorn app:app --reload
    ```

## Structure

- `app.py`: Main FastAPI application.
- `kyc.py`: Functions related to KYC processing.
- `kyb_pipeline.py`: Functions related to KYB processing.
- `image_quality.py`: Functions related to evaluating the quality of ID card images.
- `models.py`: Pydantic models for request and response data validation.
- `requirements.txt`: List of dependencies.

## Usage

1. Start the FastAPI server.
2. Send a POST request to `/kyc/` with the necessary form data.
3. Receive the KYC and KYB processing results in the response.

## Flowchart

For a detailed flowchart of the process, visit the following link:
[Flowchart](https://drive.google.com/file/d/1xRekj-RxI770zezcPmMBZzK0vOjYHHDR/view?usp=sharing)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```
