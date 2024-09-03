from ast import Global
from pickle import TRUE
import cv2
import dlib
from imutils import face_utils
from scipy.spatial import distance as dist
import streamlit as st
import cv2
import smtplib
from datetime import datetime
from streamlit.components.v1 import html
import base64

# Define your javascript
my_js = """
document.addEventListener("visibilitychange", (event) => {
  if (document.visibilityState == "visible") {
    console.log("tab is active")
  } else {
    alert("tab is inactive")
  }
});
"""

my_js2 = """window.alert(""Please Pay attention !!");"""

my_js3 = """window.open( "https://meet.google.com/", ""); """
# Wrapt the javascript as html code
my_html = f"<script>{my_js}</script>"
my_html2 = f"<script>{my_js2}</script>"
my_html3 = f"<script>{my_js3}</script>"
#Global Configuration Variables
FACIAL_LANDMARK_PREDICTOR = "shape_predictor_68_face_landmarks.dat"  # path to dlib's pre-trained facial landmark predictor
MINIMUM_EAR = 0.26    # Minimum EAR for both the eyes to mark the eyes as open
MAXIMUM_FRAME_COUNT = 48    # Maximum number of consecutive frames in which EAR can remain less than MINIMUM_EAR, otherwise alert drowsiness
FLAG = True




#Initializations
faceDetector = dlib.get_frontal_face_detector()     # dlib's HOG based face detector
landmarkFinder = dlib.shape_predictor(FACIAL_LANDMARK_PREDICTOR)  # dlib's landmark finder/predcitor inside detected face

# Finding landmark id for left and right eyes
(leftEyeStart, leftEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rightEyeStart, rightEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

def eye_aspect_ratio(eye):
    
    p2_minus_p6 = dist.euclidean(eye[1], eye[5])
    p3_minus_p5 = dist.euclidean(eye[2], eye[4])
    p1_minus_p4 = dist.euclidean(eye[0], eye[3])
    ear = (p2_minus_p6 + p3_minus_p5) / (2.0 * p1_minus_p4)
    return ear


def app():
    st.header("Online Lecture")
    global FLAG
    Meet = st.button("Join Meet")
    run = st.checkbox('Start Lecture')
    if Meet:
        html(my_html3)
        
    NO_OF_WARNINGS = 0
    EYE_CLOSED_COUNTER = 0
    
    FRAME_WINDOW = st.image([])      
    webcam = cv2.VideoCapture(0)
    while run:
        # read frame from webcam 
        status, frame = webcam.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        grayImage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceDetector(grayImage, 0)

        #if (len(faces) == 0):
           # cv2.putText(frame, "No Face Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        for face in faces:
            
            faceLandmarks = landmarkFinder(grayImage, face)
            faceLandmarks = face_utils.shape_to_np(faceLandmarks)

            leftEye = faceLandmarks[leftEyeStart:leftEyeEnd]
            rightEye = faceLandmarks[rightEyeStart:rightEyeEnd]

            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            ear = (leftEAR + rightEAR) / 2.0

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)

            cv2.drawContours(frame, [leftEyeHull], -1, (255, 0, 0), 2)
            cv2.drawContours(frame, [rightEyeHull], -1, (255, 0, 0), 2)

            if ear < MINIMUM_EAR:
                EYE_CLOSED_COUNTER += 1
            else:
                EYE_CLOSED_COUNTER = 0

            cv2.putText(frame, "EAR: {:.2f}".format(ear), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            if EYE_CLOSED_COUNTER >= MAXIMUM_FRAME_COUNT:
                cv2.putText(frame, "Drowsiness", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                FLAG = False
                
        FRAME_WINDOW.image(frame)
        
    else:
        st.write('Stopped')
        #st.write(Flag)
    submit = st.button("Submit")
    if submit:
        #st.write(FLAG)
        if(FLAG == False):
            result = "Subject: Online Lec \n\n Student was not paying attention"
            s = "Student was not paying attention"
        else:
            result = "Subject: Online Lec \n\n Student was paying attention"
            s = "Student was paying attention"
        st.write(s)
        conn = smtplib.SMTP('imap.gmail.com',587)
        conn.ehlo()
        conn.starttls()
        conn.login('tdesai.me@student.sfit.ac.in', 'Tanmay007')
        conn.sendmail('tdesai.me@student.sfit.ac.in','tdesai.me@gmail.com',result)
        conn.quit()
        FLAG = True
    #html(my_html)
        
        
        
