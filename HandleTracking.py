import cv2
import mediapipe as mp
import urllib.request
import numpy as np
import time

class handDetector():
    def __init__(self,mode=False,maxHands=2,detectionCon=0.5,trackCon=0.5):
        self.mode=mode
        self.maxHands=maxHands
        self.detectionCon=detectionCon
        self.trackCon=trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=True,
            max_num_hands=2,
            min_detection_confidence=0.5) # error aqui
        self.mpDraw = mp.solutions.drawing_utils  # dibujo de puntos


    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.result = self.hands.process(imgRGB)
        if self.result.multi_hand_landmarks:  # exists  hand on image
            for handLms in self.result.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)  #
        return img

    def findPosition(self,img ,handNo=0,draw=True):
        lmList=[]
        if self.result.multi_hand_landmarks:
            myHand = self.result.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id,lm) 
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append([id,cx,cy])
                if draw:
                    cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)
        return lmList


    def counting_fingers(self,lmList):
        if len(lmList) != 0:
            fingers=[]
            if lmList[4][2] < lmList[2][2]:  #Index finger
                fingers.append("pulgar")
            if lmList[8][2] < lmList[6][2]:       #Index finger
                fingers.append("indice")
            if lmList[12][2] < lmList[10][2]:     #Middle finger
                fingers.append("medio")
            if lmList[16][2] < lmList[14][2]:     #Ring finger
                fingers.append("anular")
            if lmList[20][2] < lmList[18][2]:     #Little finger
                fingers.append("meñique")
        else:
            fingers=[]
        response = ",".join(fingers)
        return response
