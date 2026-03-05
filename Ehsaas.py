#!/usr/bin/env python3
"""
Ehsaas.py (The Ultimate Complete Version)
Features: Voice Commands, Zero-Lag Pointer, Dwell Click, Pinch Right-Click, 
Two-Finger Scroll (Top/Bottom), Two-Finger Swipe (Forward/Back), Palm Lock.
"""
import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import argparse
import time
import math
import json
import queue
import threading
import subprocess
from datetime import datetime

import cv2
import numpy as np
import pyautogui
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import mediapipe as mp

# ---------------- CLI & TUNABLES ----------------
parser = argparse.ArgumentParser()
parser.add_argument("--headless", action="store_true")
parser.add_argument("--fps", type=int, default=30)
parser.add_argument("--model", type=str, default="vosk-model-small-en-us-0.15")  # Change Vosk MOdel path here if needed
args = parser.parse_args()

HEADLESS = args.headless
MODEL_PATH = os.path.abspath(args.model)
FPS_LIMIT = args.fps

# ---------------- SETTINGS ----------------
WAKE_WORD = "gp"

SMOOTHING = 0.55           # High = faster, Low = smoother
DWELL_CLICK_TIME = 1.0     
RIGHT_CLICK_HOLD = 1.5     

SCROLL_HOLD_TIME = 0.8
SCROLL_THRESHOLD = 0.04    
SWIPE_THRESHOLD_PX = 100   # Pixels needed to trigger forward/back swipe

PALM_LOCK_TIME = 2.0

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

LOGFILE = "Ehsaas.log"

# ---------------- APPS & ALIASES ----------------
ALLOWED_APPS = {
    "chrome": "chrome",
    "vscode": "code",
    "explorer": "explorer",
    "notepad": "notepad",
    "calculator": "calc",
    "whatsapp": " whatsapp:",   # writing start before app name opens cmd prompt and then app, this is a neat trick to avoid the black cmd window popping up!
    "telegram": " tg:",
    "photos": " ms-photos:"
}

# The actual Windows process names needed to close the apps
PROCESS_NAMES = {
    "chrome": ["chrome.exe"],
    "vscode": ["Code.exe"],
    "explorer": ["explorer.exe"],
    "notepad": ["notepad.exe"],
    "calculator": ["CalculatorApp.exe"],
    "whatsapp": ["WhatsApp.exe"],
    "telegram": ["Telegram.exe"],
    # Windows constantly changes the Photos app name, so we target all of them!
    "photos": ["PhotosApp.exe", "Microsoft.Photos.exe", "Photos.exe"]
}

ALIASES = {
    "chrome": ["chrome","google chrome"],
    "vscode": ["vscode","vs code","code"],
    "explorer": ["explorer","file explorer","files","my computer"],   # in alias we can add more natural language variations for better recognition
    "notepad": ["notepad","notes"],
    "calculator":["calculator","calc"],
    "whatsapp":["whatsapp","what's app","what app", "whatsup" , " up" ],
    "telegram":["telegram"],
    "photos":["photos","gallery"]
}

# ---------------- LOGGING ----------------
def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    line = f"[{t}] {msg}"
    print(line)
    try:
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

# ---------------- APP HELPERS ----------------
def resolve_alias(name):
    for key, values in ALIASES.items():
        for v in values:
            if v in name:
                return key
    return None

def open_app(key):
    cmd = ALLOWED_APPS.get(key)
    if not cmd: return
    # Added creationflags=0x08000000 to hide the black CMD window!
    subprocess.run(f"cmd /c start {cmd}", shell=True, creationflags=0x08000000)
    log(f"Opened {key}")

def close_app(key):
    # Get the list of targets
    targets = PROCESS_NAMES.get(key, [key + ".exe"])
    
    # 1. THE STANDARD ASSASSIN (Works perfectly for Chrome, VS Code, Notepad)
    for exe in targets:
        subprocess.run(["taskkill", "/F", "/T", "/IM", exe], creationflags=0x08000000)
        
    # 2. THE POWERSHELL NUKE (Specifically bypasses the Microsoft Store Sandbox)
    if key == "whatsapp":
        subprocess.run('powershell -command "Stop-Process -Name *whatsapp* -Force"', shell=True, creationflags=0x08000000)
    elif key == "photos":
        subprocess.run('powershell -command "Stop-Process -Name *photo* -Force"', shell=True, creationflags=0x08000000)
        
    log(f"Closed {key}")

