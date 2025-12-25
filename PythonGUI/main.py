import cv2
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation
from cvzone.FaceMeshModule import FaceMeshDetector
import os
import time
import numpy as np
import math

# ------------ Settings ------------
BACKGROUND_FOLDER = "img"
FILTER_FOLDER = "filters"
EYES_FOLDER = os.path.join(FILTER_FOLDER, "eyes")
FACE_FOLDER = os.path.join(FILTER_FOLDER, "face")
HEAD_FOLDER = os.path.join(FILTER_FOLDER, "head")
TEARS_FOLDER = os.path.join(FILTER_FOLDER, "tears")

CAM_WIDTH, CAM_HEIGHT = 640, 480

# ------------ Camera ------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, 60)

# ------------ CV Modules ------------
segmentor = SelfiSegmentation()
faceDetector = FaceMeshDetector(maxFaces=1)

# ------------ Load backgrounds ------------
imgList = []
if os.path.exists(BACKGROUND_FOLDER):
    for imgPath in os.listdir(BACKGROUND_FOLDER):
        full_path = os.path.join(BACKGROUND_FOLDER, imgPath)
        img = cv2.imread(full_path)
        if img is not None:
            imgList.append(cv2.resize(img, (CAM_WIDTH, CAM_HEIGHT)))

# Solid colors
colorList = [
    (0, 255, 0),
    (255, 0, 0),
    (0, 0, 0),
    (255, 255, 255)
]

# ------------ Load accessories ------------
def load_png_folder(folder):
    items = []
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.lower().endswith(".png"):
                png = cv2.imread(os.path.join(folder, f), cv2.IMREAD_UNCHANGED)
                if png is not None:
                    items.append(png)
    return items

eyesAccessories = load_png_folder(EYES_FOLDER)
faceAccessories = load_png_folder(FACE_FOLDER)
headAccessories = load_png_folder(HEAD_FOLDER)
tearAccessories = load_png_folder(TEARS_FOLDER)

# ------------ State variables ------------
indexImg = 0
indexColor = 0

mode = "image" if len(imgList) > 0 else "original"   # background mode

# accessory on/off
eyesOn = False
faceOn = False
headOn = False
tearsOn = False

# which item inside each group
eyesIndex = 0
faceIndex = 0
headIndex = 0
tearsIndex = 0

# which group is currently selected for [ / ] switching
currentCategory = None  # "eyes", "face", "head", "tears"

pTime = 0
prevMask = None
tearOffset = 0


# ------------ Helpers ------------

def dist(p1, p2):
    return math.dist((p1[0], p1[1]), (p2[0], p2[1]))


