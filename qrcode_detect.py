import os
import argparse
import cv2
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol
from scipy import ndimage

from loggers import get_logger

SCALE_PERCENT = 50
BORDER = 50
LINE_COLOR = ((0, 0, 255), 2)

logger = get_logger('qrcode_extractor')


def get_rect(box, shape):
    ymin = max(box[:, 1].min(), 10) - 10
    ymax = min(box[:, 1].max(), shape[0] - 10) + 10
    xmin = max(box[:, 0].min(), 10) - 10
    xmax = min(box[:, 0].max(), shape[1] - 10) + 10
    return (ymin, ymax, xmin, xmax)


class QRCodeExtractor:
    qrDecoder = cv2.QRCodeDetector()

    @staticmethod
    def read_image_from_path(image_path):
        image = cv2.imread(image_path, cv2.COLOR_BGR2GRAY)
        if image is None:
            logger.error(f'File {image_path} is not image. Please check this file')
            return None
        return image

    @staticmethod
    def read_image_from_bytes(byte_str):
        nparr = np.fromstring(byte_str, np.uint8)
        return cv2.imdecode(nparr, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def save_image(path, image, name=None):
        filename = str(hex(hash(str(image))))[2:] + '.jpg' if name is None else f'{name}.jpg'
        path = os.path.join(path, filename)
        cv2.imwrite(path, image)
        logger.info(f"Save image to {path}")
        return path

    @classmethod
    def crop_qrcode(cls, image):
        pass

    @classmethod
    def draw_qrcode(cls, image):
        image = image.copy()
        barcodes = decode(image, symbols=[ZBarSymbol.QRCODE])

        list_barcodes = []
        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            list_barcodes.append(barcode_data)

            # extract the bounding box location of the barcode and draw the
            # bounding box surrounding the barcode on the image
            (x, y, w, h) = barcode.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), *LINE_COLOR)
            # the barcode data is a bytes object so if we want to draw it on
            # our output image we need to convert it to a string first

        if not list_barcodes:
            decodedText, points, _ = cls.qrDecoder.detectAndDecode(image)
            if points is not None:
                list_barcodes = [decodedText]
                x1, y1 = points[0].min(axis=0)
                x2, y2 = points[0].max(axis=0)
                cv2.rectangle(image, (x1, y1), (x2, y2), *LINE_COLOR)

        return list_barcodes, image

    @staticmethod
    def auto_canny(image, sigma=0.33):
        # compute the median of the single channel pixel intensities
        v = np.median(image)
        # apply automatic Canny edge detection using the computed median
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edged = cv2.Canny(image, lower, upper)
        # return the edged image
        return edged

    @classmethod
    def find_qrcode(cls, image):
        qr = decode(image, symbols=[ZBarSymbol.QRCODE])
        if qr:
            return [qr[0].data.decode("utf-8")], image
        img = image.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        gradX = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
        gradY = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)

        # subtract the y-gradient from the x-gradient
        gradient = cv2.subtract(gradX, gradY)
        gradient = cv2.convertScaleAbs(gradient)

        blurred = cv2.blur(gradient, (9, 9))
        for thresh in (85, 125, 175):
            (_, thresh) = cv2.threshold(blurred, thresh, 255, cv2.THRESH_BINARY)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
            closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            closed = cv2.erode(closed, None, iterations=4)
            closed = cv2.dilate(closed, None, iterations=4)

            (cnts, _) = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL,
                                         cv2.CHAIN_APPROX_SIMPLE)

            contours = sorted(cnts, key=cv2.contourArea, reverse=True)
            for contour in contours[:4]:
                rect = cv2.minAreaRect(contour)
                box = np.int0(cv2.boxPoints(rect))

                rect = get_rect(box, gray.shape)

                img_cropped = img[rect[0]:rect[1], rect[2]:rect[3]]

                qr = decode(img_cropped, symbols=[ZBarSymbol.QRCODE])

                if qr:
                    return [qr[0].data.decode("utf-8")], img_cropped
        return [], image


def get_parser():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-i", "--images_paths", type=str, nargs='+',
                            help="Paths to images that need extract QR code")
    arg_parser.add_argument("-d", "--images_dir", type=str, nargs=1,
                            help="Path to dir that content many images")
    arg_parser.add_argument("--debug", action='store_true',
                            help="Set debug mode")
    arg_parser.add_argument("--save_image", action='store_true',
                            help="Save image with finding QR code")

    return arg_parser


def main():
    arg_parser = get_parser()
    args = arg_parser.parse_args()

    if args.images_path is not None:
        for image_path in args.images_path:
            QRCodeExtractor.find_qrcode(image_path)

    # for qrcode_image in os.listdir(QRCODE_IMAGES_PATH):
    #     image = cv2.imread(qrcode_image)
    #
    #     resized_image = resize(image)
    #     find_qrcode(resized_image)


if __name__ == '__main__':
    main()
