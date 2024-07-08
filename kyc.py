import cv2
import numpy as np
import insightface
from ultralytics import YOLO
from models import FaceComparisonResult, KycResult
from utils import load_image, calculate_rotation_angle, rotate_image, image_to_base64

model = YOLO('models/card_detector.pt')
threshold = 50

def detect_id_card(input_file):
    image = load_image(input_file)
    results = model(image)
    id_card_detected = False
    coordinates = []

    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()
        if boxes.shape[0] > 0:
            id_card_detected = True
            coordinates = boxes.tolist()
            break

    return id_card_detected, coordinates

def compare_faces(id_card_source, person_source, show_image=False):
    model = insightface.app.FaceAnalysis()
    model.prepare(ctx_id=-1)  # Use CPU

    id_card_image, id_card_pil_image = load_image(id_card_source)
    person_image, person_pil_image = load_image(person_source)
    
    id_card_faces = model.get(id_card_image)
    person_faces = model.get(person_image)

    if len(id_card_faces) > 0 and id_card_faces[0].landmark_2d_68 is not None:
        angle = calculate_rotation_angle(id_card_faces[0].landmark_2d_68)
        id_card_pil_image = rotate_image(id_card_pil_image, angle)
        id_card_image = np.array(id_card_pil_image)
        id_card_faces = model.get(id_card_image)

    if len(person_faces) > 0 and person_faces[0].landmark_2d_68 is not None:
        angle = calculate_rotation_angle(person_faces[0].landmark_2d_68)
        person_pil_image = rotate_image(person_pil_image, angle)
        person_image = np.array(person_pil_image)
        person_faces = model.get(person_image)

    results = []

    for i, id_card_face in enumerate(id_card_faces):
        for j, person_face in enumerate(person_faces):
            embedding1 = id_card_face.embedding
            embedding2 = person_face.embedding

            similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
            similarity_percentage = similarity * 100

            if show_image:
                bbox1 = id_card_face.bbox.astype(int)
                bbox2 = person_face.bbox.astype(int)
                left1, top1, right1, bottom1 = bbox1
                left2, top2, right2, bottom2 = bbox2
                cropped_face_1 = id_card_pil_image.crop((left1, top1, right1, bottom1))
                cropped_face_2 = person_pil_image.crop((left2, top2, right2, bottom2))
                id_card_face_bytes = image_to_base64(cropped_face_1)
                person_face_bytes = image_to_base64(cropped_face_2)
            else:
                id_card_face_bytes = ''
                person_face_bytes = ''

            result = FaceComparisonResult(
                comparison_between=f"ID card face {i + 1} and person face {j + 1}",
                id_card_face=id_card_face_bytes,
                person_face=person_face_bytes,
                similar=similarity * 100 > threshold,
                score=similarity_percentage
            )
            results.append(result)

    avg_score = sum([r.score for r in results]) / len(results) if results else 0
    face_selfie = len(person_faces)

    id_card_detected, coordinates = detect_id_card(person_source)
    if id_card_detected:
        if avg_score > threshold and avg_score < 90:
            summary = 'Accepted: User is holding the ID card, and the face matches.'
        elif avg_score < threshold:
            summary = 'Rejected: User Face not matched with ID card'
        else:
            summary = 'Rejected: Suspicious activity detected, the face similarity exceeds 90%'
    else:
        if avg_score > threshold and avg_score < 90:
            summary = 'Rejected: User not holding ID Card.'
        elif avg_score < threshold:
            summary = 'Rejected: User Face not matched with ID card and User not holding ID Card'
        else:
            summary = 'Rejected: Suspicious activity detected, the face similarity exceeds 90% and User not holding ID Card'

    final_result = KycResult(
        details=results,
        avg_score=avg_score,
        face_detected_in_id_card=len(id_card_faces),
        face_detected_in_person_pict=face_selfie,
        status='Reject' if 'Rejected' in summary else 'Accept',
        summary=summary,
        id_card_detected=id_card_detected,
        id_card_coordinates=coordinates
    )

    return final_result
