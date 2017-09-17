import cv2
import numpy as np


def gradient_polar(img):
    '''Get gradient angle and magnitude'''

    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=15)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=15)
    return cv2.cartToPolar(gx, gy, angleInDegrees=True)


def preprocess_frame(frame):
    '''Resize image and convert to float'''
    resize_factor = 0.5
    height, width = frame.shape[:2]
    new_size = (int(resize_factor * width), int(resize_factor * height))

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, new_size)
    return np.float32(img) / 255.0


def calibrate_initial(video_capturer):
    '''Do a moving average of magnitude and angle'''
    num_images = 10

    ret, frame = video_capturer.read()
    img = preprocess_frame(frame)
    avg_mag, avg_angle = gradient_polar(img)

    for i in range(num_images):
        ret, frame = video_capturer.read()
        img = preprocess_frame(frame)
        mag, angle = gradient_polar(img)

        avg_mag = 0.9 * avg_mag + 0.1 * mag
        avg_angle = 0.9 * avg_angle + 0.1 * angle
    return avg_mag, avg_angle


def main():

    cap = cv2.VideoCapture(0)
    init_mag, init_angle = calibrate_initial(cap)

    while True:
        ret, frame = cap.read()

        img = preprocess_frame(frame)
        mag, angle = gradient_polar(img)

        view = np.abs(mag * angle - init_mag * init_angle)
        view = view / np.max(view)
        cv2.imshow('frame', view)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()