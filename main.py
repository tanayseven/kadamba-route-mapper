import re
from pathlib import Path
from typing import Generator

import cv2
import openpyxl
from PIL import Image
from numpy import ndarray
from pytesseract import pytesseract


def read_image(image_path: str) -> ndarray:
    return cv2.imread(image_path)


def greyscale(image: ndarray):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def black_and_white(image: ndarray) -> ndarray:
    thresh, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return image


def remove_horizontal_lines(image: ndarray) -> ndarray:
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    detected_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(image, [c], -1, (0, 0, 0), 2)
    return image


def remove_vertical_lines(image: ndarray) -> ndarray:
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
    detected_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(image, [c], -1, (0, 0, 0), 2)
    return image


def blur(image: ndarray) -> ndarray:
    return cv2.GaussianBlur(image, (5, 5), 0)


def mark_boxes_on_image(image: ndarray, boxes: str) -> ndarray:
    for box in boxes.splitlines():
        box = box.split(' ')
        x, y, w, h = int(box[1]), int(box[2]), int(box[3]), int(box[4])
        cv2.rectangle(image, (x, y), (w, h), (0, 255, 0), 2)
    return image


def write_image(image: ndarray, image_path: str):
    cv2.imwrite(image_path, image)


def detect_text(image: Image) -> str:
    return pytesseract.image_to_string(
        image, config='--oem 3  --psm 6'
    )


def has_numbers(string: str) -> bool:
    return any(char.isdigit() for char in string)


def parse_detected_text(detected_text: str) -> list[list[str]]:
    parsed_text = []
    count = 1
    for line in detected_text.splitlines():
        if line:
            text = re.split(r'[ {|_]', line)
            text = [word for word in text if word]
            if not has_numbers(text[0]):
                continue
            kms = ''.join([letter for letter in text[0] if letter.isdigit()])
            stage = text[1].strip()
            if stage.isnumeric():
                continue
            parsed_text.append([kms, stage, count])
            count += 1
    return parsed_text


def detected_text_to_xlsx(detected_text: list[list[str]], xlsx_file_path: str):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    for row in detected_text:
        sheet.append(row)
    workbook.save(xlsx_file_path)


def process_images(raw_images: Generator[Path, None, None], processed_image_dir: Path):
    for image_file in raw_images:
        img = read_image(str(image_file))
        img = greyscale(img)
        img = black_and_white(img)
        img = blur(img)
        # img = remove_horizontal_lines(img)
        img = remove_vertical_lines(img)
        boxes = pytesseract.image_to_boxes(img)
        # img = mark_boxes_on_image(img, boxes)
        write_image(img, str(processed_image_dir / image_file.name))


def transform_images_to_xlsx(processed_image_dir: Path):
    all_detected_text = [["Kms", "Stages", "Stage Number"]]
    processed_images = processed_image_dir.glob('*')
    for file in processed_images:
        image = Image.open(str(file))
        text_detected = detect_text(image)
        text_detected = parse_detected_text(text_detected)
        all_detected_text.extend(text_detected)

    detected_text_to_xlsx(all_detected_text, 'routes.xlsx')


if __name__ == '__main__':
    raw_images = (Path.cwd() / 'raw_images').glob('*')
    processed_image_dir = Path.cwd() / 'processed_images'
    if not processed_image_dir.exists():
        processed_image_dir.mkdir()
    process_images(raw_images, processed_image_dir)
    transform_images_to_xlsx(processed_image_dir)
