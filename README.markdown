# Scam Detection Web Application

## Overview
This is a Flask-based web application designed to detect potential scam calls in real-time using speech recognition with the Vosk model and phone number lookup via a Telegram bot. The app monitors audio input for scam-related keywords in Hindi and alerts users if a threshold is exceeded. It also allows users to look up phone numbers for additional details.

## Project Structure
```
scam-detection-app/
├── app.py
├── vosk-model-small-hi-0.22/
│   └── [Vosk model files]
├── static/
│   └── style.css
├── templates/
│   └── index.html
└── README.md
```

## Prerequisites
- Python 3.8+
- Vosk model (`vosk-model-small-hi-0.22`) downloaded and placed in the project root
- Telegram API credentials (API_ID, API_HASH, PHONE_NUMBER)
- Node.js (for SocketIO client, if needed)
- Git for version control

## Setup Instructions
1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd scam-detection-app
   ```

2. **Install Dependencies**
   Install the required Python packages:
   ```bash
   pip install flask flask-socketio eventlet vosk pyaudio numpy telethon
   ```

3. **Download Vosk Model**
   - Download the `vosk-model-small-hi-0.22` from [Vosk Models](https://alphacephei.com/vosk/models).
   - Extract the model to the `vosk-model-small-hi-0.22` directory in the project root.

4. **Configure Telegram API**
   - Obtain your Telegram API credentials from [my.telegram.org](https://my.telegram.org).
   - Update `app.py` with your `API_ID`, `API_HASH`, and `PHONE_NUMBER`.

5. **Run the Application**
   ```bash
   python app.py
   ```
   The app will start on `http://localhost:5000`.

## Usage
- **Access the Web Interface**: Open `http://localhost:5000` in a browser.
- **Phone Number Lookup**: Enter a phone number and click "Lookup" to fetch details via the Telegram bot.
- **Call Monitoring**: Click "Accept Call" to start real-time audio monitoring. The app will detect scam keywords and alert if the threshold (2 keywords) is reached.
- **Reject Call**: Stops the audio monitoring.

## Features
- Real-time scam detection using Vosk speech recognition for Hindi keywords.
- Phone number lookup via Telegram bot integration.
- Responsive UI with SocketIO for real-time alerts.
- Customizable scam keyword list and detection threshold.

## Dependencies
- Flask: Web framework
- Flask-SocketIO: Real-time communication
- Eventlet: Asynchronous I/O
- Vosk: Speech recognition
- PyAudio: Audio input
- NumPy: Audio data processing
- Telethon: Telegram API client

## Notes
- Ensure a working microphone for audio input.
- The Vosk model path must be correctly set in `app.py`.
- Telegram bot (`@TrueCaller_Z_Bot`) must be accessible and responsive.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-branch`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.

## License
This project is licensed under the MIT License.