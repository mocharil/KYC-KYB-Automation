from pdf2image import convert_from_bytes
import io, re
from google.oauth2 import service_account
import vertexai
from mimetypes import guess_type
from PyPDF2 import PdfReader
import requests
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmCategory,
    HarmBlockThreshold,
    Image
)
from dotenv import load_dotenv
import os
load_dotenv()

# Vertex AI configuration
project_id = os.getenv('PROJECT_ID')
credentials_file_path = os.getenv('CREDENTIALS_FILE_PATH')
credentials = service_account.Credentials.from_service_account_file(credentials_file_path)
vertexai.init(project=project_id, credentials=credentials)
model = os.getenv("GEMINI_MODEL")
multimodal_model = GenerativeModel(model)

safety_config = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
}

# Generation Config
config = GenerationConfig(temperature=0.0, top_p=1, top_k=32)

def split_pdf_per_5_pages_to_images(pdf_bytes):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(reader.pages)
    num_files = (total_pages + 4) // 5
    
    all_images_bytes = []
    
    for i in range(num_files):
        start_page = i * 5
        end_page = min(start_page + 5, total_pages)
        
        images = convert_from_bytes(pdf_bytes, first_page=start_page + 1, last_page=end_page)
        
        for image in images:
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            all_images_bytes.append(img_bytes)
        
        print(f"Part {i + 1} processed with pages from {start_page + 1} to {end_page}.")
        break
    return all_images_bytes
      
def get_bytes(URL):
    content_file = requests.get(URL).content
    mime_type, _ = guess_type(URL)
    if mime_type == 'application/pdf':
        return split_pdf_per_5_pages_to_images(content_file)
    return [content_file]

def pipeline(LINK):
    content = []
    for c in get_bytes(LINK)[:3]:
        content.append(Image.from_bytes(c))

    return content

def kyb_processing(NPWP_LINK, NIB_LINK, AKTA_LINK, SK_LINK):
    contents = []
    for idx, LINK in enumerate([NPWP_LINK, NIB_LINK, AKTA_LINK, SK_LINK], start=1):
        prompt = f"the File Above are image_{idx}"
        contents.extend(pipeline(LINK))
        contents.append(prompt)

    prompt = """Please analyze all the files above.
    Determine the document type for each file based on the criteria provided.
    Criteria for determining document types:
    1. NPWP: The document must contain the words "Direktorat Jenderal Pajak".
    2. NIB: The document must contain the words "NOMOR INDUK BERUSAHA".
    3. Company Deed: The document must contain the words "AKTA" and "NOTARIS".
    4. Decree of Kementerian Hukum dan HAM: The document must contain the words "Kementerian Hukum dan HAM (Kemenkumham)".
    Return the result in JSON format as follows:
    {
        "image_1": {
            "document_type": "<document_type>",
            "confidence_score": <value between 0 and 1>,
            "explanation": "<reason>",
            "npwp_number": "<number of NPWP if document type is NPWP>",
            "name": "<name>",
            "address": "<address>"
        },
        "image_2": {
            "document_type": "<document_type>",
            "confidence_score": <value between 0 and 1>,
            "explanation": "<reason>",
            "nib_number": "<number of NIB if document type is NIB>",
            "name": "<name>",
            "address": "<address>"
        },
        "image_3": {
            "document_type": "<document_type>",
            "confidence_score": <value between 0 and 1>,
            "explanation": "<reason>",
            "company_deed_number": "<number of company deed if document type is Company Deed>",
            "name": "<company_name>",
            "address": "<company address or position of the company or notaris address>"
        },
        "image_4": {
            "document_type": "<document_type>",
            "confidence_score": <value between 0 and 1>,
            "explanation": "<reason>",
            "decree_number": "<number of decree if document type is Decree of Kementerian Hukum dan HAM>",
            "name": "<company_name>",
            "address": "<company address or position of the company or notaris address>"
        },
        "match_score_name": "<similarity score for names across all documents from 0-100>",
        "match_score_address": "<similarity score for addresses across all documents from 0-100>",
        "explanation": "<analysis>"
    }
    """
    contents.append(prompt)
    responses = multimodal_model.generate_content(contents,
                                                  safety_settings=safety_config, 
                                                  generation_config=config, 
                                                  stream=True)
    full_result = ''
    for response in responses:
        full_result += response.text
    usage = {}   
    for i in str(response.usage_metadata).split('\n'):
        if i.strip():
            x = i.split(':')
            usage.update({x[0].strip():int(x[1].strip())})

    null = ''
    true = True
    false = False
    result_json = eval(re.findall(r'\{.*\}', full_result, flags=re.I | re.S)[0])
    
    return {'result': result_json, 'usage': usage}
