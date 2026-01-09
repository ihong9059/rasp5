# License Plate Recognition Web App

Raspberry Pi 5에서 스마트폰 카메라(IP Webcam)를 사용하여 자동차 번호판을 인식하는 웹 애플리케이션

## Features

- 스마트폰 카메라 실시간 스트리밍 (IP Webcam)
- 웹 브라우저에서 실시간 영상 확인
- 원클릭 캡처 및 번호판 인식
- 한국 자동차 번호판 지원

## Requirements

### Hardware
- Raspberry Pi 5
- Android 스마트폰 (IP Webcam 앱 설치)
- 동일 네트워크 연결 (WiFi)

### Software
- Python 3.9+
- IP Webcam (Android 앱)

## Installation

### 1. 시스템 패키지 설치

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv libgl1-mesa-glx
```

### 2. 프로젝트 설정

```bash
cd /home/uttec/rasp5/licensePlate

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. 스마트폰 IP Webcam 설정

1. Android 스마트폰에서 **IP Webcam** 앱 설치 (Play Store)
2. 앱 실행 후 하단의 **Start server** 클릭
3. 화면에 표시된 IP 주소 확인 (예: `http://192.168.0.10:8080`)

## Usage

### 1. 서버 실행

```bash
cd /home/uttec/rasp5/licensePlate
source venv/bin/activate
python app.py
```

서버가 `http://0.0.0.0:5000`에서 실행됩니다.

### 2. 웹 앱 접속

1. PC 또는 태블릿 브라우저에서 `http://<라즈베리파이IP>:5000` 접속
2. IP Webcam URL 입력란에 스마트폰 IP 입력 (예: `192.168.0.10`)
3. **Connect** 버튼 클릭
4. 실시간 카메라 화면 확인

### 3. 번호판 인식

1. 자동차 번호판이 화면에 보이도록 스마트폰 위치 조정
2. **Capture** 버튼 클릭
3. 인식된 번호판 결과 확인

## Project Structure

```
licensePlate/
├── app.py              # Flask 메인 애플리케이션
├── plate_recognizer.py # 번호판 인식 모듈
├── requirements.txt    # Python 패키지
├── static/
│   ├── css/style.css   # 스타일시트
│   └── js/main.js      # JavaScript
├── templates/
│   └── index.html      # 웹 페이지
└── captures/           # 캡처 이미지 저장
```

## Troubleshooting

### 카메라 스트림이 보이지 않음
- 스마트폰과 라즈베리파이가 같은 네트워크에 있는지 확인
- IP Webcam 앱이 실행 중인지 확인
- 방화벽 설정 확인

### OCR 인식률이 낮음
- 번호판이 화면 중앙에 크게 보이도록 조정
- 조명이 충분한지 확인
- 카메라 초점이 맞는지 확인

### 서버 실행 오류
```bash
# 가상환경 활성화 확인
source venv/bin/activate

# 패키지 재설치
pip install -r requirements.txt --force-reinstall
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | 메인 페이지 |
| `/video_feed` | GET | 비디오 스트림 |
| `/capture` | POST | 캡처 및 인식 |
| `/set_camera` | POST | 카메라 URL 설정 |

## License

MIT License
