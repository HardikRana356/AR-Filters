import cv2
import os
import math
import numpy as np
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation
from cvzone.FaceMeshModule import FaceMeshDetector

# ---------------- INIT ----------------
segmentor = SelfiSegmentation()
detector = FaceMeshDetector(maxFaces=1)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILTER_DIR = os.path.join(ROOT, "filters")
BG_DIR = os.path.join(ROOT, "backgrounds")

# ---------------- LOAD ASSETS ----------------
def load_pngs(folder):
    arr = []
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.lower().endswith(".png"):
                p = cv2.imread(os.path.join(folder, f), cv2.IMREAD_UNCHANGED)
                if p is not None and p.shape[2] == 4:
                    arr.append(p)
    return arr

def load_bgs(folder):
    arr = []
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.lower().endswith((".jpg", ".png")):
                img = cv2.imread(os.path.join(folder, f))
                if img is not None:
                    arr.append(img)
    return arr

eyes_pngs  = load_pngs(os.path.join(FILTER_DIR, "eyes"))
face_pngs  = load_pngs(os.path.join(FILTER_DIR, "face"))
head_pngs  = load_pngs(os.path.join(FILTER_DIR, "head"))
tears_pngs = load_pngs(os.path.join(FILTER_DIR, "tears"))
bg_imgs    = load_bgs(BG_DIR)

# ---------------- STATE ----------------
STATE = {
    "camera_on": True,
    "bg_mode": "original",
    "bg_i": 0,

    "eyes": False,
    "face": False,
    "head": False,
    "tears": False,

    "ei": 0, "fi": 0, "hi": 0, "ti": 0,
    "tear_y": 0
}

# ---------------- FPS OPTIMIZATION STATE ----------------
frame_count = 0
cached_face = None
png_cache = {}     # cache resized PNGs

# ---------------- HELPERS ----------------
def dist(a, b):
    return math.dist((a[0], a[1]), (b[0], b[1]))

def safe_overlay(img, png, x, y):
    h, w = img.shape[:2]
    ph, pw = png.shape[:2]

    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(w, x + pw)
    y2 = min(h, y + ph)

    if x1 >= x2 or y1 >= y2:
        return img

    px1 = x1 - x
    py1 = y1 - y
    px2 = px1 + (x2 - x1)
    py2 = py1 + (y2 - y1)

    return cvzone.overlayPNG(
        img,
        png[py1:py2, px1:px2],
        [x1, y1]
    )

def get_cached_png(png, w, h):
    key = (id(png), w, h)
    if key not in png_cache:
        png_cache[key] = cv2.resize(png, (w, h), interpolation=cv2.INTER_AREA)
    return png_cache[key]

# ---------------- MAIN PROCESS ----------------
def process_frame(img):
    global frame_count, cached_face

    if not STATE["camera_on"] or img is None:
        return None

    frame_count += 1
    img = cv2.flip(img, 1)
    h, w = img.shape[:2]

    # ---------- BACKGROUND (DOWNSCALED) ----------
    if STATE["bg_mode"] in ("blur", "image"):
        small = cv2.resize(img, (w // 2, h // 2))
        if STATE["bg_mode"] == "blur":
            bg_small = cv2.GaussianBlur(small, (21, 21), 0)
        else:
            bg = bg_imgs[STATE["bg_i"] % len(bg_imgs)]
            bg_small = cv2.resize(bg, (w // 2, h // 2))

        fg_small = segmentor.removeBG(small, bg_small, threshold=0.85)
        img = cv2.resize(fg_small, (w, h))

    # ---------- FACE MESH (EVERY 2 FRAMES) ----------
    if frame_count % 2 == 0 or cached_face is None:
        try:
            _, faces = detector.findFaceMesh(img, False)
            cached_face = faces[0] if faces else None
        except:
            cached_face = None

    if cached_face is None:
        return img

    f = cached_face

    # ---------- FACE ----------
    if STATE["face"] and face_pngs:
        p = face_pngs[STATE["fi"] % len(face_pngs)]
        fw = int(dist(f[234], f[454]) * 1.8)
        if fw > 10:
            fh = int(fw * p.shape[0] / p.shape[1])
            png = get_cached_png(p, fw, fh)
            cx = int((f[234][0] + f[454][0]) / 2)
            cy = int(f[10][1] - fh * 0.25)
            img = safe_overlay(img, png, cx - fw // 2, cy)

    # ---------- EYES ----------
    if STATE["eyes"] and eyes_pngs:
        p = eyes_pngs[STATE["ei"] % len(eyes_pngs)]
        ew = int(dist(f[33], f[263]) * 1.9)
        if ew > 10:
            eh = int(ew * p.shape[0] / p.shape[1])
            png = get_cached_png(p, ew, eh)
            cx = int((f[33][0] + f[263][0]) / 2)
            cy = int((f[159][1] + f[386][1]) / 2)
            img = safe_overlay(img, png, cx - ew // 2, cy - eh // 2)

    # ---------- TEARS ----------
    if STATE["tears"] and tears_pngs:
        p = tears_pngs[STATE["ti"] % len(tears_pngs)]
        tw = int(dist(f[145], f[374]) * 0.25)
        if tw > 5:
            th = int(tw * p.shape[0] / p.shape[1])
            png = get_cached_png(p, tw, th)
            for pt in [f[145], f[374]]:
                img = safe_overlay(
                    img, png,
                    int(pt[0] - tw // 2),
                    int(pt[1] + STATE["tear_y"])
                )
            STATE["tear_y"] = (STATE["tear_y"] + 2) % 25

    # ---------- HEAD ----------
    if STATE["head"] and head_pngs:
        p = head_pngs[STATE["hi"] % len(head_pngs)]
        hw = int(dist(f[234], f[454]) * 2.3)
        if hw > 20:
            hh = int(hw * p.shape[0] / p.shape[1])
            png = get_cached_png(p, hw, hh)
            cx = int((f[234][0] + f[454][0]) / 2)
            cy = int(f[10][1] + hh * 0.30 - hh)
            img = safe_overlay(img, png, cx - hw // 2, cy)

    return img

# ---------------- COMMAND HANDLER ----------------
def handle_command(cmd):
    if cmd["action"] == "toggle":
        STATE[cmd["key"]] = not STATE[cmd["key"]]
    elif cmd["action"] == "next":
        STATE[cmd["key"]] += 1
    elif cmd["action"] == "camera":
        STATE["camera_on"] = cmd["value"]
    elif cmd["action"] == "bg":
        STATE["bg_mode"] = cmd["mode"]
    elif cmd["action"] == "next_bg":
        STATE["bg_i"] += 1
