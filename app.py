from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from kyc import compare_faces
from kyb_pipeline import kyb_processing
from image_quality import evaluate_ocr_quality


from models import CompleteResponse, KYCResponse, KYBResponse, KYBResult, ImageData, KYBUsage

app = FastAPI()

@app.post("/kyc/", response_model=CompleteResponse)
def kyc_and_kyb_process(
    url_ktp: str = Form(None), 
    url_selfie: str = Form(None),
    url_npwp: str = Form(None),
    url_nib: str = Form(None),
    url_akta: str = Form(None),
    url_sk: str = Form(None)
):
    result = CompleteResponse()

    # KYC process
    try:
        if url_ktp and url_selfie:
            #check ktp
            quality_score = evaluate_ocr_quality(url_ktp)
            if quality_score<60:
                result.kyc = KYCResponse(
                    details=[],
                    avg_score=0,
                    face_detected_in_id_card=0,
                    face_detected_in_person_pict=0,
                    status ='failed', 
                    summary = f"ID Card is blurry, with a clarity score of {quality_score:.2f}%".replace('.00',''),
                    id_card_detected=False,
                    id_card_coordinates=[]
                )                

            else:
                result.kyc = compare_faces(url_ktp, url_selfie, False)
        elif url_ktp or url_selfie:
            summary = 'You must provide URL KTP' if not url_ktp else 'You must provide URL Selfie'
            result.kyc = KYCResponse(
                details=[],
                avg_score=0,
                face_detected_in_id_card=0,
                face_detected_in_person_pict=0,
                status='failed', 
                summary=summary,
                id_card_detected=False,
                id_card_coordinates=[]
            )
        else:
            result.kyc = KYCResponse(
                details=[],
                avg_score=0,
                face_detected_in_id_card=0,
                face_detected_in_person_pict=0,
                status='failed', 
                summary='There are no URL Selfie and KTP',
                id_card_detected=False,
                id_card_coordinates=[]
            )

        # KYB Process
        if url_npwp and url_nib and url_akta and url_sk:
            kyb = kyb_processing(url_npwp, url_nib, url_akta, url_sk)
            result.kyb = KYBResponse(**kyb)
        elif url_npwp or url_nib or url_akta or url_sk:
            required_urls = {
                'URL NPWP': url_npwp,
                'URL NIB': url_nib,
                'URL Akta': url_akta,
                'URL SK': url_sk
            }

            missing_urls = [name for name, url in required_urls.items() if not url]
            msg = 'You must provide: ' + ', '.join(missing_urls)

            result.kyb = KYBResponse(
                result=KYBResult(
                    image_1=ImageData(document_type='', confidence_score=0, explanation='', name='', address=''),
                    image_2=ImageData(document_type='', confidence_score=0, explanation='', name='', address=''),
                    image_3=ImageData(document_type='', confidence_score=0, explanation='', name='', address=''),
                    image_4=ImageData(document_type='', confidence_score=0, explanation='', name='', address=''),
                    match_score_name=0,
                    match_score_address=0,
                    explanation=msg
                ),
                usage=KYBUsage(prompt_token_count=0, candidates_token_count=0, total_token_count=0)
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result
