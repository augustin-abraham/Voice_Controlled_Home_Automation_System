# Voice Controlled Home Automation System

A Raspberry Pi-based smart home automation system that enables users to control appliances using voice commands or a web-based dashboard. The system integrates speech recognition, GPIO-based device control, servo motor automation, LCD feedback, and Flask web services to provide an interactive and user-friendly home automation experience.

---

## Project Overview

This project implements a voice-controlled home automation system using Raspberry Pi. The system continuously listens for a wake word and executes user commands to control connected devices such as lights, fans, gates, and music playback.

In addition to voice control, a Flask-based web interface allows users to remotely control appliances through a browser. Real-time system status is displayed on an I2C LCD, while audio feedback is provided through text-to-speech functionality.

---

## Features

* Voice-controlled appliance operation
* Wake-word activation ("Hey Buddy")
* Flask-based web dashboard
* Smart gate automation using servo motor
* Light control using GPIO
* Fan/motor control
* LCD status display
* Text-to-speech feedback
* Music playback control
* Buzzer and LED notifications
* Real-time command execution

---

## Hardware Components

* Raspberry Pi
* USB Microphone
* I2C LCD Display (16x4)
* Servo Motor
* DC Motor / Fan
* Buzzer
* LEDs
* Relay Modules (optional)
* Wi-Fi Network

---

## Software Technologies

* Python
* Flask
* SpeechRecognition
* RPi.GPIO
* RPLCD
* Linux (Raspberry Pi OS)
* HTML/CSS
* Google Speech Recognition API
* eSpeak Text-to-Speech

---

## System Workflow

1. System waits for the wake word **"Hey Buddy"**.
2. Voice command is captured using a USB microphone.
3. Speech recognition converts audio into text.
4. Raspberry Pi processes the command.
5. GPIO devices are controlled based on the command.
6. LCD displays the current system status.
7. Audio feedback is provided through text-to-speech.
8. Users can alternatively control devices through the Flask web dashboard.

---

## Supported Voice Commands

### Lighting

* Turn on light
* Turn off light

### Fan Control

* Turn on fan
* Turn off fan

### Smart Gate

* Open gate
* Close gate

### Music Player

* Play music
* Stop music

### System Commands

* Exit
* Stop

---

## Project Structure

```text
Voice_Controlled_Home_Automation_System/
│
├── source_code/
│   └── voice_home_automation.py
│
├── web_interface/
│   ├── index.html
│   └── style.css
│
├── images/
│   ├── system_setup.jpg
│   ├── web_dashboard.png
│   ├── lcd_display.jpg
│   └── hardware_connections.jpg
│
├── requirements.txt
│
└── README.md
```

---

## Applications

* Smart Home Automation
* Voice Assistant Systems
* IoT-Based Appliance Control
* Smart Access Control
* Home Security Systems
* Assistive Technology

---

## Skills Demonstrated

* Raspberry Pi Development
* Python Programming
* Embedded Linux
* Speech Recognition
* Flask Web Development
* GPIO Programming
* Servo Motor Control
* LCD Interfacing
* Human-Machine Interaction
* IoT Concepts

---

## Future Enhancements

* Mobile Application Integration
* MQTT-Based Communication
* Cloud Monitoring Dashboard
* Face Recognition Authentication
* Smart Energy Monitoring
* AI-Based Voice Assistant

---

## Author

**Augustin C Abraham**

MSc Electronics

Embedded Systems | IoT | Raspberry Pi | Verilog HDL | Semiconductor Enthusiast
