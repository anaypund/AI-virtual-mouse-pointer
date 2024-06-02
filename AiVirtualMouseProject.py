import cv2
import numpy as np

import HandTrackingModule as htm
import time
from time import sleep
import autopy, pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math
from playsound import playsound
import keyboard
import screen_brightness_control as sbcontrol



##########################
wCam, hCam = 640, 480
frameR = 100 # Frame Reduction
smoothening = 7
#########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (255, 0, 0)
flag = False
level = 0
condition_met = False
condition_met_tabs = False


wScr, hScr = autopy.screen.size()

while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)
    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, y1, x2, y2)

        # Filter based on size
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
    
    # 3. Check which fingers are up
    fingers = detector.fingersUp()
    # print(fingers)


    #Play / Pause Media:
    # if 250 < area < 1000 and fingers == [0, 1, 1, 1, 1]:
    #     length, img, lineInfo = detector.findDistance(8, 12, img)
    #     if length < 25:
    #         pyautogui.press("playpause")

    # print(fingers)
    cv2.rectangle(img, (frameR, frameR -50), (wCam - frameR, hCam - frameR - 70),
    (255, 0, 255), 2)
    try:
        # Only Index Finger : Moving Mode
        if fingers == [0, 1, 0, 0, 0] or fingers == [0, 1, 1, 0, 0] and (level == 0 or level == 1):
            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR - 50, hCam - frameR - 70), (0, hScr))
            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
        
            # 7. Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY
            
        # 8. Both Index and middle fingers are up : Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1 and (level == 0 or level == 1):
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            # print(length)
            # 10. Click mouse if distance short
            if length < 25:
                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                15, (0, 255, 0), cv2.FILLED)
                # autopy.mouse.click()
                pyautogui.click()
                time.sleep(0.1)
                

        #Index and middle finger partially closed : Dragging mode
        if fingers[1] == 1 and fingers[2] == 1 and (level == 0 or level == 1):
            lengthDrag, img, lineInfo = detector.findDistance(8, 6, img)
            lengthDrag2, img, lineInfo = detector.findDistance(10, 12, img)
            if lengthDrag < 25 and lengthDrag2 < 25 and flag == False:
                flag = True
                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                15, (0, 255, 0), cv2.FILLED)
                pyautogui.mouseDown(button = "left")
            elif flag == True and not (lengthDrag < 25 and lengthDrag2 < 25):
                pyautogui.mouseUp(button = "left")
                flag = False

        # All are up : Right click
        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0 and (level == 0 or level == 1):
            autopy.mouse.click(autopy.mouse.Button.RIGHT)

        #Thumb is up : scroll up
        if fingers == [1, 0, 0, 0, 0] and level == 0:
            pyautogui.scroll(-300)

        #Thumb and index is up : scroll down
        if fingers == [1, 1, 0, 0, 0] and level == 0:
            pyautogui.scroll(300)

        # Level switch : 0
        if 250 < area < 1000 and fingers == [1, 1, 0, 0, 1] and (level == 1 or level == 2):
            playsound('./sounds/level 1.mp3')
            level = 0

        # Level switch : 1
        if 250 < area < 1000 and fingers == [0, 1, 0, 0, 1] and (level == 0 or level == 2):
            playsound('./sounds/level 2.mp3')
            level = 1

        # Level switch : 2
        if 250 < area < 1000 and fingers == [1, 0, 0, 0, 1] and (level == 1 or level == 0):
            playsound('./sounds/level 3.mp3')
            level = 2
        ######################################################## LEVEL 0 ##################################################################
        
        # Volume Control
        if 250 < area < 1000 and fingers == [1, 1, 1, 1, 1] and level == 0:

            # Find Distance between index and Thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)
            # Find Distance between pinky and ring
            length2, img, lineInfo2 = detector.findDistance(14, 19, img)
            # print(length)
            fingers = detector.fingersUp()
            # Convert Volume
            volBar = np.interp(length, [50, 200], [400, 150])
            volPer = np.interp(length, [50, 200], [0, 100])

            # Reduce Resolution to make it smoother
            smoothness = 10
            volPer = smoothness * round(volPer / smoothness)


            # If pinky is touching ring set volume
            if length2 < 30:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                colorVol = (0, 255, 0)
            else:
                colorVol = (255, 0, 0)
            cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                        1, (255, 0, 0), 3)
            cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
            cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, colorVol, 3)

        # Brightness Control
        if 250 < area < 1000 and fingers == [1, 1, 1, 1, 0] and level == 0:
            lengthBright, img, lineInfo = detector.findDistance(4, 8, img)

            brightBar = np.interp(lengthBright, [50, 200], [400, 150])
            brightPer = np.interp(lengthBright, [50, 200], [0, 100])
            # Reduce Resolution to make it smoother
            smoothness = 10
            brightPer = smoothness * round(brightPer / smoothness)
            cv2.rectangle(img, (50, int(brightBar)), (85, 400), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, f'{int(brightPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                        1, (255, 0, 0), 3)

            if lengthBright < 20:
                lengthBright = 0
            elif lengthBright > 170:
                lengthBright = 200  
            # print(lengthBright)
            sbcontrol.set_brightness(lengthBright/2, display = 0)

        if fingers == [0, 0, 0, 0, 1] and level == 0:
            if not condition_met_tabs:  # Check if the condition has not been met previously
                condition_met_tabs = True
                pyautogui.hotkey('win', 'tab')
           
        if fingers == [0, 0, 0, 0, 0] and level == 0:
            condition_met_tabs = False

        ######################################################## LEVEL 1 ##################################################################
            
        # print(level)
        # Thumb, Index and Middle Up : Zoom In
        if 250 < area < 1000 and fingers == [1, 1, 1, 0, 0] and level == 1:
            print("Entered Zoom in")
            pyautogui.hotkey('ctrl', 'add')
            time.sleep(1)

        # Thumb, Index, Middle and ring Up : Zoom Out
        if 250 < area < 1000 and fingers == [1, 1, 1, 1, 0] and level == 1:
            print("Entered Zoom out")
            pyautogui.hotkey('ctrl', 'subtract')
            time.sleep(1)

        # Pinky up : Exit
        if fingers == [0, 0, 0, 0, 1] and level == 1:
            playsound('./sounds/Thank you.mp3')
            break
            time.sleep(0.1)
            playsound('./sounds/goodbye.mp3')

        ######################################################## LEVEL 2 ##################################################################

        # Index : Up arrow key
        if fingers == [1, 0, 1, 1, 1] and level == 2:
            print(fingers)
            if not condition_met:  # Check if the condition has not been met previously
                condition_met = True
                keyboard.press_and_release("up")
                

        # Thumb : Left key
        if fingers == [0, 1, 1, 1, 1] and level == 2:
            print(fingers)
            if not condition_met:  # Check if the condition has not been met previously
                condition_met = True
                keyboard.press_and_release("left")
                

        # Pinky : Right key
        if fingers == [1, 1, 0, 1, 1] and level == 2:
            print(fingers)
            if not condition_met:  # Check if the condition has not been met previously
                condition_met = True
                keyboard.press_and_release("right")
                

        # Palm : Down arrow key
        if fingers == [0, 0, 0, 0, 0] and level == 2:
            print(fingers)
            if not condition_met:  # Check if the condition has not been met previously
                condition_met = True
                keyboard.press_and_release("down")
                

        # Reset the condition flag if fingers change from [1, 1, 1, 1, 1]
        if fingers == [1, 1, 1, 1, 1]:
            condition_met = False


    except Exception as e:
        print("Failed to recognise hand")
        
    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
    (255, 0, 0), 3)
    cv2.putText(img, f'Level : {str(int(level)+1)}', (490, 450), cv2.FONT_HERSHEY_PLAIN, 2,
    (255, 0, 0), 3)
    # 12. Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)