def overlay_soft_bg(img, bg, prev_mask=None, smooth=31, alpha_mask=0.7):
    """Smooth, temporally-stable background replacement."""
    imgNoBg = segmentor.removeBG(img, (0, 0, 0))
    gray = cv2.cvtColor(imgNoBg, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    if smooth % 2 == 0:
        smooth += 1
    mask = cv2.GaussianBlur(mask, (smooth, smooth), 0)
    mask = mask.astype(np.float32) / 255.0

    if prev_mask is not None and prev_mask.shape == mask.shape:
        mask = alpha_mask * mask + (1 - alpha_mask) * prev_mask

    mask3 = cv2.merge([mask, mask, mask])

    fg = img.astype(np.float32) * mask3
    bg = bg.astype(np.float32) * (1 - mask3)

    out = cv2.add(fg, bg)
    return out.astype(np.uint8), mask


def place_eyes_accessory(img, face, png):
    """Place glasses/goggles etc. around eyes."""
    if png is None:
        return img
    try:
        left, right = face[33], face[263]
        topL, topR = face[159], face[386]

        eye_width = dist(left, right)
        if eye_width <= 0:
            return img

        target_w = int(eye_width * 1.9)
        target_h = int(target_w * png.shape[0] / png.shape[1])
        png_resized = cv2.resize(png, (target_w, target_h), interpolation=cv2.INTER_AREA)

        cx = int((left[0] + right[0]) / 2)
        cy = int((topL[1] + topR[1]) / 2) + int(target_h * 0.05)

        x = cx - target_w // 2
        y = cy - target_h // 2

        return cvzone.overlayPNG(img, png_resized, [x, y])
    except:
        return img


def place_face_accessory(img, face, png):
    """
    Place a full-face mask (transparent eyes etc.) over the face.
    Covers from forehead to chin and from left to right side of face.
    """
    if png is None:
        return img
    try:
        forehead = face[10]
        chin = face[152]
        leftCheek = face[234]
        rightCheek = face[454]

        face_width = dist(leftCheek, rightCheek)
        face_height = chin[1] - forehead[1]
        if face_width <= 0 or face_height <= 0:
            return img

        aspect = png.shape[1] / png.shape[0]  # w/h

        # Start from vertical requirement: a bit taller than forehead→chin
        target_h = int(face_height * 1.2)
        target_w = int(target_h * aspect)

        # Ensure it is wide enough to cover from ear to ear
        min_w = int(face_width * 1.9)
        if target_w < min_w:
            target_w = min_w
            target_h = int(target_w / aspect)

        png_resized = cv2.resize(png, (target_w, target_h), interpolation=cv2.INTER_AREA)

        cx = int((leftCheek[0] + rightCheek[0]) / 2)
        # slight upward bias so it covers a bit above forehead and below chin
        top_y = int(forehead[1] - target_h * 0.25)

        x = cx - target_w // 2
        y = top_y

        return cvzone.overlayPNG(img, png_resized, [x, y])
    except:
        return img


def place_head_accessory(img, face, png):
    """
    Place a crown/hat above head.
    Bottom edge sits right at hairline (forehead landmark).
    Scaled with face width so it adjusts with distance.
    """
    if png is None:
        return img                  
    try:
        forehead = face[10]
        leftCheek = face[234]
        rightCheek = face[454]

        head_width = dist(leftCheek, rightCheek)
        if head_width <= 0:
            return img

        # Bigger factor for more coverage across head
        target_w = int(head_width * 2.3)
        aspect = png.shape[1] / png.shape[0]  # w/h
        target_h = int(target_w / aspect)

        png_resized = cv2.resize(png, (target_w, target_h), interpolation=cv2.INTER_AREA)

        cx = int((leftCheek[0] + rightCheek[0]) / 2)

        # bottom edge at (approx) hairline = forehead[1]
        bottom_y = int(forehead[1] + target_h * 0.30)  # tiny overlap
        top_y = bottom_y - target_h

        x = cx - target_w // 2
        y = top_y

        return cvzone.overlayPNG(img, png_resized, [x, y])
    except:
        return img


def place_tears_accessory(img, face, png, offset):
    """Place animated tears under eyes."""
    if png is None:
        return img
    try:
        leftT = face[145]
        rightT = face[374]

        tear_width = dist(leftT, rightT) * 0.25
        if tear_width <= 0:
            return img

        target_w = int(tear_width)
        target_h = int(target_w * png.shape[0] / png.shape[1])
        png_resized = cv2.resize(png, (target_w, target_h), interpolation=cv2.INTER_AREA)

        for p in [leftT, rightT]:
            x = int(p[0] - target_w / 2)
            y = int(p[1] + offset)
            img = cvzone.overlayPNG(img, png_resized, [x, y])

        return img
    except:
        return img


# ------------ Main loop ------------

while True:
    success, frame = cap.read()
    if not success:
        break

    # base image (no accessories yet)
    baseImg = cv2.flip(frame, 1)

    # Face landmarks on base image
    _, faces = faceDetector.findFaceMesh(baseImg, draw=False)

    # ---- Background composite (no accessories involved) ----
    h, w, _ = baseImg.shape
    if mode == "image" and len(imgList) > 0:
        bg = imgList[indexImg]
        imgOut, prevMask = overlay_soft_bg(baseImg, bg, prevMask)
        modeText = f"BG: Image {indexImg+1}/{len(imgList)}"
    elif mode == "color":
        bg = np.full((h, w, 3), colorList[indexColor], dtype=np.uint8)
        imgOut, prevMask = overlay_soft_bg(baseImg, bg, prevMask)
        modeText = f"BG: Color {indexColor+1}/{len(colorList)}"
    elif mode == "blur":
        blurBg = cv2.GaussianBlur(baseImg, (51, 51), 0)
        imgOut, prevMask = overlay_soft_bg(baseImg, blurBg, prevMask)
        modeText = "BG: Blur"
    else:
        imgOut = baseImg.copy()
        prevMask = None
        modeText = "BG: Original"

    # ---- Now overlay accessories AFTER background ----
    visOrig = baseImg.copy()
    visOut = imgOut.copy()

    if faces:
        face = faces[0]

        # Face mask first
        if faceOn and len(faceAccessories) > 0:
            visOrig = place_face_accessory(visOrig, face, faceAccessories[faceIndex])
            visOut = place_face_accessory(visOut, face, faceAccessories[faceIndex])

        # Eyes
        if eyesOn and len(eyesAccessories) > 0:
            visOrig = place_eyes_accessory(visOrig, face, eyesAccessories[eyesIndex])
            visOut = place_eyes_accessory(visOut, face, eyesAccessories[eyesIndex])

        # Tears (animated)
        if tearsOn and len(tearAccessories) > 0:
            visOrig = place_tears_accessory(visOrig, face, tearAccessories[tearsIndex], tearOffset)
            visOut = place_tears_accessory(visOut, face, tearAccessories[tearsIndex], tearOffset)

        # Head hat/crown last so it appears on top
        if headOn and len(headAccessories) > 0:
            visOrig = place_head_accessory(visOrig, face, headAccessories[headIndex])
            visOut = place_head_accessory(visOut, face, headAccessories[headIndex])

    # Animate tears (only when on)
    if tearsOn and len(tearAccessories) > 0:
        tearOffset = (tearOffset + 2) % 25
    else:
        tearOffset = 0

    # Stack for display
    imgStacked = cvzone.stackImages([visOrig, visOut], 2, 1)

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if pTime != 0 else 0
    pTime = cTime
    cv2.putText(imgStacked, f"FPS: {int(fps)}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    # Info text
    cv2.putText(imgStacked, modeText, (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    accInfo = f"Eyes:{'ON' if eyesOn else 'OFF'}  Face:{'ON' if faceOn else 'OFF'}  Head:{'ON' if headOn else 'OFF'}  Tears:{'ON' if tearsOn else 'OFF'}"
    cv2.putText(imgStacked, accInfo, (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    helpText = "BG:1-Orig 2-Img(A/D) 3-Color(J/L) 4-Blur | Acc:0-Off E-eyes F-face H-head T-tears [ / ] switch  Q-Quit"
    cv2.putText(imgStacked, helpText,
                (10, imgStacked.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 230), 2)

    cv2.imshow("IntelliVision AR Studio", imgStacked)

    # ------------ Keys ------------
    key = cv2.waitKey(1) & 0xFF

    # Background modes
    if key == ord('1'):
        mode = "original"
    elif key == ord('2'):
        mode = "image"
    elif key == ord('3'):
        mode = "color"
    elif key == ord('4'):
        mode = "blur"

    # Background navigation
    elif key == ord('a') and mode == "image" and len(imgList) > 0:
        indexImg = (indexImg - 1) % len(imgList)
    elif key == ord('d') and mode == "image" and len(imgList) > 0:
        indexImg = (indexImg + 1) % len(imgList)
    elif key == ord('j') and mode == "color":
        indexColor = (indexColor - 1) % len(colorList)
    elif key == ord('l') and mode == "color":
        indexColor = (indexColor + 1) % len(colorList)

    # Accessories toggle
    elif key == ord('0'):
        eyesOn = faceOn = headOn = tearsOn = False
        currentCategory = None

    elif key == ord('e'):
        eyesOn = not eyesOn
        if len(eyesAccessories) > 0:
            currentCategory = "eyes"

    elif key == ord('f'):
        faceOn = not faceOn
        if len(faceAccessories) > 0:
            currentCategory = "face"

    elif key == ord('h'):
        headOn = not headOn
        if len(headAccessories) > 0:
            currentCategory = "head"

    elif key == ord('t'):
        tearsOn = not tearsOn
        if len(tearAccessories) > 0:
            currentCategory = "tears"

    # Switch accessory inside current category
    elif key == ord('['):
        if currentCategory == "eyes" and len(eyesAccessories) > 0:
            eyesIndex = (eyesIndex - 1) % len(eyesAccessories)
        elif currentCategory == "face" and len(faceAccessories) > 0:
            faceIndex = (faceIndex - 1) % len(faceAccessories)
        elif currentCategory == "head" and len(headAccessories) > 0:
            headIndex = (headIndex - 1) % len(headAccessories)
        elif currentCategory == "tears" and len(tearAccessories) > 0:
            tearsIndex = (tearsIndex - 1) % len(tearAccessories)

    elif key == ord(']'):
        if currentCategory == "eyes" and len(eyesAccessories) > 0:
            eyesIndex = (eyesIndex + 1) % len(eyesAccessories)
        elif currentCategory == "face" and len(faceAccessories) > 0:
            faceIndex = (faceIndex + 1) % len(faceAccessories)
        elif currentCategory == "head" and len(headAccessories) > 0:
            headIndex = (headIndex + 1) % len(headAccessories)
        elif currentCategory == "tears" and len(tearAccessories) > 0:
            tearsIndex = (tearsIndex + 1) % len(tearAccessories)

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
