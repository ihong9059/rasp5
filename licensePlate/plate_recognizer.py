import cv2
import numpy as np
import re
import easyocr

class PlateRecognizer:
    def __init__(self):
        # EasyOCR 리더 초기화 (한국어 + 영어)
        self.reader = easyocr.Reader(['ko', 'en'], gpu=False)

        # 한국 번호판 패턴 (한글 포함 필수)
        self.patterns = [
            # 신형 번호판 (2019~): 123가4567
            r'\d{2,3}[가-힣]\d{4}',
            # 구형 번호판: 12가3456
            r'\d{2}[가-힣]\d{4}',
            # 지역 포함: 서울12가3456
            r'[가-힣]{2}\d{2}[가-힣]\d{4}',
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
            # bbox를 Python 기본 타입으로 변환
            bbox_converted = [[int(p[0]), int(p[1])] for p in bbox]
            extracted_texts.append({
                'text': clean_text,
                'confidence': float(confidence),
                'bbox': bbox_converted
            })

        # 인접한 텍스트 병합 시도
        merged_texts = self.merge_nearby_texts(extracted_texts)
        extracted_texts.extend(merged_texts)

        return extracted_texts

    def merge_nearby_texts(self, texts):
        """인접한 텍스트들을 병합하여 번호판 후보 생성"""
        if len(texts) < 2:
            return []

        merged = []

        # bbox 중심점 기준으로 정렬 (y 먼저, 그 다음 x)
        sorted_texts = sorted(texts, key=lambda t: (
            (t['bbox'][0][1] + t['bbox'][2][1]) / 2,  # y 중심
            (t['bbox'][0][0] + t['bbox'][2][0]) / 2   # x 중심
        ))

        # 같은 라인에 있고 x좌표가 인접한 텍스트들만 그룹화
        for i in range(len(sorted_texts)):
            for j in range(i + 1, min(i + 4, len(sorted_texts))):  # 최대 3개 연속만 확인
                t1 = sorted_texts[i]
                t2 = sorted_texts[j]

                # y 좌표 차이 확인 (같은 라인인지)
                y1 = (t1['bbox'][0][1] + t1['bbox'][2][1]) / 2
                y2 = (t2['bbox'][0][1] + t2['bbox'][2][1]) / 2
                height = max(abs(t1['bbox'][2][1] - t1['bbox'][0][1]),
                           abs(t2['bbox'][2][1] - t2['bbox'][0][1]), 30)

                if abs(y1 - y2) > height * 0.8:
                    continue

                # x 좌표 거리 확인 (인접한지)
                x1_right = max(t1['bbox'][1][0], t1['bbox'][2][0])
                x2_left = min(t2['bbox'][0][0], t2['bbox'][3][0])
                width = max(abs(t1['bbox'][1][0] - t1['bbox'][0][0]),
                          abs(t2['bbox'][1][0] - t2['bbox'][0][0]), 30)

                # 두 텍스트 사이의 거리가 너무 멀면 스킵
                if x2_left - x1_right > width * 2:
                    continue

                # 두 텍스트 병합
                if t1['bbox'][0][0] < t2['bbox'][0][0]:
                    combined = t1['text'] + t2['text']
                else:
                    combined = t2['text'] + t1['text']

                avg_conf = (t1['confidence'] + t2['confidence']) / 2

                if len(combined) >= 5:  # 번호판은 최소 5자
                    merged.append({
                        'text': combined,
                        'confidence': avg_conf,
                        'bbox': t1['bbox'],
                        'merged': True
                    })

                # 세 번째 텍스트도 확인
                for k in range(j + 1, min(j + 3, len(sorted_texts))):
                    t3 = sorted_texts[k]
                    y3 = (t3['bbox'][0][1] + t3['bbox'][2][1]) / 2

                    if abs(y2 - y3) > height * 0.8:
                        continue

                    x3_left = min(t3['bbox'][0][0], t3['bbox'][3][0])
                    if x3_left - x2_left > width * 3:
                        continue

                    # 세 텍스트를 x 좌표 순으로 정렬 후 병합
                    three = sorted([t1, t2, t3], key=lambda t: t['bbox'][0][0])
                    combined3 = ''.join([t['text'] for t in three])
                    avg_conf3 = sum([t['confidence'] for t in three]) / 3

                    if len(combined3) >= 7:  # 번호판은 보통 7자 이상
                        merged.append({
                            'text': combined3,
                            'confidence': avg_conf3,
                            'bbox': three[0]['bbox'],
                            'merged': True
                        })

        return merged

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

            # 전체 이미지에서 먼저 OCR 수행
            texts = self.extract_plate_text(image)
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
