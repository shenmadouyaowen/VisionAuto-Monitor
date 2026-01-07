import cv2
import os

def crop_icons():
    img_path = r'uploaded_image_1767314254080.png'
    img = cv2.imread(img_path)
    if img is None:
        print("Error: Could not read uploaded image.")
        return

    # 1. Crop "Continue" button (top one)
    # img[y1:y2, x1:x2]
    continue_btn = img[15:108, 15:475]
    cv2.imwrite('data/continue_btn.png', continue_btn)
    
    # 2. Crop "Error" status message
    error_msg = img[150:195, 30:350]
    cv2.imwrite('data/error_msg.png', error_msg)

    print("Icons cropped and saved to data/ directory.")

if __name__ == "__main__":
    crop_icons()
