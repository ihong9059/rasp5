import cv2
import numpy as np
import re
import easyocr

class PlateRecognizer:
    def __init__(self):
        # EasyOCR 리더 초기화 (한국어 + 영어)
        self.reader = easyocr.Reader(['ko', 'en'], gpu=False)

        # 한국 번호판 패턴
        self.patterns = [
            # 신형 번호판 (2019~): 123가4567
            r'\d{2,3}[가-힣]\d{4}',
            # 구형 번호판: 12가3456
            r'\d{2}[가-힣]\d{4}',
            # 지역 포함: 서울12가3456
            r'[가-힣]{2}\d{2}[가-힣]\d{4}',
            # 숫자만 (외국 번호판 등)
            r'\d{2,4}[-\s]?\d{2,4}',
        ]

    def preprocess_image(self, image):
        """이미지 전처리"""
        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 노이즈 제거
        denoised = cv2.bilateralFilter(gray, 11, 17, 17)

        # 대비 향상
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        return enhanced

    def find_plate_region(self, image):
        """번호판 영역 검출"""
        gray = self.preprocess_image(image)

        # 엣지 검출
        edges = cv2.Canny(gray, 30, 200)

        # 컨투어 찾기
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        plate_region = None
        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.018 * peri, True)

            # 4개의 꼭지점을 가진 사각형 찾기
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)

                # 번호판 비율 체크 (보통 2:1 ~ 5:1)
                if 1.5 < aspect_ratio < 6:
                    plate_region = (x, y, w, h)
                    break

        return plate_region

    def extract_plate_text(self, image):
        """번호판 텍스트 추출"""
        # 전체 이미지에서 OCR 수행
        results = self.reader.readtext(image)

        extracted_texts = []
        for (bbox, text, confidence) in results:
            # 공백 제거
            clean_text = text.replace(' ', '').replace('-', '')
            extracted_texts.append({
                'text': clean_text,
                'confidence': confidence,
                'bbox': bbox
            })

        return extracted_texts

    def validate_plate(self, text):
        """번호판 패턴 검증"""
        for pattern in self.patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return None

    def recognize(self, image):
        """번호판 인식 메인 함수"""
        results = {
            'success': False,
            'plate_number': None,
            'confidence': 0,
            'all_texts': [],
            'plate_region': None
        }

        try:
            # 이미지가 numpy 배열인지 확인
            if isinstance(image, bytes):
                nparr = np.frombuffer(image, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is None:
                results['error'] = 'Invalid image'
                return results

            # 번호판 영역 검출 시도
            plate_region = self.find_plate_region(image)

            # 번호판 영역이 있으면 해당 영역만 OCR
            if plate_region:
                x, y, w, h = plate_region
                # 여유 공간 추가
                margin = 10
                x = max(0, x - margin)
                y = max(0, y - margin)
                w = min(image.shape[1] - x, w + 2 * margin)
                h = min(image.shape[0] - y, h + 2 * margin)

                roi = image[y:y+h, x:x+w]
                results['plate_region'] = plate_region
            else:
                # 전체 이미지 사용
                roi = image

            # OCR 수행
            texts = self.extract_plate_text(roi)
            results['all_texts'] = texts

            # 번호판 패턴 매칭
            for item in texts:
                plate_number = self.validate_plate(item['text'])
                if plate_number:
                    results['success'] = True
                    results['plate_number'] = plate_number
                    results['confidence'] = item['confidence']
                    break

            # 패턴 매칭 실패시 가장 높은 신뢰도의 텍스트 반환
            if not results['success'] and texts:
                best = max(texts, key=lambda x: x['confidence'])
                results['plate_number'] = best['text']
                results['confidence'] = best['confidence']
                results['success'] = len(best['text']) >= 4

        except Exception as e:
            results['error'] = str(e)

        return results


# 테스트용
if __name__ == '__main__':
    recognizer = PlateRecognizer()
    print("PlateRecognizer initialized successfully")
