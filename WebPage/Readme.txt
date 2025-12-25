AI-Based Real-Time Background Removal and AR Filters (Web Application)

PROJECT OVERVIEW
This project is a real-time AI-powered web application that performs background removal,
background replacement, and face-based augmented reality (AR) filters using live camera input.
The backend processes video frames using computer vision and machine learning techniques,
while the frontend displays the processed output in real time using WebSockets.

This project is developed for academic / college purposes.

------------------------------------------------------------

SYSTEM ARCHITECTURE

Browser (Camera)
   |
Frontend (React.js)
   |  WebSocket
Backend (Python + OpenCV + MediaPipe)
   |
Processed Frames
   |
Browser Display

------------------------------------------------------------

PROJECT STRUCTURE

WebPage/
├── backend/
│   ├── main.py
│   ├── ar_engine.py
│   ├── requirements.txt
│   └── venv/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── filters/
│   ├── eyes/
│   ├── face/
│   ├── head/
│   └── tears/
│
└── backgrounds/ (optional)

------------------------------------------------------------

SYSTEM REQUIREMENTS

- Python 3.9 or Python 3.10
- Node.js v18 or higher
- npm
- Git
- Webcam
- Chrome or Edge browser

------------------------------------------------------------

HOW TO RUN THE PROJECT

==============================
BACKEND SETUP (PYTHON)
==============================

Step 1: Open Terminal / PowerShell
Command:
cd WebPage/backend

Step 2: Create Virtual Environment (First Time Only)
Command:
python -m venv venv

Step 3: Activate Virtual Environment

Windows Command:
.\venv\Scripts\activate

Mac / Linux Command:
source venv/bin/activate

Step 4: Install Backend Dependencies
Command:
pip install -r requirements.txt

Step 5: Start Backend Server
Command:
uvicorn main:app --reload

Expected Output:
Uvicorn running on http://127.0.0.1:8000

Do not close this terminal.

==============================
FRONTEND SETUP (REACT)
==============================

Step 6: Open a WebPage Terminal
Command:
cd WebPage/frontend

Step 7: Install Frontend Dependencies (First Time Only)
Command:
npm install

Step 8: Start Frontend Application
Command:
npm start

Browser URL:
http://localhost:3000

------------------------------------------------------------

CAMERA PERMISSION

When the browser asks for camera access, click ALLOW.
Camera permission is required for the application to work.

------------------------------------------------------------

APPLICATION FEATURES

- Live camera feed
- AI-based background removal
- Background blur and image replacement
- AR filters (eyes, face, head, tears)
- Camera on/off control
- Real-time processing

------------------------------------------------------------

OPTIONAL: RUN USING NGROK (FOR DEMO)

Step 1: Start Backend on Public Interface
Command:
uvicorn main:app --host 0.0.0.0 --port 8000

Step 2: Start Ngrok Tunnel
Command:
ngrok http 8000

Ngrok Output Example:
https://abcd-12-34.ngrok-free.app

Step 3: Update WebSocket URL in Frontend

Old:
ws://localhost:8000/ws

WebPage:
wss://abcd-12-34.ngrok-free.app/ws

------------------------------------------------------------

COMMON ISSUES AND FIXES

Camera Not Working:
- Allow camera permission
- Use Chrome or Edge
- Ensure webcam is not used by another app

MediaPipe Installation Error:
- Use Python 3.9 or 3.10
- Recreate virtual environment

WebSocket Not Connecting:
- Ensure backend is running
- Check port 8000
- Use wss:// with Ngrok

------------------------------------------------------------

STOPPING THE APPLICATION

To stop backend or frontend:
Command:
CTRL + C

------------------------------------------------------------

ACADEMIC NOTE

The backend runs locally due to computer vision and AI dependency constraints.
The frontend communicates with the backend using WebSockets for real-time processing.

------------------------------------------------------------

PROJECT CATEGORY

Academic / College Project
Real-Time Computer Vision Application
AI and Web Technology Integration

------------------------------------------------------------

CONCLUSION

This project demonstrates real-time background removal and augmented reality
effects using AI-driven computer vision techniques integrated with a web-based interface.
