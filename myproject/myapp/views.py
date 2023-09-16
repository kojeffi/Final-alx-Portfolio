import cv2
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import time
from threading import Thread
import pyttsx3
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

# Initialize the webcam capture
cap = cv2.VideoCapture(0)

# Initialize the hand detector and classifier
detector = HandDetector(maxHands=1)
classifier = Classifier("keras_model.h5", "labels.txt")

offset = 20
imgSize = 300

# "1","2","3","4","5","6","7","8","9",


labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
          "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

word = []
word_label = ""

# Function to start/stop the hand tracking and classification process
running = False


def toggle_process(request):
    global running, word_label
    running = not running
    if running:
        start_button_text = "Stop Process"
        # Update this line to match your HTML button element
        process_thread = Thread(target=process)
        process_thread.start()
    else:
        start_button_text = "Start Process"  # Update this line to match your HTML button element
    return render(request, 'base.html', {'running': running, 'start_button_text': start_button_text, 'word_label': word_label})


# Function to handle hand tracking and classification process
def process():
    global running, word, word_label
    while running:
        success, img = cap.read()
        if not success:
            continue

        imgOutput = img.copy()
        hands, img = detector.findHands(img)
        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']

            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8)

            imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]

            imgCropShape = imgCrop.shape

            aspectRatio = h / w

            if aspectRatio > 1:
                k = imgSize / h
                wCal = math.ceil(k * w)
                imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                imgResizeShape = imgResize.shape
                wGap = math.ceil((imgSize - wCal) / 2)
                imgWhite[:, wGap:wCal + wGap] = imgResize
                prediction, index = classifier.getPrediction(imgWhite, draw=False)
                alphabet = labels[index]
                word.append(alphabet)
                speak_alphabet(alphabet)

            else:
                k = imgSize / w
                hCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                imgResizeShape = imgResize.shape
                hGap = math.ceil((imgSize - hCal) / 2)
                imgWhite[hGap:hCal + hGap, :] = imgResize
                prediction, index = classifier.getPrediction(imgWhite, draw=False)
                alphabet = labels[index]
                word.append(alphabet)
                speak_alphabet(alphabet)

            cv2.rectangle(imgOutput, (x - offset, y - offset - 50), (x - offset + 90,
                                                                      y - offset - 50 + 50), (255, 0, 255),
                          cv2.FILLED)
            cv2.putText(imgOutput, labels[index], (x, y - 28), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
            cv2.rectangle(imgOutput, (x - offset, y - offset), (x + w + offset, y + h + offset), (255, 0, 255), 4)

        cv2.imshow("Image", imgOutput)
        if cv2.waitKey(1) == ord('q'):
            break

        word_label = "Recognized Alphabets: " + " " + " ,".join(word)
    cv2.destroyAllWindows()


# Function to convert alphabet to speech
def speak_alphabet(alphabet):
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.say(alphabet)
    engine.runAndWait()

# Function to clear the recognized word
def clear_word(request):
    global word, word_label
    word = []
    word_label = "Recognized Alphabets:"
    return render(request, 'base.html', {'running': running, 'start_button_text': "Start Process", 'word_label': word_label})

from django.shortcuts import render,redirect
from .forms import registrationform,User
# from django.contrib.auth.views import login

def registration(request):
    if request.method == 'POST':
        form = registrationform(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page
    else:
        form = registrationform()
    return render(request, 'registration.html', {'form': form})

# Change the view name from `login` to `custom_login`
def custom_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)  # Use the imported `login` function from `django.contrib.auth.views`
            return render(request, 'base.html')
    else:
        return render(request, 'login.html')


def base(request):
    return render(request, 'base.html')
def base(request):
    return render(request, 'base.html', {'running': running,
    'start_button_text': "Start Process", 'word_label': word_label})

def index(request):
    return render(request, 'index.html')
def about(request):
    return render(request, 'about.html')


def services(request):
    return render(request, 'services.html')


def dashboard(request):
    return render(request, 'dashboard.html')


# Function to stream video frames and recognized words to the front end
def video_feed(request):
    def generate_frames():
        global word_label
        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

            # Yield the recognized words as a Server-Sent Event (SSE)
            yield "data: {0}\n\n".format(word_label)
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

import os

def save_recognized_alphabets(request):
    global word
    if request.method == 'POST':
        # Get the recognized alphabets
        recognized_word = " ".join(word)

        # Define the file path where you want to save the recognized alphabets
        file_path = "recognized_alphabets.txt"

        # Check if the file exists, and create it if it doesn't
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                file.write("")  # Create an empty file

        # Open the file in append mode and write the recognized word
        with open(file_path, "a") as file:
            file.write(recognized_word + "\n")

    return render(request, 'base.html', {'running': running, 'start_button_text': "Start Process", 'word_label': word_label})




from django.shortcuts import render

def view_recognized_alphabets(request):
    file_path = "recognized_alphabets.txt"
    recognized_alphabets = []

    # Check if the file exists
    if os.path.exists(file_path):
        # Read the contents of the file
        with open(file_path, "r") as file:
            recognized_alphabets = file.readlines()

    return render(request, 'view_recognized_alphabets.html', {'recognized_alphabets': recognized_alphabets})


from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse


# Import any other necessary modules

def clear_recognized_alphabets(request):
    # Logic to clear the recognized alphabets goes here
    # For example, you can clear the 'recognized_alphabets.txt' file
    file_path = "recognized_alphabets.txt"

    # Ensure the file exists and open it in write mode to clear its contents
    if os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write("")

    # Redirect back to the 'view_recognized_alphabets' view
    return HttpResponseRedirect(reverse('view_recognized_alphabets'))

