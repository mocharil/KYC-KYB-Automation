from pydantic import BaseModel
from typing import List, Optional

class FaceComparisonResult(BaseModel):
    comparison_between: str
    id_card_face: str
    person_face: str
    similar: bool
    score: float

class KycResult(BaseModel):
    details: List[FaceComparisonResult]
    avg_score: float
    face_detected_in_id_card: int
    face_detected_in_person_pict: int
    status: str
    summary: str
    id_card_detected: bool
    id_card_coordinates: List

class ImageData(BaseModel):
    document_type: str
    confidence_score: float
    explanation: str
    npwp_number: Optional[str] = None
    nib_number: Optional[str] = None
    company_deed_number: Optional[str] = None
    decree_number: Optional[str] = None
    name: str
    address: str

class KYBResult(BaseModel):
    image_1: ImageData
    image_2: ImageData
    image_3: ImageData
    image_4: ImageData
    match_score_name: float
    match_score_address: float
    explanation: str

class KYBUsage(BaseModel):
    prompt_token_count: int
    candidates_token_count: int
    total_token_count: int

class KYBResponse(BaseModel):
    result: KYBResult
    usage: KYBUsage

class KYCDetail(BaseModel):
    comparison_between: str
    id_card_face: str
    person_face: str
    score: float
    similar: bool

class KYCResponse(BaseModel):
    avg_score: float
    details: List[KYCDetail]
    face_detected_in_id_card: int
    face_detected_in_person_pict: int
    id_card_coordinates: List[List[float]]
    id_card_detected: bool
    status: str
    summary: str

class CompleteResponse(BaseModel):
    kyb: Optional[KYBResponse] = None
    kyc: Optional[KYCResponse] = None

class ErrorResponse(BaseModel):
    detail: str
