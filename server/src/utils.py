# Desc: This file contains the utility functions that are used for generating and zipping up files and  cropping images.
import os
import cv2
import zipfile
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import shutil
import time

def check_path_exists(parent, school_name,  class_name):
    if not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
                
    if not os.path.exists(parent + school_name + "/"):
        os.makedirs(parent + school_name + "/", exist_ok=True)

    if not os.path.exists(parent + school_name + "/" + class_name + "/"):
            os.makedirs(parent + school_name + "/" + class_name + "/", exist_ok=True)
    
    return parent + school_name + "/" + class_name + "/"

def create_all_files_path(parent):
    if not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    if not os.path.exists(parent + "All Drawings/"):
        os.makedirs(parent + "All Drawings/", exist_ok=True)   
    return parent + "All Drawings/"

def zip_and_merge_pdfs(pdfs_for_merger: list):
    writer = PdfWriter()
    for pdf in pdfs_for_merger:
        reader = PdfReader(pdf)
        writer.append(reader)
    with open("./pdfs/All_PDFs.pdf", "wb") as output_pdf:
        writer.write(output_pdf)
    print(time.time())

    zip_files('./pdfs', "../Templates.zip")

def zip_files(path, zipName):
    zf = zipfile.ZipFile(zipName,  'w')
    for dirname, subdirs, files in os.walk(path):
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()
    shutil.rmtree(path)


# Crops for QR code
def find_contours_and_crop(image, name, inner_contours=False):
    # Convert to gray and apply GaussianBlur
    original = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9,9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    # Find contours and filter for QR code
    cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        x,y,w,h = cv2.boundingRect(approx)
        area = cv2.contourArea(c)
        ar = w / float(h)
        if len(approx) == 4 and area > 1000 and (ar > .85 and ar < 1.3):
            cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 3)
            if inner_contours:
                ROI = original[y+10:y+h-10, x+10:x+w-10]
            else:
                ROI = original[y:y+h, x:x+w]
            cv2.imwrite(name+'.png', ROI)

# Manually Crop Image
def manual_crop_image(image, name):
    cropped = image[80:548, 80:520]
    cv2.imwrite(name+'.png', cropped)
    