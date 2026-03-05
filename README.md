# 🌌 Ehsaas

**Ehsaas** is an AI-powered **gesture controlled virtual mouse and offline voice command system** built using Python.

It allows users to control their computer using **hand gestures in the air and simple voice commands**, reducing the need for a physical mouse or keyboard.

The word *Ehsaas* means **perception or awareness**.
This project aims to give computers the ability to **perceive human gestures and voice** and respond in real time.

---

# 🚀 Overview

Ehsaas combines multiple technologies to create a hands-free interaction system:

* Computer Vision for gesture recognition
* Offline Speech Recognition for voice commands
* System Automation for controlling applications and settings

Using a **webcam and microphone**, the system detects gestures and voice commands and translates them into real computer actions.

Everything runs **locally on the device**, ensuring privacy and low latency.

---

# ✨ Key Features

| Feature                  | Description                                   |
| ------------------------ | --------------------------------------------- |
| AI Virtual Mouse         | Control cursor using finger movement          |
| Anti-Jitter Smoothing    | Smooth pointer movement using interpolation   |
| Dwell Click              | Hold finger still to trigger left click       |
| Pinch Right Click        | Pinch thumb and index finger                  |
| Air Scroll               | Two-finger gesture for scrolling              |
| Air Swipe Navigation     | Horizontal swipe for browser forward/back     |
| Palm Lock                | Open palm gesture instantly locks Windows     |
| Offline Voice Assistant  | Control apps and system using voice           |
| Wake Word Activation     | Commands begin with **"gp"**                  |
| Multithreaded Processing | Voice and gesture systems run simultaneously  |
| Silent App Control       | Apps open/close without command window popups |
| Logging System           | Activity logs stored in `Ehsaas.log`          |

---

# 🖐 Gesture Controls

The system detects gestures using **MediaPipe hand landmarks**.

| Gesture                     | Action                 |
| --------------------------- | ---------------------- |
| Index finger movement       | Move mouse cursor      |
| Hold finger still           | Left Click             |
| Pinch thumb + index         | Right Click            |
| Two-finger V gesture        | Scroll Down            |
| Sideways V (`>`) gesture    | Scroll Up              |
| Two-finger horizontal swipe | Browser Back / Forward |
| Open palm                   | Lock Windows computer  |

Gesture detection uses **geometric thresholds and hold timers** to avoid accidental actions.

---

# 🎤 Voice Command System

Ehsaas includes an **offline voice assistant** built using Vosk speech recognition.

Commands use a wake word:

```
gp
```

Example commands:

```
gp open chrome
gp close chrome
gp volume up
gp volume down
gp play
gp pause
gp next
gp previous
gp lock
```

Voice commands can:

* open applications
* close running apps
* control media playback
* adjust system volume
* toggle Bluetooth
* open system settings

Speech recognition runs **completely offline**.

---

# ⚡ System Automation

Ehsaas interacts directly with Windows using system commands.

| Capability         | Method                  |
| ------------------ | ----------------------- |
| Open Applications  | Windows `start` command |
| Close Applications | `taskkill` + PowerShell |
| Media Controls     | Keyboard media keys     |
| Lock Computer      | Windows system API      |

Supported applications include:

* Chrome
* VS Code
* File Explorer
* Notepad
* Calculator
* WhatsApp
* Telegram
* Windows Photos

Alias mapping allows **natural language variations** for voice commands.

---

# 🧠 Technologies Used

| Technology  | Purpose                             |
| ----------- | ----------------------------------- |
| Python      | Core programming language           |
| OpenCV      | Webcam capture and image processing |
| MediaPipe   | Hand landmark detection             |
| Vosk        | Offline speech recognition          |
| PyAutoGUI   | Mouse and keyboard automation       |
| NumPy       | Mathematical calculations           |
| SoundDevice | Microphone audio input              |

---

# 🏗 System Architecture

Ehsaas runs two main engines simultaneously:

| Engine         | Purpose                                  |
| -------------- | ---------------------------------------- |
| Gesture Engine | Detects hand gestures from webcam frames |
| Voice Engine   | Processes microphone input for commands  |

The voice engine runs in a **separate thread**, allowing both systems to operate in real time.

---

# 🛠 Installation

### 1️⃣ Install Python

Install **Python 3.9 or later**.

---

### 2️⃣ Install Dependencies

```
pip install opencv-python numpy pyautogui sounddevice vosk mediapipe
```

---

### 3️⃣ Download Speech Model

Download the Vosk speech model:

```
vosk-model-small-en-us-0.15
```

Extract it into the project folder.

---

### 4️⃣ Project Structure

```
ehsaas/
│
├── Ehsaas.py
├── Ehsaas.log
├── vosk-model-small-en-us-0.15/
└── README.md
```

---

### 5️⃣ Run the Program

```
python Ehsaas.py
```

Optional runtime arguments:

```
python Ehsaas.py --headless
python Ehsaas.py --fps 30
python Ehsaas.py --model vosk-model-small-en-us-0.15
```

---

# 🎯 Use Cases

* Hands-free computer interaction
* Accessibility tools for limited mobility users
* Gesture-based user interface research
* Computer vision learning projects
* AI powered desktop control systems

---

# 🔮 Future Improvements

Possible extensions for the project:

* Face authentication system
* Custom gesture training
* Graphical control panel (GUI)
* Multi-language voice recognition
* Cross-platform support (Linux / macOS)

---

# 👤 Author

**Harkirat Singh**
Computer Engineering Student
Thapar Institute of Engineering & Technology

---

# 📄 License
This project is open source and available under the **MIT License**.



* Development Notes *

This project was built using AI-assisted development tools.
The author designed the system architecture, features, and functionality, and guided the development process by:

-defining project requirements
-identifying bugs and improvements
-testing and refining the system
-directing implementation decisions

AI tools (chat gpt and gemini) were used to help generate and refine portions of the code during development.
The final system design, testing, and feature integration were directed by the project author.
