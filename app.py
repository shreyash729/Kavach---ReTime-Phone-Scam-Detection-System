from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import eventlet
import os
import vosk
import json
import pyaudio
import numpy as np
import asyncio
from telethon import TelegramClient, events
import re
eventlet.monkey_patch()

# Initialize Flask and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
#socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")
socketio = SocketIO(
    app,
    async_mode='eventlet',
    cors_allowed_origins="*",
    use_reloader=False,
    ping_timeout=60000,  # 60 seconds
    ping_interval=25000  # 25 seconds
)
# Telegram API Configuration
API_ID = os.getenv("TELEGRAM_API_ID") # your telegram api ID
API_HASH = os.getenv("TELEGRAM_API_HASH")  # your telegram api hash
PHONE_NUMBER = os.getenv("PHONE_NUMBER")  # Your phone number Include country code (e.g., +91xxxxxx)
BOT_X_USERNAME = "@TrueCaller_Z_Bot"  

# Vosk Model Configuration
VOSK_MODEL_PATH = "./vosk-model-small-hi-0.22" 
assert os.path.exists(VOSK_MODEL_PATH), "Vosk model path is incorrect or missing!"

# Load Vosk Model
vosk_model = vosk.Model(VOSK_MODEL_PATH)
recognizer = vosk.KaldiRecognizer(vosk_model, 16000)  # Sample rate 16kHz

# Scam Keywords (Hindi)
SCAM_KEYWORDS = [
    "पैसे भेजो", "आपका अकाउंट ब्लॉक", "पुलिस गिरफ्तारी","यूपीआई पिन",  
    "आपके बेटे", "आपकी बेटी", "ओटीपी बताइए", "इमरजेंसी पैसा",
    "पैसे", "ओटीपी", "बैंक", "अकाउंट", "लॉटरी", "धोखाधड़ी", "ठगी", "पुलिस", "गिरफ्तारी","पेटीएम कस्टमर केयर", "केवाईसी","पेटीएम वॉलेट","वॉलेट","अपडेट नहीं होने के कारण", "एप्लीकेशन डाउनलोड करना ह","प्ले स्टोर को खोलिए","बेटे से बात करा दू","क्राइम ब्रांच से","एफआइआर मुकदमा दर्ज हुआ है","जुर्माना लगेगा","जेल होगी","मुकदमे की चार्ज सीट","लड़की का रेप किया है","आपका बेटा इस समय अरेस्ट हो चुका है","अरेस्ट हो चुका है","गूगल पे","सर आप गूगल पे फ़ोन पे क्या यूज़ करते हैं?","फ़ोन पे","बच्चे को क्लियर","आपका बैंक अकाउंट हैक हो गया है","आपका पैन कार्ड ब्लॉक हो गया है","आपको तुरंत पैसे ट्रांसफर करने होंगे","आपके नाम से लोन लिया गया है","टैक्स भरने में देरी हुई है, जुर्माना लगेगा","आपका क्रेडिट कार्ड अवैध रूप से इस्तेमाल हुआ है","आपके खिलाफ एफआइआर दर्ज हो चुकी है","आपको कोर्ट में पेश होना होगा","आपका नाम क्राइम रिकॉर्ड में आया है","आपके घर पर पुलिस आ रही है","आपको जमानत दिलवाने के लिए पैसे चाहिए","मैं आपके बैंक से बात कर रहा हूँ","हम सरकारी विभाग से बात कर रहे हैं","आपका नंबर लकी ड्रा में निकला है","आपको फ्री में मोबाइल मिलेगा","आपके रिश्तेदार ने मुझे पैसे भेजने को कहा","आपके फोन में वायरस है","आपको नया सिम कार्ड एक्टिवेट करना होगा","हमें आपका रिमोट एक्सेस दीजिए","अपना पासवर्ड शेयर करें","आपके बेटे को एक्सीडेंट हो गया है","आपके बेटी को एक्सीडेंट हो गया है","आपके परिवार वाले को हॉस्पिटल में भर्ती कराना है","आपके रिश्तेदार को जेल से छुड़ाना है","आपका आधार नंबर सस्पेंड हो गया है","आपके यूपीआई आईडी से गलत ट्रांजैक्शन हुआ है", "आपको केवाईसी अपडेट करना होगा", "आपका व्हाट्सएप नंबर डिलीट हो जाएगा","आपको कैशबैक मिलेगा","आपको रिफंड मिलेगा","एसबीआई से बात कर रहा हूं","अपहरण","किडनैपिंग","किडनैप","अश्लील  वीडियो","अश्लील फोटों","एक्सीडेंट होगया है","एक्सीडेंट हुआ है","रेप किया है","रेप केस में पकड़ा गया है","सट्टे में हार गया","रेड में पकड़ा गया","रेड","पुलिस चौकी","थाना प्रभारी","पुलिस थाना","मैसेज आया होगा","नंबर होगा","नोटिफिकेशन","अकाउंट एक्सपायर", "अकाउंट सस्पेंड","साइबर क्राइम","साइबर","लोन"
]
THRESHOLD = 2  # Number of scam words before confirming fraud

