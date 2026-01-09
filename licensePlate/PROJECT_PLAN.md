# License Plate Recognition - Project Plan

## 1. Project Structure

```
licensePlate/
├── prompt.md           # 프로젝트 요구사항
├── PROJECT_PLAN.md     # 프로젝트 계획서 (본 문서)
├── README.md           # 사용 설명서
├── requirements.txt    # Python 패키지 목록
├── app.py              # Flask 메인 애플리케이션
├── plate_recognizer.py # 번호판 인식 모듈
├── static/
│   ├── css/
│   │   └── style.css   # 스타일시트
│   └── js/
│       └── main.js     # 프론트엔드 JavaScript
├── templates/
│   └── index.html      # 메인 웹 페이지
└── captures/           # 캡처된 이미지 저장 폴더
```

## 2. Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Smartphone    │     │  Raspberry Pi 5 │     │  Web Browser    │
│   (IP Webcam)   │────▶│  (Flask Server) │◀────│  (Client)       │
│                 │     │                 │     │                 │
│  MJPEG Stream   │     │  - Stream Proxy │     │  - View Stream  │
│  Port: 8080     │     │  - OCR Process  │     │  - Capture Btn  │
│                 │     │  - Web Server   │     │  - View Result  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 3. Implementation Details

### 3.1 Backend (Flask)

**app.py**
- `/` : 메인 페이지 렌더링
- `/video_feed` : IP Webcam 스트림 프록시
- `/capture` : 현재 프레임 캡처 및 번호판 인식
- `/api/config` : IP Webcam URL 설정

**plate_recognizer.py**
- OpenCV로 이미지 전처리 (그레이스케일, 노이즈 제거)
- EasyOCR로 텍스트 인식
- 한국 번호판 패턴 매칭 (정규식)

### 3.2 Frontend

**index.html**
- 실시간 비디오 스트림 표시
- IP Webcam URL 설정 입력
- 캡처 버튼
- 인식 결과 표시 영역

### 3.3 IP Webcam Integration

- Android IP Webcam 앱의 MJPEG 스트림 URL 사용
- URL 형식: `http://<phone-ip>:8080/video`
- Flask에서 프록시하여 CORS 문제 해결

## 4. Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0+ | Web framework |
| OpenCV-Python | 4.8+ | Image processing |
| EasyOCR | 1.7+ | OCR (Korean support) |
| Requests | 2.31+ | HTTP client |
| NumPy | 1.24+ | Array operations |

## 5. Korean License Plate Patterns

| Type | Pattern | Example |
|------|---------|---------|
| 신형 (2019~) | 123가4567 | 3자리 + 한글 + 4자리 |
| 구형 | 12가3456 | 2자리 + 한글 + 4자리 |
| 영업용 | 서울12가3456 | 지역 + 2자리 + 한글 + 4자리 |

## 6. Development Steps

1. ✅ 프로젝트 폴더 생성
2. ✅ 요구사항 문서화
3. ⬜ Flask 백엔드 구현
4. ⬜ 프론트엔드 구현
5. ⬜ 번호판 인식 모듈 구현
6. ⬜ 통합 테스트
7. ⬜ 문서화

## 7. Testing Plan

1. IP Webcam 연결 테스트
2. 스트림 프록시 동작 확인
3. 캡처 기능 테스트
4. OCR 인식률 테스트 (다양한 번호판)
5. 전체 워크플로우 테스트
