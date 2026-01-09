// DOM Elements
const cameraIpInput = document.getElementById('camera-ip');
const connectBtn = document.getElementById('connect-btn');
const connectionStatus = document.getElementById('connection-status');
const videoStream = document.getElementById('video-stream');
const noVideo = document.getElementById('no-video');
const captureBtn = document.getElementById('capture-btn');
const resultPlaceholder = document.getElementById('result-placeholder');
const resultContent = document.getElementById('result-content');
const plateNumber = document.getElementById('plate-number');
const confidence = document.getElementById('confidence');
const allTexts = document.getElementById('all-texts');
const loadingOverlay = document.getElementById('loading-overlay');

// Connect to IP Webcam
async function connectCamera() {
    const ip = cameraIpInput.value.trim();

    if (!ip) {
        showStatus('IP 주소를 입력하세요', 'error');
        return;
    }

    connectBtn.disabled = true;
    connectBtn.textContent = 'Connecting...';

    try {
        const response = await fetch('/set_camera', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ip: ip })
        });

        const data = await response.json();

        if (data.success) {
            showStatus('Connected successfully!', 'success');

            // Start video stream
            videoStream.src = '/video_feed';
            videoStream.style.display = 'block';
            noVideo.style.display = 'none';

            // Enable capture button
            captureBtn.disabled = false;
        } else {
            showStatus(data.error || 'Connection failed', 'error');
        }
    } catch (error) {
        showStatus('Network error: ' + error.message, 'error');
    } finally {
        connectBtn.disabled = false;
        connectBtn.textContent = 'Connect';
    }
}

// Show connection status
function showStatus(message, type) {
    connectionStatus.textContent = message;
    connectionStatus.className = 'status ' + type;
}

// Capture and recognize license plate
async function captureAndRecognize() {
    captureBtn.disabled = true;
    loadingOverlay.style.display = 'flex';

    try {
        const response = await fetch('/capture', {
            method: 'POST'
        });

        const data = await response.json();

        // Hide placeholder, show result
        resultPlaceholder.style.display = 'none';
        resultContent.style.display = 'block';

        if (data.success && data.plate_number) {
            plateNumber.textContent = data.plate_number;
            plateNumber.className = 'plate-number';

            const conf = Math.round(data.confidence * 100);
            confidence.textContent = `Confidence: ${conf}%`;

            // Show all detected texts
            if (data.all_texts && data.all_texts.length > 0) {
                const texts = data.all_texts.map(t =>
                    `"${t.text}" (${Math.round(t.confidence * 100)}%)`
                ).join(', ');
                allTexts.textContent = `Detected texts: ${texts}`;
            } else {
                allTexts.textContent = '';
            }
        } else {
            plateNumber.textContent = data.error || 'No license plate detected';
            plateNumber.className = 'plate-number error';
            confidence.textContent = '';
            allTexts.textContent = '';
        }

    } catch (error) {
        resultPlaceholder.style.display = 'none';
        resultContent.style.display = 'block';
        plateNumber.textContent = 'Error: ' + error.message;
        plateNumber.className = 'plate-number error';
        confidence.textContent = '';
        allTexts.textContent = '';
    } finally {
        captureBtn.disabled = false;
        loadingOverlay.style.display = 'none';
    }
}

// Enter key to connect
cameraIpInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        connectCamera();
    }
});

// Check if camera was previously connected
async function checkStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();

        if (data.camera_connected && data.camera_url) {
            cameraIpInput.value = data.camera_url;

            if (data.has_frame) {
                videoStream.src = '/video_feed';
                videoStream.style.display = 'block';
                noVideo.style.display = 'none';
                captureBtn.disabled = false;
                showStatus('Camera already connected', 'success');
            }
        }
    } catch (error) {
        console.log('Status check failed:', error);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', checkStatus);