# ---------------- VOICE EXECUTION ----------------
def execute_voice(text):
    t = text.lower()

    if "volume up" in t:
        for _ in range(10): pyautogui.press("volumeup")
    elif "volume down" in t:
        for _ in range(10): pyautogui.press("volumedown")
    elif "play" in t or "resume" in t:
        pyautogui.press("playpause")
    elif "pause" in t:
        pyautogui.press("playpause")
    elif "next" in t:
        pyautogui.press("nexttrack")
    elif "previous" in t:
        pyautogui.press("prevtrack")
    elif "lock" in t:
        os.system("rundll32.exe user32.dll,LockWorkStation")
    elif "bluetooth on" in t:
        subprocess.run("powershell Start-Service bthserv", shell=True)
    elif "bluetooth off" in t:
        subprocess.run("powershell Stop-Service bthserv", shell=True)
    elif "nightlight" in t:
        subprocess.run("start ms-settings:nightlight", shell=True)
    elif t.startswith("open "):
        key = resolve_alias(t.replace("open ",""))
        if key: open_app(key)
    elif t.startswith("close "):
        key = resolve_alias(t.replace("close ",""))
        if key: close_app(key)

# ---------------- VOICE ENGINE ----------------
def voice_thread():
    if not os.path.exists(MODEL_PATH):
        log(f"Voice model missing at: {MODEL_PATH}")
        return

    model = Model(MODEL_PATH)
    
    vocab = [  # The grammar list of words/phrases we want Vosk to recognize for better accuracy
        "gp", "open", "close", "chrome", "vscode", "explorer", "notepad",
        "calculator", "telegram", "whatsapp", "photos", "whats" , "app" , "brightness",
        "volume", "up", "down", "play", "pause", "resume", "next", "previous",
        "bluetooth", "on", "off", "nightlight", "lock", "[unk]" , "Ehsaas"
    ]
    
     # Pass the grammar list into the recognizer as a JSON string
    rec = KaldiRecognizer(model, 16000, json.dumps(vocab))
    
    q = queue.Queue()

    def callback(indata, frames, time_info, status):
        q.put(bytes(indata))
        
    try:
        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=callback):

            log("VOICE ENGINE READY")
            awake = False
            wake_time = 0

            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    r = json.loads(rec.Result())
                    text = r.get("text", "")

                    if not text:
                        continue

                    log("Heard: " + text)

                    if WAKE_WORD in text:
                        awake = True
                        wake_time = time.time()
                        cmd = text.replace(WAKE_WORD, "").strip()
                        if cmd:
                            threading.Thread(target=execute_voice, args=(cmd,), daemon=True).start()
                            awake = False
                            
                    elif awake and time.time() - wake_time < 5:
                        threading.Thread(target=execute_voice, args=(text,), daemon=True).start()
                        awake = False
    except Exception as e:
        log(f"Voice engine error: {e}")

