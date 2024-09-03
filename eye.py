
import streamlit as st
import cv2
import dlib
import numpy as np
import imutils
from imutils import face_utils

MAXIMUM_FRAME_COUNT = 180
FACIAL_LANDMARK_PREDICTOR = "shape_predictor_68_face_landmarks.dat" 
EYE_COUNTER = 0
def eye_on_mask(mask, side, shape):
    
    points = [shape[i] for i in side]
    points = np.array(points, dtype=np.int32)
    mask = cv2.fillConvexPoly(mask, points, 255)
    l = points[0][0]
    t = (points[1][1]+points[2][1])//2
    r = points[3][0]
    b = (points[4][1]+points[5][1])//2
    return mask, [l, t, r, b]

def find_eyeball_position(end_points, cx, cy):
    """Find and return the eyeball positions, i.e. left or right or top or normal"""
    x_ratio = (end_points[0] - cx)/(cx - end_points[2])
    y_ratio = (cy - end_points[1])/(end_points[3] - cy)
    if x_ratio > 3:
        return 1
    elif x_ratio < 0.33:
        return 2
    elif y_ratio < 0.33:
        return 3
    else:
        return 0

    
def contouring(thresh, mid, img, end_points, right=False):
   
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(cnts, key = cv2.contourArea)
        M = cv2.moments(cnt)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        if right:
            cx += mid
        cv2.circle(img, (cx, cy), 4, (0, 0, 255), 2)
        pos = find_eyeball_position(end_points, cx, cy)
        return pos
    except:
        pass
    
def process_thresh(thresh):
    
    thresh = cv2.erode(thresh, None, iterations=2) 
    thresh = cv2.dilate(thresh, None, iterations=4) 
    thresh = cv2.medianBlur(thresh, 3) 
    thresh = cv2.bitwise_not(thresh)
    return thresh


def get_eye_pos(img, left, right):
    global EYE_COUNTER
   
    text = ''
    if left == right and left != 0:
        text = ''
        
        #EYE_COUNTER = 0

        if left == 1:
            print('Looking left')
            text = 'Looking left'
            
            EYE_COUNTER = EYE_COUNTER + 1

        elif left == 2:
            print('Looking right')
            text = 'Looking right'
            
            EYE_COUNTER = EYE_COUNTER + 1
            
        elif left == 3:
            print('Looking up')
            text = 'Looking up'
            
            EYE_COUNTER = EYE_COUNTER + 1
        
        font = cv2.FONT_HERSHEY_SIMPLEX 
        cv2.putText(img, text, (30, 30), font,  
                   1, (0, 255, 255), 2, cv2.LINE_AA)
        #if(EYE_COUNTER >= MAXIMUM_FRAME_COUNT):
        #cv2.putText(img,str(eyeCounter), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    return text
        


faceDetector = dlib.get_frontal_face_detector()     # dlib's HOG based face detector
landmarkFinder = dlib.shape_predictor(FACIAL_LANDMARK_PREDICTOR)  # dlib's landmark finder/predcitor inside detected face
left = [36, 37, 38, 39, 40, 41]
right = [42, 43, 44, 45, 46, 47]

cap = cv2.VideoCapture(0)
ret, img = cap.read()
thresh = img.copy()

cv2.namedWindow('image')
kernel = np.ones((9, 9), np.uint8)

def nothing(x):
    pass
cv2.createTrackbar('threshold', 'image', 75, 255, nothing)

st.title("""Student Attention Detection""")
run = st.checkbox('Run')
FRAME_WINDOW = st.image([])        
webcam = cv2.VideoCapture(0)
while run:
    # read frame from webcam 
    status, img = webcam.read()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceDetector(grayImage, 0)

    for face in faces:
        faceLandmarks = landmarkFinder(grayImage, face)
        faceLandmarks = face_utils.shape_to_np(faceLandmarks)
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        mask, end_points_left = eye_on_mask(mask, left, faceLandmarks)
        mask, end_points_right = eye_on_mask(mask, right, faceLandmarks)
        mask = cv2.dilate(mask, kernel, 5)
        
        eyes = cv2.bitwise_and(img, img, mask=mask)
        mask = (eyes == [0, 0, 0]).all(axis=2)
        eyes[mask] = [255, 255, 255]
        mid = int((faceLandmarks[42][0] + faceLandmarks[39][0]) // 2)
        eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
        threshold = cv2.getTrackbarPos('threshold', 'image')
        _, thresh = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY)
        thresh = process_thresh(thresh)
        
        eyeball_pos_left = contouring(thresh[:, 0:mid], mid, img, end_points_left)
        eyeball_pos_right = contouring(thresh[:, mid:], mid, img, end_points_right, True)
        result = get_eye_pos(img, eyeball_pos_left, eyeball_pos_right)
        if(EYE_COUNTER>= MAXIMUM_FRAME_COUNT):
            cv2.putText(img,"Please Look at the Screen", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            EYE_COUNTER = 0
        cv2.imshow("thresh",thresh)  
           
        # for (x, y) in shape[36:48]:
        #     cv2.circle(img, (x, y), 2, (255, 0, 0), -1)
      
    FRAME_WINDOW.image(img)
else:
    st.write('Stopped')