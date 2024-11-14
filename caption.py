import ctypes
import pygetwindow as gw
import pyautogui
import pytesseract
from deep_translator import GoogleTranslator
import pyttsx3
import time
import os
import re

# Set up Tesseract path (modify based on your installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize the translator
translator = GoogleTranslator(source='en', target='ru')

# Initialize text-to-speech engine with increased speed
engine = pyttsx3.init()
engine.setProperty('rate', 300)  # Set faster reading rate
engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_RU-RU_IRINA_11.0')  # Set Russian voice

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def normalize_text(text):
    """Normalize the text to a consistent format."""
    text = text.lower()  # Приводим к нижнему регистру
    text = re.sub(r'\s+', ' ', text)  # Убираем лишние пробелы
    text = re.sub(r'[^\w\s.,|?]', '', text)  # Удаляем знаки препинания, кроме точки, запятой, '|', и вопросительного знака
    return text.strip()

def activate_live_captions():
    """Simulate Win + Ctrl + L to start Live Captions."""
    ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # Win key down
    ctypes.windll.user32.keybd_event(0x11, 0, 0, 0)  # Ctrl key down
    ctypes.windll.user32.keybd_event(0x4C, 0, 0, 0)  # L key down
    ctypes.windll.user32.keybd_event(0x4C, 0, 2, 0)  # L key up
    ctypes.windll.user32.keybd_event(0x11, 0, 2, 0)  # Ctrl key up
    ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # Win key up

def capture_translate_and_speak_text():
    # Activate "Live Captions" at the start
    activate_live_captions()
    time.sleep(2)  # Give a moment for "Live Captions" to start

    # Find the "Live Captions" window
    live_captions_window = None
    for window in gw.getWindowsWithTitle("Live Captions"):
        live_captions_window = window
        break

    if not live_captions_window:
        print("Live Captions app window not found.")
        return

    last_spoken_text = ""  # Store the last spoken portion to avoid repetition

    while True:
        # Get the window's position and size
        x, y, width, height = (live_captions_window.left,
                               live_captions_window.top,
                               live_captions_window.width,
                               live_captions_window.height)
        
        # Capture the window screenshot
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        
        # Extract text from the screenshot
        text = pytesseract.image_to_string(screenshot, lang="eng").strip()
        
        # Only proceed if we got new text
        if text:
            # Translate and normalize text
            translated_text = translator.translate(text)
            normalized_text = normalize_text(translated_text)
            
            # Clear console and display the full translated text without '|'
            clear_console()
            print(translated_text.replace('|', ''))

            # Determine the new part to speak based on '.', ',', '|', and '?' symbols
            sentences = re.split(r'[.,|?]', normalized_text)
            new_part = ""
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and sentence not in last_spoken_text:
                    new_part += sentence + '. '

            # Only speak the new part if it exists
            if new_part:
                engine.say(new_part)
                engine.runAndWait()  # Озвучиваем текст, без многопоточности
                last_spoken_text += new_part  # Обновляем озвученный текст

        time.sleep(0.2)  # Reduce delay for faster updates

# Run the capture, translate, and speak function
capture_translate_and_speak_text()
