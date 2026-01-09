# License Plate Recognition Project - Requirements

## Project Overview
Raspberry Pi 5에서 스마트폰 카메라(IP Webcam)를 사용하여 자동차 번호판을 인식하고 결과를 웹에서 표시하는 프로젝트

## Requirements

### Hardware
- Raspberry Pi 5
- Smartphone with IP Webcam app installed
- Same network connection (WiFi)

### Core Features
1. **IP Webcam Integration**
   - 스마트폰의 IP Webcam 앱을 통해 실시간 영상 스트리밍
   - 웹 브라우저에서 카메라 화면 실시간 표시

2. **Web Interface**
   - 실시간 카메라 스트림 표시
   - 캡처 버튼으로 현재 화면 캡처
   - 인식된 번호판 결과 표시

3. **License Plate Recognition**
   - 캡처된 이미지에서 번호판 영역 검출
   - OCR을 통한 번호판 문자 인식
   - 한국 자동차 번호판 형식 지원

### Technical Stack
- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **OCR**: EasyOCR (Korean + English support)
- **Image Processing**: OpenCV
- **Camera Source**: IP Webcam (Android app)

## User Story
1. 사용자가 스마트폰에서 IP Webcam 앱 실행
2. 라즈베리파이에서 웹 서버 실행
3. PC/태블릿 브라우저에서 웹 앱 접속
4. 실시간 카메라 화면 확인
5. 자동차 번호판이 보이면 "캡처" 버튼 클릭
6. 번호판 인식 결과 화면에 표시