# Global state

scam_count = 0
user_alert_count = 0
audio_data = []
stream = None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lookup', methods=['POST'])

async def lookup():
    phone_number = request.json['number']
    try:
        telegram_response = await fetch_telegram_details(phone_number)
        #parsed_data = parse_telegram_response(telegram_response)
        return jsonify({
            'success': True,
            'data': telegram_response
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# SocketIO Events
@socketio.on('client_event')
def handle_client_event(data):
    global scam_count, user_alert_count
    print('Received from client:', data)
    if scam_count < THRESHOLD:
        emit('server_event', {'message': 'No Severe scam detected till now'})
    if scam_count > THRESHOLD:
        emit('server_event', {'message': 'this Call might be a scam'})
        scam_count = 0



@socketio.on('start_call')
def handle_start_call():
    global stream, scam_count
    print("Call started - monitoring for fraud...")
    scam_count = 0
    stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, 
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  frames_per_buffer=8000)
    socketio.start_background_task(target=scam_detection)

# Helper Functions

async def fetch_telegram_details(phone_number):
    """Fetch phone details from the Telegram bot."""
    async with TelegramClient("session_name", API_ID, API_HASH) as client:
        # Send phone number to bot
        await client.send_message(BOT_X_USERNAME, phone_number)
        await asyncio.sleep(5)

        # Fetch latest response
        async for msg in client.iter_messages(BOT_X_USERNAME, limit=1):
            return msg.text

import time
import json

def scam_detection():
    """Monitors the call for scam words in real-time."""
    global scam_count, audio_data
    try:
        while True:
            # Read audio data from the stream
            data = stream.read(2000, exception_on_overflow=False)
            audio_data.append(data)

            # Perform speech recognition
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")

                if text:
                    print(f"📝 Recognized: {text}")

                    # Check for scam keywords
                    for keyword in SCAM_KEYWORDS:
                        if keyword in text:
                            scam_count += 1
                            print(f"🚨 SCAM ALERT! ({scam_count}/{THRESHOLD}) - Detected: {text}\n")

                            # Emit an event to the client if the threshold is reached
                            if scam_count >= THRESHOLD:
                                print("⚠️ Emitting fraud_detected event...")
                                try:
                                    socketio.emit('fraud_detected')
                                except Exception as e:
                                    print(f"Error emitting event: {e}")
                                scam_count = 0  # Reset the counter
                            break

            # Yield control back to the event loop
            eventlet.sleep(0.1)  # Small delay to prevent blocking

    except Exception as e:
        print(f"Error in scam_detection: {e}")

# Run the app
if __name__ == '__main__':
    print("Starting Flask server...")
    socketio.run(app,debug=False, host='0.0.0.0', port=5000)