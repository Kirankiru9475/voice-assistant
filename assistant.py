import speech_recognition as sr
import webbrowser
import pywhatkit
import ollama
import os
import subprocess

recognizer = sr.Recognizer()

APPS = {
    "notepad": "notepad",
    "calculator": "calc",
    "paint": "mspaint",
    "chrome": "chrome",
    "explorer": "explorer",
    "command prompt": "cmd",
    "settings": "ms-settings:",
    "wifi settings": "ms-settings:network-wifi",
    "bluetooth settings": "ms-settings:bluetooth",
    "display settings": "ms-settings:display",
}

def ask_ollama(text):
    prompt = (
        "You control a Windows laptop assistant. Reply ONLY with action lines, one per line, no extra words.\n"
        "Allowed lines:\n"
        "OPEN_YOUTUBE\n"
        "OPEN_SITE: <website address like mail.google.com or snapchat.com>\n"
        "PLAY: <song name>\n"
        "OPEN_APP: <one of: notepad, calculator, paint, chrome, explorer, command prompt, settings, wifi settings, bluetooth settings, display settings>\n"
        "SEARCH: <google search text>\n"
        "STOP\n"
        "CHAT: <short answer>\n"
        "If the user asks for several things, output several lines in order.\n"
        "User said: " + text
    )
    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()

def run_action(line):
    line = line.strip()
    if line.startswith("STOP"):
        return False
    elif line.startswith("OPEN_YOUTUBE"):
        webbrowser.open("https://www.youtube.com")
    elif line.startswith("PLAY:"):
        song = line.replace("PLAY:", "").strip()
        print("Playing:", song)
        pywhatkit.playonyt(song)
    elif line.startswith("OPEN_APP:"):
        app = line.replace("OPEN_APP:", "").strip().lower()
        if app in APPS:
            print("Opening:", app)
            subprocess.Popen("start " + APPS[app], shell=True)
        else:
            print("I don't know that app:", app)
    elif line.startswith("SEARCH:"):
        query = line.replace("SEARCH:", "").strip()
        webbrowser.open("https://www.google.com/search?q=" + query)
    elif line.startswith("CHAT:"):
        print(line.replace("CHAT:", "").strip())
    elif line.startswith("OPEN_SITE:"):
        site = line.replace("OPEN_SITE:", "").strip()
        if not site.startswith("http"):
            site = "https://" + site
        print("Opening site:", site)
        webbrowser.open(site)
    return True

with sr.Microphone() as source:
    recognizer.adjust_for_ambient_noise(source)
    print("Assistant ready. Say 'stop' to quit.")

    running = True
    while running:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            text = recognizer.recognize_google(audio, language="en-IN").lower()
            print("You said:", text)

            reply = ask_ollama(text)
            print("Ollama:", reply)

            for line in reply.split("\n"):
                if line.strip():
                    if not run_action(line):
                        print("Goodbye!")
                        running = False
                        break
        except sr.WaitTimeoutError:
            continue
        except sr.UnknownValueError:
            print("Could not understand, try again")
        except Exception as e:
            print("Error:", e)