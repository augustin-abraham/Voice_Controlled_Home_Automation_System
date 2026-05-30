import os
import sys
import time
import random
import RPi.GPIO as GPIO
import speech_recognition as sr
from RPLCD.i2c import CharLCD
from flask import Flask, render_template, request
import subprocess
import multiprocessing  # ✅ replaces threading for Flask

# --- LCD Setup (I2C 0x3F, 16x4 display) ---
lcd = CharLCD('PCF8574', 0x3F, cols=16, rows=4)
lcd.clear()

def display_on_lcd(line1='', line2='', line3='', line4=''):
    lcd.clear()
    lines = [line1, line2, line3, line4]
    for i, line in enumerate(lines):
        if line:
            lcd.cursor_pos = (i, 0)
            lcd.write_string(line[:16])
    time.sleep(0.2)

# --- Suppress ALSA/JACK warnings ---
sys.stderr = open(os.devnull, 'w')
try:
    from ctypes import CDLL
    asound = CDLL('libasound.so')
    asound.snd_lib_error_set_handler(None)
except:
    pass
sys.stderr = sys.__stderr__

# --- GPIO Setup ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

light = 17
buzzer = 22
servo_pin = 23
error_led = 24
motor_in1 = 5
motor_in2 = 6

GPIO.setup(light, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(buzzer, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(error_led, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_in1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(motor_in2, GPIO.OUT, initial=GPIO.LOW)

# --- Servo setup ---
GPIO.setup(servo_pin, GPIO.OUT)
servo_pwm = GPIO.PWM(servo_pin, 50)
servo_pwm_started = False
_current_servo_angle = 0

def _angle_to_duty(angle):
    return 2.5 + (float(angle) / 18.0)

def set_servo_angle(angle, step_delay=0.02):
    global _current_servo_angle, servo_pwm, servo_pwm_started
    angle = max(0, min(180, int(angle)))
    if not servo_pwm_started:
        servo_pwm.start(0)
        servo_pwm_started = True
        time.sleep(0.1)
    start = _current_servo_angle
    if start == angle:
        return
    step = 1 if angle > start else -1
    for a in range(start, angle + step, step):
        duty = _angle_to_duty(a)
        servo_pwm.ChangeDutyCycle(duty)
        time.sleep(step_delay)
    time.sleep(0.05)
    servo_pwm.ChangeDutyCycle(0)
    _current_servo_angle = angle

def open_gate():
    speak("Opening gate")
    set_servo_angle(90)
    beep(0.2)

def close_gate():
    speak("Closing gate")
    set_servo_angle(0)
    beep(0.2)

# --- Buzzer + LED functions ---
def beep(duration=0.3):
    GPIO.output(buzzer, GPIO.HIGH)
    GPIO.output(error_led, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(buzzer, GPIO.LOW)
    GPIO.output(error_led, GPIO.LOW)

def error_beep():
    for _ in range(3):
        GPIO.output(buzzer, GPIO.HIGH)
        GPIO.output(error_led, GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(buzzer, GPIO.LOW)
        GPIO.output(error_led, GPIO.LOW)
        time.sleep(0.3)

def play_rhythm():
    notes = [0.1, 0.1, 0.2, 0.1, 0.3]
    for note in notes:
        GPIO.output(buzzer, GPIO.HIGH)
        GPIO.output(error_led, GPIO.HIGH)
        time.sleep(note)
        GPIO.output(buzzer, GPIO.LOW)
        GPIO.output(error_led, GPIO.LOW)
        time.sleep(0.05)

# --- Speak function ---
def speak(text):
    print(text)
    display_on_lcd(text)
    os.system(f'espeak "{text}"')

# --- Music Player Function ---
music_process = None
songs_dir = os.path.expanduser("~/voice_control_project/songs")
def play_music():
    """Play a random song from ~/voice_control_project/songs."""
    global music_process
    songs_dir = os.path.expanduser("~/voice_control_project/songs")
    if not os.path.exists(songs_dir):
        speak("Songs folder not found")
        error_beep()
        return

    files = [f for f in os.listdir(songs_dir) if f.lower().endswith(('.mp3', '.wav'))]
    if not files:
        speak("No music files found")
        error_beep()
        return

    # Stop any existing playback
    stop_music()

    song = random.choice(files)
    song_path = os.path.join(songs_dir, song)
    speak(f"Playing {song}")
    display_on_lcd("Playing:", song[:16])

    # Use mpg123 for MP3 or aplay for WAV
    cmd = ["mpg123", "-q", song_path] if song.endswith(".mp3") else ["aplay", song_path]
    music_process = subprocess.Popen(cmd)


def stop_music():
    """Stop any running music playback."""
    global music_process
    if music_process and music_process.poll() is None:
        music_process.terminate()
        speak("Music stopped")
        display_on_lcd("Music stopped")
        beep(0.2)
        music_process = None


# --- Flask Setup ---
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control():
    device = request.form.get('device')
    action = request.form.get('action')

    if device == 'light':
        if action == 'on':
            GPIO.output(light, GPIO.LOW)
            speak("Light turned on")
        else:
            GPIO.output(light, GPIO.HIGH)
            speak("Light turned off")

    elif device == 'fan':
        if action == 'on':
            GPIO.output(motor_in1, GPIO.HIGH)
            GPIO.output(motor_in2, GPIO.LOW)
            speak("Fan turned on")
        else:
            GPIO.output(motor_in1, GPIO.LOW)
            GPIO.output(motor_in2, GPIO.LOW)
            speak("Fan turned off")

    elif device == 'gate':
        if action == 'open':
            open_gate()
        else:
            close_gate()

    elif device == 'music':
        if action == 'play':
            play_music()
        else:
            stop_music()

    return render_template('index.html')

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# ✅ Instead of thread, run Flask in a separate process
flask_process = multiprocessing.Process(target=run_flask)
flask_process.start()

# --- Speech Recognition Setup ---
recognizer = sr.Recognizer()
recognizer.energy_threshold = 60
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.05
recognizer.dynamic_energy_ratio = 1.5

mic_name = "USB PnP Sound Device"
mic_index = None
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    if mic_name in name:
        mic_index = i
        break
if mic_index is None:
    raise Exception("USB microphone not found!")

mic = sr.Microphone(device_index=mic_index)

with mic as source:
    print("Calibrating mic for ambient noise...")
    display_on_lcd("Calibrating", "microphone...")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    print(f"Ambient noise level set to: {recognizer.energy_threshold}")

display_on_lcd("Voice Control", "System Ready", "Say 'Hey BUDDY'")
time.sleep(1)

# --- Trigger Loop ---
while True:
    with mic as source:
        print("\nSay 'Hey Pi' to activate...")
        display_on_lcd("Waiting for", "trigger: 'Hey BUDDY'")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
            command = recognizer.recognize_google(audio).lower()
            print("You said:", command)
            display_on_lcd("Heard:", command)
            if "hey buddy" in command:
                play_rhythm()
                speak("Yes, I am listening. You can give commands now.")
                print("Trigger detected. Entering command mode...")
                time.sleep(1)
                break
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            display_on_lcd("No trigger word", "heard...")
            time.sleep(0.5)

# --- Main Command Loop ---
try:
    while True:
        with mic as source:
            print("\nListening for command...")
            display_on_lcd("Listening for", "command...")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
                cmd = recognizer.recognize_google(audio).lower()
                print("Command:", cmd)
                display_on_lcd("Command:", cmd)

                if any(x in cmd for x in ["turn on light", "light on", "lights on"]):
                    GPIO.output(light, GPIO.LOW)
                    speak("Light turned on")
                    beep(0.3)

                elif any(x in cmd for x in ["turn off light", "light off", "lights off"]):
                    GPIO.output(light, GPIO.HIGH)
                    speak("Light turned off")
                    beep(0.3)

                elif any(x in cmd for x in ["fan on", "turn on fan", "start fan"]):
                    GPIO.output(motor_in1, GPIO.HIGH)
                    GPIO.output(motor_in2, GPIO.LOW)
                    speak("Fan turned on")
                    beep(0.3)

                elif any(x in cmd for x in ["fan off", "turn off fan", "stop fan"]):
                    GPIO.output(motor_in1, GPIO.LOW)
                    GPIO.output(motor_in2, GPIO.LOW)
                    speak("Fan turned off")
                    beep(0.3)

                elif any(x in cmd for x in ["open gate", "gate open", "open the gate"]):
                    open_gate()

                elif any(x in cmd for x in ["close gate", "gate close", "close the gate"]):
                    close_gate()

                elif "play music" in cmd or "start music" in cmd:
                    play_music()

                elif "stop music" in cmd or "pause music" in cmd:
                    stop_music()

                elif any(x in cmd for x in ["stop", "exit", "quit"]):
                    speak("Goodbye!")
                    play_rhythm()
                    break

                else:
                    speak("Sorry, I did not understand")
                    error_beep()

            except (sr.UnknownValueError, sr.WaitTimeoutError):
                display_on_lcd("Command not", "recognized")
                error_beep()
                time.sleep(0.5)

except KeyboardInterrupt:
    print("Program stopped manually")
    display_on_lcd("Program stopped")

finally:
    stop_music()
    if servo_pwm_started:
        servo_pwm.ChangeDutyCycle(0)
        servo_pwm.stop()
    GPIO.cleanup()
    lcd.clear()
    lcd.write_string("GPIO cleaned up.")
    print("GPIO cleaned up. Program ended.")
    flask_process.terminate()  
