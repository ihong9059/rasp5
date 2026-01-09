# 작업 보고서 - 2026-01-09

## 문제 상황
- Mac에서 VNC를 사용하여 Raspberry Pi 5에 접속 시 Ctrl+Space로 한글/영문 전환이 작동하지 않음
- 다이얼로그가 잠깐 보이다가 사라지고 전환되지 않는 현상

## 원인 분석

### 1. 환경 확인
- **VNC 서버**: wayvnc (Wayland 기반)
- **입력기**: ibus + ibus-engine-hangul
- **im-config**: ibus로 설정됨

### 2. 발견된 문제점
1. **환경 변수 미설정**: GTK_IM_MODULE, QT_IM_MODULE, XMODIFIERS가 세션에 로드되지 않음
2. **Mac 단축키 충돌**: Mac에서 Ctrl+Space가 Spotlight 또는 입력 소스 전환에 사용됨

## 적용한 수정 사항

### 1. 환경 변수 설정

**~/.profile에 추가:**
```bash
# IBus Input Method
export GTK_IM_MODULE=ibus
export QT_IM_MODULE=ibus
export XMODIFIERS=@im=ibus
```

**~/.config/environment.d/ibus.conf 생성 (Wayland용):**
```
GTK_IM_MODULE=ibus
QT_IM_MODULE=ibus
XMODIFIERS=@im=ibus
```

### 2. 한영 전환 단축키 변경

**ibus 트리거 키 변경:**
```bash
gsettings set org.freedesktop.ibus.general.hotkey triggers "['<Shift>space', '<Control>space', '<Super>space']"
```

**ibus-hangul switch-keys 변경:**
```bash
gsettings set org.freedesktop.ibus.engine.hangul switch-keys 'Hangul,Shift+space,Caps_Lock'
```

### 3. 현재 한영 전환 키 설정
| 키 | 상태 |
|---|---|
| Hangul | 사용 가능 |
| Shift+Space | 사용 가능 |
| Caps Lock | 사용 가능 |
| Ctrl+Space | Mac에서 가로챔 (문제) |

## 후속 조치

### 필수
- **재부팅 필요**: `sudo reboot` 후 VNC 재접속하여 테스트

### 선택 (Mac 측 설정)
Mac에서 Ctrl+Space를 사용하고 싶다면:
1. 시스템 설정 → 키보드 → 키보드 단축키
2. Spotlight → "Spotlight 검색 보기" 비활성화 또는 다른 키로 변경
3. 입력 소스 → "이전 입력 소스 선택" 비활성화 또는 다른 키로 변경

## 확인 명령어 (다음 세션용)

```bash
# 환경 변수 확인
echo "GTK_IM_MODULE=$GTK_IM_MODULE"
echo "QT_IM_MODULE=$QT_IM_MODULE"
echo "XMODIFIERS=$XMODIFIERS"

# ibus 상태 확인
pgrep -a ibus

# 현재 트리거 키 확인
gsettings get org.freedesktop.ibus.general.hotkey triggers

# hangul switch-keys 확인
gsettings get org.freedesktop.ibus.engine.hangul switch-keys
```

## 추가 수정 사항 (2차)

재부팅 후에도 한글 전환은 되지만 실제 입력이 안 되는 문제 발생.

### 원인
ibus-hangul 엔진 설정이 Wayland 환경에 최적화되지 않음

### 해결 방법
```bash
# 초기 입력 모드를 한글로 변경
gsettings set org.freedesktop.ibus.engine.hangul initial-input-mode 'hangul'

# 이벤트 포워딩 활성화
gsettings set org.freedesktop.ibus.engine.hangul use-event-forwarding true

# Preedit 모드를 syllable로 변경
gsettings set org.freedesktop.ibus.engine.hangul preedit-mode 'syllable'

# ibus 재시작
ibus restart
```

## 최종 설정 값

| 설정 | 값 |
|------|-----|
| initial-input-mode | hangul |
| use-event-forwarding | true |
| preedit-mode | syllable |
| switch-keys | Hangul,Shift+space |

## 상태
- [x] 재부팅 후 테스트 완료
- [x] 한글 입력 정상 작동 확인

---

## 번호판 인식 시스템 개선 (오후)

### 문제 상황
1. 번호판 인식 실패 - "No license plate detected"
2. 캡처 시 이미지가 즉시 고정되지 않음
3. JSON 직렬화 오류 (numpy int32)

### 원인 분석
1. EasyOCR이 번호판을 분리된 텍스트로 인식: "201", "누", "2734"
2. 잘못된 영역 검출로 인해 번호판이 아닌 영역에서 OCR 수행
3. 숫자만 있는 패턴(2026)이 번호판으로 오인식

### 적용한 수정 사항

#### 1. 텍스트 병합 로직 추가
**파일**: `plate_recognizer.py`
- `merge_nearby_texts()` 함수 추가
- 같은 라인의 인접한 텍스트 자동 병합
- 결과: "201" + "누" + "2734" → "201누2734"

#### 2. 번호판 패턴 수정
- 숫자만 있는 패턴 제거 (한글 포함 필수)
- "2026" 같은 날짜 오인식 방지

#### 3. 전체 이미지 OCR
- 잘못된 영역 검출 문제 해결
- 전체 이미지에서 OCR 수행 후 패턴 매칭

#### 4. JSON 직렬화 오류 수정
```python
# numpy int32/float64 → Python int/float 변환
bbox_converted = [[int(p[0]), int(p[1])] for p in bbox]
'confidence': float(confidence)
```

#### 5. UI 개선 - 캡처 즉시 고정
**파일**: `app.py`, `static/js/main.js`
- `/freeze` 엔드포인트 추가 (프레임만 저장)
- `/recognize/<filename>` 엔드포인트 추가 (OCR 수행)
- 버튼 클릭 → 즉시 이미지 고정 → OCR 처리 → 결과 표시

### 테스트 결과
- 번호판 "201누2734" 정상 인식
- Confidence: 66%
- 캡처 즉시 이미지 고정 작동

### 생성된 문서
- `IMPROVEMENT_REPORT.md` - 개선 사항 상세 리포트
- `JETSON_ORIN_NANO_REPORT.md` - GPU 대안 비교 리포트

### 향후 개선 가능 사항
1. 이미지 전처리 강화 (신뢰도 향상)
2. 번호판 영역 검출 개선 (딥러닝 모델)
3. GPU 가속 (Jetson Orin Nano 또는 GPU PC)

## 최종 상태
- [x] 한글 입력 정상 작동
- [x] 번호판 인식 정상 작동
- [x] UI 개선 완료
- [x] 문서화 완료
