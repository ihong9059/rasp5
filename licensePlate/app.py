#!/usr/bin/env python3
"""
License Plate Recognition Web Application
Raspberry Pi 5 + IP Webcam + EasyOCR
"""

from flask import Flask, render_template, Response, request, jsonify, send_from_directory
import cv2
import requests
import numpy as np
from datetime import datetime
import os
import threading

from plate_recognizer import PlateRecognizer

app = Flask(__name__)

# Global variables
camera_url = None
current_frame = None
frame_lock = threading.Lock()
recognizer = None

# Captures directory
CAPTURES_DIR = os.path.join(os.path.dirname(__file__), 'captures')
os.makedirs(CAPTURES_DIR, exist_ok=True)


def init_recognizer():
    """Initialize OCR recognizer (lazy loading)"""
    global recognizer
    if recognizer is None:
        print("Initializing EasyOCR... (this may take a moment)")
        recognizer = PlateRecognizer()
        print("EasyOCR initialized successfully")
    return recognizer


def get_frame_from_ip_webcam():
    """Get frame from IP Webcam stream"""
    global camera_url, current_frame

    if not camera_url:
        return None

    try:
        # IP Webcam snapshot URL
        snapshot_url = f"http://{camera_url}:8080/shot.jpg"
        response = requests.get(snapshot_url, timeout=5)

        if response.status_code == 200:
            nparr = np.frombuffer(response.content, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            with frame_lock:
                current_frame = frame.copy()

            return frame
    except Exception as e:
        print(f"Error getting frame: {e}")

    return None


def generate_frames():
    """Generate frames for video streaming"""
    while True:
        frame = get_frame_from_ip_webcam()

        if frame is not None:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            # No frame available, wait a bit
            import time
            time.sleep(0.1)


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/set_camera', methods=['POST'])
def set_camera():
    """Set IP Webcam URL"""
    global camera_url

    data = request.get_json()
    ip = data.get('ip', '')

    if not ip:
        return jsonify({'success': False, 'error': 'IP address required'})

    # Test connection
    try:
        test_url = f"http://{ip}:8080/shot.jpg"
        response = requests.get(test_url, timeout=5)

        if response.status_code == 200:
            camera_url = ip
            return jsonify({'success': True, 'message': f'Connected to {ip}'})
        else:
            return jsonify({'success': False, 'error': 'Cannot connect to camera'})

    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Connection timeout'})
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Connection failed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/freeze', methods=['POST'])
def freeze():
    """Capture current frame immediately (fast)"""
    global current_frame

    with frame_lock:
        if current_frame is None:
            return jsonify({
                'success': False,
                'error': 'No frame available. Check camera connection.'
            })
        frame = current_frame.copy()

    # Save captured image
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'capture_{timestamp}.jpg'
    filepath = os.path.join(CAPTURES_DIR, filename)
    cv2.imwrite(filepath, frame)

    return jsonify({
        'success': True,
        'filename': filename,
        'timestamp': timestamp
    })


@app.route('/recognize/<filename>', methods=['POST'])
def recognize(filename):
    """Recognize license plate from saved image"""
    filepath = os.path.join(CAPTURES_DIR, filename)

    if not os.path.exists(filepath):
        return jsonify({
            'success': False,
            'error': 'Image file not found'
        })

    # Load image
    frame = cv2.imread(filepath)

    # Initialize recognizer if needed
    rec = init_recognizer()

    # Recognize license plate
    result = rec.recognize(frame)

    # Add capture info
    result['captured_file'] = filename

    return jsonify(result)


@app.route('/capture', methods=['POST'])
def capture():
    """Capture current frame and recognize license plate (legacy)"""
    global current_frame

    with frame_lock:
        if current_frame is None:
            return jsonify({
                'success': False,
                'error': 'No frame available. Check camera connection.'
            })
        frame = current_frame.copy()

    # Save captured image
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'capture_{timestamp}.jpg'
    filepath = os.path.join(CAPTURES_DIR, filename)
    cv2.imwrite(filepath, frame)

    # Initialize recognizer if needed
    rec = init_recognizer()

    # Recognize license plate
    result = rec.recognize(frame)

    # Add capture info
    result['captured_file'] = filename
    result['timestamp'] = timestamp

    return jsonify(result)


@app.route('/status')
def status():
    """Get current status"""
    global camera_url, current_frame

    with frame_lock:
        has_frame = current_frame is not None

    return jsonify({
        'camera_connected': camera_url is not None,
        'camera_url': camera_url,
        'has_frame': has_frame,
        'recognizer_ready': recognizer is not None
    })


@app.route('/captures/<filename>')
def serve_capture(filename):
    """Serve captured images"""
    return send_from_directory(CAPTURES_DIR, filename)


if __name__ == '__main__':
    print("=" * 50)
    print("License Plate Recognition Web App")
    print("=" * 50)
    print("\n1. Open IP Webcam app on your smartphone")
    print("2. Start the server in IP Webcam")
    print("3. Access this web app from browser")
    print("\nStarting server on http://0.0.0.0:5000")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
