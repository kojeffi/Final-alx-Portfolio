from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import pyttsx3
from PIL import Image
from threading import Thread


# Function to start/stop the hand tracking and classification process
def toggle_process(request):
    global running
    running = not running
    if running:
        start_button_text = "Stop Process"
        process_thread = Thread(target=process)
        process_thread.start()
    else:
        start_button_text = "Start Process"
    return render(request, 'index.html', {'start_button_text': start_button_text})


# Function to handle hand tracking and classification process
def process():
    global running, word
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
                word += alphabet
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
                word += alphabet
                speak_alphabet(alphabet)

            cv2.rectangle(imgOutput, (x - offset, y - offset - 50), (x - offset + 90,
                                                                     y - offset - 50 + 50), (255, 0, 255), cv2.FILLED)
            cv2.putText(imgOutput, labels[index], (x, y - 28), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 0, 0), 2)  # Changed the color to blue
            cv2.rectangle(imgOutput, (x - offset, y - offset), (x + w + offset, y + h + offset), (255, 0, 255), 4)

        _, buffer = cv2.imencode('.jpg', imgOutput)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        if cv2.waitKey(1) == ord('q'):
            break


# Function to convert alphabet to speech
def speak_alphabet(alphabet):
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.say(alphabet)
    engine.runAndWait()


# Function to clear the recognized word
def clear_word(request):
    global word
    word = []
    return render(request, 'index.html', {'start_button_text': 'Start Process'})


def video_feed(request):
    return StreamingHttpResponse(update_frame(), content_type='multipart/x-mixed-replace; boundary=frame')


def update_frame():
    while True:
        _, frame = cap.read()
        if frame is None:
            continue

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img.thumbnail((800, 600))
        _, buffer = cv2.imencode('.jpg', np.array(img))
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# Create the main window
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)
classifier = Classifier("keras_model.h5", "labels.txt")
offset = 20
imgSize = 300
labels = [
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E",
    "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S",
    "T", "U", "V", "W", "X", "Y", "Z"
]
word = []
running = False