import cv2
import numpy as np

#ITS NOT WORKING FOR ME IN THIS IDONT KNOW WHY SO I ALREADY CREATE A NEW TEST.PY TO TRY AGAIN AND ITS WORKS
def apply_invisible_cloak(frame, background):
    # convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    

    # define red color ranges and create masks
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([70, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)


    # cv2.morphologyEx() performs morphological transformations on binary images (mask images).
    # It’s a way to clean white regions (foreground) by eroding, dilating, or combining both.
    # These operations are extremely useful after you create a mask with cv2.inRange() — they remove small noise, fill small holes, and smooth edges.
    # cv2.morphologyEx(src, op, kernel[, dst[, anchor[, iterations[, borderType[, borderValue]]]]])
    #PARAMETERS:
        # src	        Input image (usually a binary mask)
        # op	        The morphological operation you want to perform
            # MORPH_OPEN        Tiny white dots (noise)	
            # MORPH_CLOSE       Small black holes inside white region	
            # MORPH_DILATE      Object edges look broken or jagged	
            # MORPH_ERODE       Object edges too fat / overlapping
            # MORPH_GRADIENT    Want to get only boundaries	
        # kernel	    Structuring element (e.g. np.ones((5,5), np.uint8)) defining neighborhood size
        # iterations	How many times to apply the operation (higher = stronger effect)

    # combine masks and refine if needed
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

    # create inverse mask and isolate cloak area
    inverse_mask = cv2.bitwise_not(mask)
    part1 = cv2.bitwise_and(background, background, mask=mask)
    part2 = cv2.bitwise_and(frame, frame, mask=inverse_mask)

    # combine background with current frame
    final_output = cv2.addWeighted(part1, 1, part2, 1, 0)

    return final_output


cap = cv2.VideoCapture(1)

# capture background (press 'b' to save it)
# or ignore this and use the first 2 seconds of the camera as background
while True:
    ret, background = cap.read()
    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite("background_output.jpg", background)
        print("Saved background_output.jpg")

    if cv2.waitKey(1) & 0xFF == ord('b'):
        break

while True:
    ret, frame = cap.read()
    output = apply_invisible_cloak(frame, background)
    cv2.imshow("Cloak Effect", output)

    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite("sample_output.jpg", output)
        print("Saved sample_output.jpg")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

