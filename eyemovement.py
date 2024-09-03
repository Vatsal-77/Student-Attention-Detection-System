
from enum import Flag
from glob import glob
import cv2
from gaze_tracking import GazeTracking
import streamlit as st
import smtplib
from datetime import datetime
import base64
from streamlit.components.v1 import html
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import winsound
frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second

# Define your javascript
my_js = f"""
counter = 4

document.addEventListener("visibilitychange", (event) => {{
  if (document.visibilityState == "visible") {{
    console.log("tab is active")
  }} else {{
    
        alert("Please don't switch tabs");
    
  }}
}});
"""


# Wrapt the javascript as html code
my_html = f"<script>{my_js}</script>"


NO_OF_WARNINGS = 3
MAXIMUM_FRAME_COUNT = 150
FLAG = True
WARNING_FRAME_COUNT = 90
UPLOADED_FILE_PATH = " "

def upload_file():
    global UPLOADED_FILE_PATH
    pdf_file = st.file_uploader("Upload File", type=["pdf"])

    if pdf_file is not None:
			  # TO See details
        file_details = {"filename":pdf_file.name, "filetype":pdf_file.type,
                              "filesize":pdf_file.size}
        st.write(file_details)
		
			  
			  #Saving upload
    if(pdf_file == None):
        st.write("Please Upload Answer sheet")
    else:
        with open(os.path.join("uploads",pdf_file.name),"wb") as f:
            f.write((pdf_file).getbuffer())
        UPLOADED_FILE_PATH = os.path.join("uploads",pdf_file.name)  
        st.success("File Uploaded Succesfuly")
        st.write(UPLOADED_FILE_PATH)


def send_mail():
    global UPLOADED_FILE_PATH
    global FLAG
    
    if(FLAG == False):
        result = "Student was looking left and right"
        body = "Student was looking left and right but in limits"
    else:
        result = "No malicious Activities detected"
        body = "No malicious Activities detected "
    message = MIMEMultipart()
    message['From'] = 'tdesai.me@gmail.com'
    message['To'] = 'tdesai.me@student.sfit.ac.in'
    message['Subject'] = 'Test Summary'
 
    message.attach(MIMEText(body, 'plain'))
 
    pdfname = UPLOADED_FILE_PATH
 
    # open the file in bynary
    binary_pdf = open(pdfname, 'rb')
 
    payload = MIMEBase('application', 'octate-stream', Name=pdfname)
    # payload = MIMEBase('application', 'pdf', Name=pdfname)
    payload.set_payload((binary_pdf).read())
 
    # enconding the binary into base64
    encoders.encode_base64(payload)
 
    # add header with pdf name
    payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)
    message.attach(payload)


    st.write(result)
    conn = smtplib.SMTP('imap.gmail.com',587)
    conn.ehlo()
    conn.starttls()
    conn.login('tdesai.me@student.sfit.ac.in', 'Tanmay007')
    text = message.as_string()
    conn.sendmail('tdesai.me@student.sfit.ac.in','tdesai.me@gmail.com',text)
    conn.quit()
    FLAG = True  
    

def app():
    st.header("Online Exam")
    global FLAG
    global last_detected
    global NO_OF_WARNINGS
    i = 0
    
    from gaze_tracking import GazeTracking
    gaze = GazeTracking()
    webcam = cv2.VideoCapture(0)
    EYE_COUNTER = 0
    run = st.checkbox('Start Exam')
    FRAME_WINDOW = st.image([])
    while run:
        # We get a new frame from the webcam
        _, frame = webcam.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # We send this frame to GazeTracking to analyze it
        gaze.refresh(frame)

        frame = gaze.annotated_frame()
        text = ""

        
        if gaze.is_right():
            text = "Looking right"
            EYE_COUNTER = EYE_COUNTER + 1
        elif gaze.is_left():
            text = "Looking left"
            EYE_COUNTER = EYE_COUNTER + 1
        elif gaze.is_up():
            text = "Looking Up"
            EYE_COUNTER = EYE_COUNTER + 1
        if(NO_OF_WARNINGS == 0):
            cv2.putText(frame, "Last Warning", (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, (147, 58, 31), 2)
        else:
            cv2.putText(frame, f"No of warnings remaining: {NO_OF_WARNINGS}", (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.putText(frame, text, (10, 50), cv2.FONT_HERSHEY_DUPLEX, 0.7, (147, 58, 31), 2)
        if(EYE_COUNTER>= MAXIMUM_FRAME_COUNT):
            FLAG = False
            EYE_COUNTER = 0
            i = 0

        if(i==1 and FLAG == False):
            winsound.Beep(frequency, duration)
            NO_OF_WARNINGS = NO_OF_WARNINGS - 1
        
        if(NO_OF_WARNINGS == -1 ):
            conn = smtplib.SMTP('imap.gmail.com',587)
            conn.ehlo()
            conn.starttls()
            conn.login('tdesai.me@student.sfit.ac.in', 'Tanmay007')
            conn.sendmail('tdesai.me@student.sfit.ac.in','tdesai.me@gmail.com',"Subject: Online Exam \n\n Caught Looking Elsewhere more than 3 Times \n Copied")
            conn.quit()
            st.warning("You have crossed the number of limits. \n  Sending mail about malicious activities to the authorities.")
            FRAME_WINDOW.image("67-677733_removed-image-has-been-removed.png")
            st.stop()

        if(i < WARNING_FRAME_COUNT and FLAG == False):
            cv2.putText(frame,"Please Look at the Screen", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()
    #cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    #cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
        i = i+1
        FRAME_WINDOW.image(frame)
    else:
        st.write('Stopped')
    
    
    with open("BE-Comps_SEM8_BDA_MAY19.pdf","rb") as f:
      base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display =  F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="500" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

    upload_file()
    submit = st.button("Submit")
    if submit:
        #st.write(FLAG)
        send_mail()
    html(my_html)
