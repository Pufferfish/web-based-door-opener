import time
import cv2
import numpy as np
from scipy import ndimage, linalg


def preprocess_frame(frame):
    '''Resize image and blur'''
    resize_factor = 0.5
    height, width = frame.shape[:2]
    new_size = (int(resize_factor * width), int(resize_factor * height))

    img = cv2.resize(frame, new_size)
    img = cv2.GaussianBlur(img, (11, 11), sigmaX=2, sigmaY=2)
    return img


def color_diff(img1, img2, ord=None):
    '''Pixel wise difference between two images using ord as norm (default: 2-norm)'''
    return linalg.norm(img1 - img2, ord, 2)


def center_of_mass(image):
    '''Center of mass of image'''
    center = ndimage.measurements.center_of_mass(image.astype('float32'))
    return (int(center[1]), int(center[0]))


def main():
    '''Detect movement in video stream'''
    init_images = 10
    calibration_period = 10
    cap = cv2.VideoCapture(0)

    # Initial calibration of camera
    ret, frame = cap.read()
    avg_img = preprocess_frame(frame)
    for i in range(init_images):
        ret, frame = cap.read()
        img = preprocess_frame(frame)
        avg_img = 0.9 * avg_img + 0.1 * img
    last_calibration_time = time.time()

    while True:
        ret, frame = cap.read()

        img = preprocess_frame(frame)

        diff = color_diff(img, avg_img)
        diff = cv2.threshold(diff.astype('uint8'), 100,
                             255, cv2.THRESH_BINARY)[1]
        diff = cv2.dilate(diff, None, iterations=3)
        try:
            center = center_of_mass(diff)
        except ValueError:
            pass
        else:
            cv2.circle(img, center, 2, (0, 0, 255), 3)
        cv2.imshow('diff', diff)
        cv2.imshow('view', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if time.time() - last_calibration_time > calibration_period:
            last_calibration_time = time.time()
            avg_img = 0.9 * avg_img + 0.1 * img

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
