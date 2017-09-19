import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage, linalg
from skimage.measure import compare_ssim


def preprocess_frame(frame):
    '''Resize image and convert to float'''
    resize_factor = 0.5
    height, width = frame.shape[:2]
    new_size = (int(resize_factor * width), int(resize_factor * height))

    #img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(frame, new_size)
    img = cv2.GaussianBlur(img, (5, 5), sigmaX=2, sigmaY=2)
    img = np.float32(img) / 255.0
    return img


def color_diff(img1, img2, ord=None):
    '''Pixel wise difference between two images using ord as norm (default: 2-norm)'''
    return linalg.norm(img1 - img2, ord, 2)


def calibrate_initial(video_capturer):
    '''Do a moving average of magnitude and angle'''
    num_images = 10

    ret, frame = video_capturer.read()
    avg_img = preprocess_frame(frame)

    for i in range(num_images):
        ret, frame = video_capturer.read()
        img = preprocess_frame(frame)
        avg_img = 0.9 * avg_img + 0.1 * img
    return avg_img


def main():

    cap = cv2.VideoCapture(0)
    init_img = calibrate_initial(cap)
    print(init_img.shape, init_img.dtype)
    plt.imshow(cv2.cvtColor(init_img, cv2.COLOR_BGR2RGB))
    plt.show()

    while True:
        ret, frame = cap.read()

        img = preprocess_frame(frame)

        # view = np.abs(mag * angle - init_mag * init_angle)
        # view = view / np.max(view)
        (score, diff) = compare_ssim(img, init_img, full=True, multichannel=True)
        diff = 1 - diff
        center = ndimage.measurements.center_of_mass(diff)
        center = (int(center[1]), int(center[0]))
        view = (diff * 255).astype("uint8")

        cv2.circle(view, center, 2, (0, 0, 255), 3)
        cv2.imshow('view', view)

        diff = color_diff(img, init_img)
        diff = diff
        center = ndimage.measurements.center_of_mass(diff)
        center = (int(center[1]), int(center[0]))
        view = (diff * 255).astype("uint8")

        cv2.circle(view, center, 2, (0, 0, 255), 3)
        cv2.imshow('view2', view)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
