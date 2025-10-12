import cv2
import numpy as np
import matplotlib.pyplot as plt
import copy
import os

def show_side_by_side(original, edited, title="Comparison"):
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Original")
    axes[1].imshow(cv2.cvtColor(edited, cv2.COLOR_BGR2RGB))
    axes[1].set_title("Edited")
    for ax in axes:
        ax.axis('off')
    plt.suptitle(title)
    plt.show()

def adjust_brightness(img, value):
    if value > 0:
        result = cv2.add(img, np.ones(img.shape,dtype="uint8")*value)
    elif value < 0:
        result = cv2.subtract(img, np.ones(img.shape,dtype="uint8")*abs(value))
    else:
        return result
    return result, f"brightness {value:+d}"

def adjust_contrast(img, value):
    alpha = 1 + (value / 100.0)
    result = cv2.multiply(img, np.ones(img.shape, dtype="uint8"),scale=alpha)
    return result, f"contrast {value:+d}"


def convert_grayscale(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray, "converted to grayscale"

def add_padding(img, pad_size, border_type, aspect_choice):
    if border_type == 'constant':
        border = cv2.BORDER_CONSTANT
    elif border_type == 'reflect':
        border = cv2.BORDER_REFLECT
    elif border_type == 'replicate':
        border = cv2.BORDER_REPLICATE
    else:
        border = cv2.BORDER_DEFAULT

    h, w = img.shape[:2]

    if aspect_choice.lower() == "square":
        target_ratio = 1
    elif aspect_choice.lower() == "rectangle":
        target_ratio = 16/9
    elif ':' in aspect_choice:
        a, b = map(int, aspect_choice.split(':'))
        target_ratio = a / b
    else:
        target_ratio = w / h 

    current_ratio = w / h
    new_img = img.copy()
    if current_ratio < target_ratio:
        new_w = int(h * target_ratio)
        diff = new_w - w
        left = diff // 2
        right = diff - left
        new_img = cv2.copyMakeBorder(new_img, 0, 0, left, right, border)
    elif current_ratio > target_ratio:
        new_h = int(w / target_ratio)
        diff = new_h - h
        top = diff // 2
        bottom = diff - top
        new_img = cv2.copyMakeBorder(new_img, top, bottom, 0, 0, border)

    new_img = cv2.copyMakeBorder(new_img, pad_size, pad_size, pad_size, pad_size, border)

    return new_img, f"padded {pad_size}px ({border_type}, ratio {aspect_choice})"

def apply_threshold(img, mode):
    if len(img.shape) == 3 and img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()
    
    ttype = cv2.THRESH_BINARY if mode == 'binary' else cv2.THRESH_BINARY_INV
    
    _, thresh = cv2.threshold(gray, 128, 255, ttype)
    
    thresh_bgr = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    return thresh_bgr, f"threshold ({mode})"

def blend_images(img1, img2_path, alpha):
    img2 = cv2.imread(img2_path)
    if img2 is None:
        print("Error: second image not found.")
        return img1, "blend failed"
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    blended = cv2.addWeighted(img1, alpha, img2, 1 - alpha, 0)
    return blended, f"blended with {os.path.basename(img2_path)} (α={alpha:.2f})"



def photo_editor():
    path = input("Enter path to image: ").strip()
    img = cv2.imread(path)
    while img is None:
        print("Error: Image not found.")
        path = input("Enter path to image: ").strip()
        img = cv2.imread(path)

    history_stack = [copy.deepcopy(img)]
    action_log = []

    while True:
        print("""
==== Mini Photo Editor ====
1. Adjust Brightness
2. Adjust Contrast
3. Convert to Grayscale
4. Add Padding (choose border type)
5. Apply Thresholding (binary or inverse)
6. Blend with Another Image (manual alpha)
7. Undo Last Operation
8. View History of Operations
9. Save and Exit
""")
        choice = input("Select option: ").strip()

        if choice == '1':
            val = int(input("Brightness change (-100 to +100): "))
            edited, log = adjust_brightness(img, val)
        elif choice == '2':
            val = int(input("Contrast change (-100 to +100): "))
            edited, log = adjust_contrast(img, val)
        elif choice == '3':
            edited, log = convert_grayscale(img)
        elif choice == '4':
            pad = int(input("Padding size (px): "))
            border = input("Border type (constant/reflect/replicate): ")
            ratio = input("Aspect ratio (Square/Rectangle/Custom e.g. 4:5): ")
            edited, log = add_padding(img, pad, border, ratio)
        elif choice == '5':
            mode = input("Type (binary/inverse): ").lower()
            edited, log = apply_threshold(img, mode)
        elif choice == '6':
            path2 = input("Path of second image: ")
            alpha = float(input("Alpha (0-1): "))
            edited, log = blend_images(img, path2, alpha)
        elif choice == '7':
            if len(history_stack) > 1:
                history_stack.pop()
                img = copy.deepcopy(history_stack[-1])
                print("Undone last operation.")
                continue
            else:
                print("No previous state.")
                continue
        elif choice == '8':
            print("=== History of Operations ===")
            for act in action_log:
                print("-", act)
            continue
        elif choice == '9':
            print("Final operations history:")
            for act in action_log:
                print("-", act)
            save = input("Save final image? (y/n): ").lower()
            if save == 'y':
                name = input("Enter filename (e.g. output.jpg): ")
                cv2.imwrite(name, img)
                print(f"Saved as {name}")
            break
        else:
            print("Invalid choice.")
            continue

        show_side_by_side(img, edited, log)
        img = edited
        history_stack.append(copy.deepcopy(img))
        action_log.append(log)

# ---------- Run ----------
if __name__ == "__main__":
    photo_editor()