# ---------------- GESTURE ENGINE ----------------
def gesture_engine():
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    hands = mp_hands.Hands(
        max_num_hands=1,
        model_complexity=1, 
        min_detection_confidence=0.85,
        min_tracking_confidence=0.75
    )

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    try: cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
    except: pass

    screen_w, screen_h = pyautogui.size()
    prev_x, prev_y = pyautogui.position()

    stable_since = None
    pinch_start = None
    scroll_start = None
    palm_start = None
    swipe_x_start = None

    log("GESTURE ENGINE READY")

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.01)
            continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            lm = result.multi_hand_landmarks[0].landmark

            index = lm[8]
            thumb = lm[4]
            middle = lm[12]

            # --- POINTER MOVEMENT ---
            target_x = np.interp(index.x, (0.25, 0.75), (0, screen_w))
            target_y = np.interp(index.y, (0.25, 0.75), (0, screen_h))

            curr_x = prev_x + (target_x - prev_x) * SMOOTHING
            curr_y = prev_y + (target_y - prev_y) * SMOOTHING

            curr_x = max(0, min(screen_w - 1, curr_x))
            curr_y = max(0, min(screen_h - 1, curr_y))

            try: pyautogui.moveTo(curr_x, curr_y)
            except: pass

            movement = math.hypot(curr_x - prev_x, curr_y - prev_y)

            # --- DWELL LEFT CLICK ---
            if movement < 8:   # this value decides how much hand movement is allowed while still counting as "dwelling". 
                if stable_since is None:
                    stable_since = time.time()
                elif time.time() - stable_since > DWELL_CLICK_TIME:
                    pyautogui.click()
                    time.sleep(0.3)
                    log("DWELL CLICK")
                    stable_since = None
            else:
                stable_since = None

            prev_x, prev_y = curr_x, curr_y

            # --- PINCH RIGHT CLICK ---
            pinch_dist = math.hypot(thumb.x - index.x, thumb.y - index.y)
            if pinch_dist < 0.045:
                if pinch_start is None:
                    pinch_start = time.time()
                elif time.time() - pinch_start > RIGHT_CLICK_HOLD:
                    pyautogui.rightClick()
                    log("RIGHT CLICK")
                    pinch_start = time.time() + 0.5 
            else:
                pinch_start = None

          # --- GESTURE STATES (Two Fingers / Palm) ---
            tips = [8, 12, 16, 20]
            
            # 1. Standard V-Sign (Pointing UP)
            fingers_up = [lm[t].y < lm[t-2].y for t in tips]
            two_fingers_up = fingers_up[0] and fingers_up[1] and not fingers_up[2] and not fingers_up[3]
            
            # 2. Sideways V-Sign (Pointing LEFT like '>')
            fingers_left = [lm[t].x < lm[t-2].x for t in tips]
            two_fingers_left = fingers_left[0] and fingers_left[1] and not fingers_left[2] and not fingers_left[3]
            
            palm_up = all(fingers_up)

            
            # --- TWO FINGER SCROLL (up/down)(Continuous Smooth Glide) ---
            if two_fingers_up:
                # Hold standard V-sign to glide DOWN smoothly
                if scroll_start is None: 
                    scroll_start = time.time()
                elif time.time() - scroll_start > 0.3: # Snappy 0.3s delay to start scrolling
                    # Scroll a small amount every single frame while held
                    pyautogui.scroll(-200) 
                    # Notice we removed the 1.0s cooldown so it keeps gliding!
                    
            elif two_fingers_left:
                # Hold sideways V-sign (>) to glide UP smoothly
                if scroll_start is None: 
                    scroll_start = time.time()
                elif time.time() - scroll_start > 0.3:
                    pyautogui.scroll(400) 
            else:
                scroll_start = None

            # --- TWO FINGER SWIPE (Horizontal Forward/Back) ---
            if two_fingers_up:
                mid_x = ((index.x + middle.x) / 2.0) * w
                if swipe_x_start is None:
                    swipe_x_start = mid_x
                else:
                    dx = mid_x - swipe_x_start
                    if abs(dx) > SWIPE_THRESHOLD_PX:
                        if dx > 0:
                            log("SWIPE RIGHT (BACK)")
                            pyautogui.hotkey("alt", "left")
                        else:
                            log("SWIPE LEFT (FORWARD)")
                            pyautogui.hotkey("alt", "right")
                        swipe_x_start = mid_x  # Reset baseline after swipe
            else:
                swipe_x_start = None

            # --- PALM LOCK ---
            if palm_up:
                if palm_start is None:
                    palm_start = time.time()
                elif time.time() - palm_start > PALM_LOCK_TIME:
                    log("PALM LOCK")
                    os.system("rundll32.exe user32.dll,LockWorkStation")
                    palm_start = None
            else:
                palm_start = None

            if not HEADLESS:
                mp_draw.draw_landmarks(frame, result.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

        else:
            stable_since = None
            pinch_start = None
            scroll_start = None
            palm_start = None
            swipe_x_start = None

        if not HEADLESS:
            try:
                cv2.imshow("SmartGuard Ultra", frame)
                cv2.waitKey(1)
            except: pass

# ---------------- MAIN ----------------
def main():
    log("SMART GUARD STARTING")
    t = threading.Thread(target=voice_thread, daemon=True)
    t.start()
    gesture_engine()

if __name__ == "__main__":
    main()