import requests
import img2pdf
import os
import io
from difflib import SequenceMatcher
import re
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader
from mimetypes import guess_type
from langchain_community.document_loaders import PyPDFLoader

def fetch_content_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content, response.headers.get('Content-Type')

def convert_image_bytes_to_pdf_bytes(image_bytes):
    return img2pdf.convert(image_bytes)

def extract_text_from_pdf_bytes(pdf_bytes):
    temp_pdf_path = "temp.pdf"
    with open(temp_pdf_path, "wb") as f:
        f.write(pdf_bytes)
    
    loader = PyPDFLoader(temp_pdf_path, extract_images=True)
    pages = loader.load()
    text = "\n".join([page.page_content for page in pages])
    
    # Clean up the temporary file
    os.remove(temp_pdf_path)
    
    return text

def show_content_from_url(url):
    content_bytes, mime_type = fetch_content_from_url(url)
    if mime_type.startswith('image'):
        show_image(content_bytes)
    elif mime_type == 'application/pdf':
        show_pdf(content_bytes)
    else:
        raise ValueError(f"Unsupported MIME type: {mime_type}")

def show_image(image_bytes):
    image = plt.imread(io.BytesIO(image_bytes), format='jpg')
    plt.imshow(image)
    plt.axis('off')
    plt.show()

def show_pdf(pdf_bytes):
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        plt.imshow(img)
        plt.axis('off')
        plt.show()

def free_ocr_from_url(url):
    content_bytes, mime_type = fetch_content_from_url(url)
    if mime_type != 'application/pdf':
        content_bytes = convert_image_bytes_to_pdf_bytes(content_bytes)
    return extract_text_from_pdf_bytes(content_bytes)

def word_similarity(word1, word2):
    ratio = SequenceMatcher(None, word1, word2).ratio()
    return ratio * 100

def calculate_unclear_score(text, keywords):
    words = re.split(r'[^a-zA-Z]', text)
    all_sc = []
    for k in keywords:
        sc, indikasi = max((word_similarity(k, t), t) for t in words if t)
        all_sc.append(sc)
    return sum(all_sc) / len(all_sc)

def evaluate_ocr_quality(url):
    keywords = [
        "NIK", "PROVINSI", "Nama", "Tempat", "Jenis kelamin", "Alamat",
        "RT/RW", "Desa", "Kecamatan", "Agama", "Kewarganegaraan",
        "Status", "Pekerjaan"
    ]

    extracted_text = free_ocr_from_url(url)
    return calculate_unclear_score(extracted_text, keywords)

       