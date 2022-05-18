import cv2
import numpy as np

def nothing(x):                                             
    pass

# INIZIALIZZAZIONE TRACKBAR #

kernel = np.ones((8 ,8), np.uint8)
cap = cv2.VideoCapture(0)        
cap.set(10, 100)
img = np.zeros((300,512,3), np.uint8)
img_2 = np.ones((300,512,3), np.uint8)
cv2.namedWindow("Trackbars") 
cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)                                                   
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)



# CREAZIONE WINDOW DELLA TRACKBARS #

while True:
    _, frame = cap.read()
    frameFlip = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frameFlip, cv2.COLOR_BGR2HSV)

    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")

    lower = np.array([l_h, l_s, l_v])
    upper = np.array([u_h, u_s, u_v])
    mask = cv2.inRange(hsv, lower, upper)

    mask = cv2.erode(mask, kernel, iterations=5)
    mask = cv2.dilate(mask, kernel, iterations=5)              

    result = cv2.bitwise_and(frameFlip, frameFlip, mask=mask)

    
    cv2.imshow("Trackbars", result) 

    if cv2.waitKey(1) == ord('s'):
        print(f"lower: {[l_h, l_s, l_v]}, upper: {[u_h, u_s, u_v]}\n")
