IntelliVision AR Studio
Real-Time Augmented Reality Video Enhancement & Smart Background Virtualization

IntelliVision AR Studio is an advanced real-time AR vision processing application built using OpenCV, Mediapipe FaceMesh, and CVZone, enabling smooth virtual background replacement and facial landmark-based accessory overlays similar to Snapchat filter technology.

The system supports multiple accessories at the same time, including:

Eyes accessories (glasses, goggles, anime eyes, etc.)

Face masks (transparent PNG full-face masks)

Head accessories (caps, birthday crown, cowboy hat)

Animated tear effects

Multi-mode background engines (image, blur, color, real)

Accessories and backgrounds are auto-loaded from folder structure, making it fully modular and expandable.

🚀 Key Features

Real-time AR video processing (60 FPS capable)

Facial landmark–based placement & scaling (adapts to distance from camera)

Smooth virtual background segmentation with temporal stabilization

Unlimited accessory support (add PNGs to folders, auto detected)

Multiple accessories active simultaneously

Animated tears effect with continuous motion

Multi-mode background switching:

Original Camera

Image Background

Solid Color Background

Blur Background

🎮 Controls
Key	Action
1	Original background
2	Image background mode
A / D	Switch image background
3	Color background mode
J / L	Switch color
4	Blur background
E	Toggle Eyes accessories
F	Toggle Face masks
H	Toggle Head accessories
T	Toggle Tears
[ / ]	Switch accessory in selected category
0	Remove all accessories
Q	Quit

📂 Project Folder Structure
background_removal/
│ main.py
│
├── img/                       # Put background images here
│    bg1.jpg
│    bg2.png
│    bg3.jpg
│
└── filters/                   # Accessory categories
     ├── eyes/
     │    glasses1.png
     │    glasses2.png
     │
     ├── face/
     │    mask1.png
     │    mask2.png
     │
     ├── head/
     │    crown.png
     │    hat.png
     │
     └── tears/
          tear1.png
          tear2.png


Add as many PNGs as you want — the system loads everything automatically.

🧠 Tech Stack
Component	Technology
Background Segmentation	CVZone SelfieSegmentation + Mediapipe
Face tracking / landmarks	MediaPipe FaceMesh
Live video processing	OpenCV
PNG overlay & smoothing	CVZone
Real-time AR rendering	Python3, NumPy
📦 Installation
Requirements
Python 3.8+
OpenCV
cvzone
mediapipe
numpy

Install dependencies
pip install opencv-python cvzone mediapipe numpy

Run the app
python main.py