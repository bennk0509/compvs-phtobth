import cv2
import numpy as np
import time

def apply_invisible_cloak(frame, background):
    # convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define color range (green)
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([95, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)

    # clean mask
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

    # inverse + segment
    inverse_mask = cv2.bitwise_not(mask)
    cloak_area = cv2.bitwise_and(background, background, mask=mask)
    non_cloak = cv2.bitwise_and(frame, frame, mask=inverse_mask)

    # final merge
    final = cv2.addWeighted(cloak_area, 1, non_cloak, 1, 0)
    return final


cap = cv2.VideoCapture(0)


cv2.startWindowThread()
cv2.namedWindow("Cloak Effect", cv2.WINDOW_AUTOSIZE)

time.sleep(1)

print("Press 'b' to capture background, then 'q' to quit.")

while True:
    ret, background = cap.read()
    if not ret:
        continue
    cv2.imshow("Cloak Effect", background)
    if cv2.waitKey(1) & 0xFF == ord('b'):
        break

time.sleep(0.5)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    output = apply_invisible_cloak(frame, background)
    cv2.imshow("Cloak Effect", output)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
