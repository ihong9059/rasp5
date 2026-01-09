# Glossary - 약어 및 용어 설명

이 프로젝트에서 사용되는 약어 및 기술 용어 정리

## A

### API (Application Programming Interface)
애플리케이션 프로그래밍 인터페이스. 소프트웨어 간 상호작용을 위한 규약 및 도구 모음.

## C

### CLI (Command Line Interface)
명령줄 인터페이스. 텍스트 기반으로 컴퓨터와 상호작용하는 방식.

### CSS (Cascading Style Sheets)
웹 페이지의 스타일(색상, 레이아웃, 폰트 등)을 정의하는 스타일시트 언어.

### CSI (Camera Serial Interface)
카메라 직렬 인터페이스. 라즈베리파이에서 카메라 모듈을 연결하는 데 사용되는 인터페이스.

### CV (Computer Vision)
컴퓨터 비전. 컴퓨터가 이미지나 영상을 이해하고 분석하는 기술 분야.

## H

### HTML (HyperText Markup Language)
웹 페이지의 구조를 정의하는 마크업 언어.

### HTTP (HyperText Transfer Protocol)
웹에서 데이터를 전송하기 위한 프로토콜.

## I

### IP (Internet Protocol)
인터넷 프로토콜. 네트워크에서 장치를 식별하는 주소 체계.

## J

### JPEG/JPG (Joint Photographic Experts Group)
손실 압축 방식의 이미지 파일 형식. 사진 저장에 널리 사용됨.

### JSON (JavaScript Object Notation)
데이터 교환을 위한 경량 텍스트 기반 형식.

## M

### MJPEG (Motion JPEG)
연속적인 JPEG 이미지를 스트리밍하는 비디오 압축 형식. IP Webcam에서 사용.

## O

### OCR (Optical Character Recognition)
**광학 문자 인식**

이미지나 스캔된 문서에서 텍스트를 인식하여 기계가 읽을 수 있는 문자로 변환하는 기술.

**작동 원리:**
1. 이미지 전처리 (노이즈 제거, 대비 향상)
2. 문자 영역 검출
3. 개별 문자 분리
4. 패턴 매칭 또는 딥러닝으로 문자 인식
5. 텍스트 출력

**이 프로젝트에서의 사용:**
- EasyOCR 라이브러리를 사용하여 번호판 이미지에서 문자를 인식
- 한국어와 영어를 동시에 지원
- 딥러닝 기반으로 높은 인식률 제공

**관련 라이브러리:**
- EasyOCR: 딥러닝 기반, 다국어 지원
- Tesseract: Google에서 개발한 오픈소스 OCR 엔진
- PaddleOCR: Baidu에서 개발한 OCR 도구

## R

### ROI (Region of Interest)
**관심 영역**

이미지나 영상에서 특정 처리나 분석을 수행할 대상 영역을 의미.

**사용 목적:**
- 처리 속도 향상: 전체 이미지 대신 필요한 영역만 처리
- 정확도 향상: 불필요한 배경 제거로 인식률 개선
- 메모리 절약: 필요한 부분만 메모리에 로드

**이 프로젝트에서의 사용:**
```python
# 번호판 영역(ROI)만 추출하여 OCR 수행
x, y, w, h = plate_region
roi = image[y:y+h, x:x+w]  # ROI 추출
result = ocr.recognize(roi)  # ROI에서만 문자 인식
```

**적용 예시:**
- 번호판 인식: 전체 차량 이미지에서 번호판 영역만 추출
- 얼굴 인식: 전체 사진에서 얼굴 영역만 추출
- 문서 스캔: 전체 페이지에서 특정 필드만 추출

## U

### URL (Uniform Resource Locator)
인터넷에서 리소스의 위치를 나타내는 주소.

## W

### WiFi (Wireless Fidelity)
무선 근거리 통신망(WLAN) 기술.

---

## 참고 자료

- [OpenCV Documentation](https://docs.opencv.org/)
- [EasyOCR GitHub](https://github.com/JaidedAI/EasyOCR)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
