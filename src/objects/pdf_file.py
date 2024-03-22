import pypdfium2 as pdfium
from  objects.mongo import Mongo
import PIL.Image
import os
import cv2
import base64
from qreader import QReader
from utils import check_path_exists
from pypdf import PdfReader
import fitz
import io
import PIL.Image as Image
import numpy as np
from matplotlib import pyplot as plt

# This file is responsible for taking in the scanned pdf files and cropping out the image
# It works by converting the pdf to a png, then using Canny edge detection to find the thick black lines of the box. 
# Then it crops in a certain amount of pixels to remove everything except the image. 
# We then incorporated a QR reader that reads the qr off the page, finds the student in the databse, and updates their drawing.
# The drawings are stored using a base64 string that gets encoded and decoded on database transport 

class PDFFile:
    def __init__(self, filePath) -> None:
        self.filePath = filePath
        self.qrReader = QReader()

    def crop_image(self):
        pdf = pdfium.PdfDocument(self.filePath)
        for i in range(len(pdf)):
            bitmap = pdf[i].render(
                scale = 1,
                rotation = 0
            )
            pil_img  = bitmap.to_pil()
            processed_path = "./processed_images/out_" + str(i) +".png"
            pil_img.save(processed_path)

            # Load the image
            image = cv2.imread(processed_path)  # Replace 'your_image.jpg' with the path to your image


            cropped_image, binary_mask = self.find_longest_lines(image)
            cropped_again, binary_mask2 = self.find_longest_lines(cropped_image)

            self.find_longest_lines2(processed_path)


            # cv2.imshow('Cropped Image', binary_mask)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            # cv2.imshow('Cropped Image', binary_mask2)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()


            qr_id = self.read_qr_code(processed_path=processed_path)
            student = Mongo().find_student(qr_id) if qr_id != None else None
            
            if (student != None):
                print("Cropping " + student["name"] + ": " + str(student["_id"]))
                image_file_name = "ID " + str(student["id"]) + '(' + str(i + 1) +").png"
                updated = Mongo().update_image(qr_id, image_file_name)

                main_path = check_path_exists("./processed_images/", student["school"], student["class"])

                cv2.imwrite(main_path+ image_file_name, cropped_image)  

                with open (main_path + image_file_name, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read())
                    Mongo().update_raw_image(qr_id, encoded)
                Mongo().close_client()
                
            else:
                print("Cropping Unknown Image")
                image_file_name = "ID " + '(' + str(i + 1) +").png"

                if not os.path.exists("./processed_images/"):
                    os.mkdir("./processed_images/")

                cv2.imwrite('./processed_images/' + image_file_name, cropped_image)
                
            
    def read_qr_code(self, processed_path):
        qr_image = cv2.imread(processed_path)

        image = cv2.cvtColor(qr_image, cv2.COLOR_BGR2RGB)
        decoded_texts = self.qrReader.detect_and_decode(image=image)
        qr_final = ''
        for text in decoded_texts:
            qr_final = qr_final + str(text)
        return(qr_final)
       
    def find_longest_lines(self, image):
        
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Canny edge detection to find edges
        edges = cv2.Canny(gray, threshold1=30, threshold2=100)  # You can adjust the thresholds as needed

        # Find lines using Hough Line Transform
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

        # Create a binary mask of the same size as the image
        binary_mask = np.zeros_like(image)

        longest_line_length = 0
        longest_line = None

        horizontal_longest_line_length = 0
        horizontal_longest_line = None



        # Iterate through the detected lines
        for line in lines: 
            x1, y1, x2, y2 = line[0]

            if (x1 == x2):
                print(line[0])

            # Ensure the line is approximately vertical (adjust the angle threshold as needed)
            if abs(x2 - x1) < 10:
                # Draw the detected lines on the mask
                line_length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                if line_length > longest_line_length:
                    longest_line_length = line_length
                    longest_line = line[0]
            if abs(y2 - y1) < 10:
                # Draw the detected lines on the mask
                horiz_line_length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                if horiz_line_length > horizontal_longest_line_length:
                    horizontal_longest_line_length = horiz_line_length
                    horizontal_longest_line = line[0]

        x1, y1, x2, y2 = longest_line
        x1_2, y1_2, x2_2, y2_2 = horizontal_longest_line
        cv2.line(binary_mask, (x1, y1), (x2, y2), (255, 255, 255), 2)
        cv2.line(binary_mask, (x1_2, y1_2), (x2_2, y2_2), (255, 255, 255), 2)
        
        # print(horizontal_longest_line_length, longest_line_length)
        # print(x1, y1, x2, y2)
        # print(x1_2, y1_2, x2_2, y2_2)

        x = min(x1, x2, x1_2, x2_2)
        y = min(y1, y2, y1_2, y2_2)
        width = abs(x2_2 - x1_2)
        height = abs(y2-y1)

        # Convert the mask to grayscale
        binary_mask = cv2.cvtColor(binary_mask, cv2.COLOR_BGR2GRAY)

        # Apply a threshold to create a binary mask
        binary_threshold = 1  # Adjust this threshold as needed
        binary_mask = cv2.threshold(binary_mask, binary_threshold, 255, cv2.THRESH_BINARY)[1]

        # Invert the binary mask (optional)
        binary_mask = cv2.bitwise_not(binary_mask)

        

        #x1, y1, x2, y2 = longest_line
        #x, y, w, h = min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)
        #print(x1, y1, x2, y2)
        #print(x,y,w,h)
        cropped_image = image[y:y+height, x:x+width]
        return cropped_image, binary_mask

    def find_longest_lines2(self, image):

        img = cv2.imread(image,0)
        print (img.shape)
        h, w = img.shape[:2]

        # Drop top and bottom area of image with black parts.
        img= img[100:h-100, :]
        h, w = img.shape[:2]

        # Threshold image
        ret,th1 = cv2.threshold(img,50,255,cv2.THRESH_BINARY)

        # get rid of thinner lines
        kernel = np.ones((5,5),np.uint8)
        th1 = cv2.dilate(th1,kernel,iterations = 3)

        # Determine contour of all blobs found
        _, contours0, hierarchy = cv2.findContours( th1.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = [cv2.approxPolyDP(cnt, 3, True) for cnt in contours0]

        # Draw all contours
        vis = np.zeros((h, w, 3), np.uint8)
        cv2.drawContours( vis, contours, -1, (128,255,255), 3, cv2.LINE_AA)

        # Draw the contour with maximum perimeter (omitting the first contour which is outer boundary of image
        # Not necessary in this case
        vis2 = np.zeros((h, w, 3), np.uint8)
        perimeter=[]
        for cnt in contours[1:]:
            perimeter.append(cv2.arcLength(cnt,True))
        print (perimeter)
        print (max(perimeter))
        maxindex= perimeter.index(max(perimeter))
        print (maxindex)

        cv2.drawContours( vis2, contours, maxindex +1, (255,0,0), -1)


        # Show all images
        titles = ['Original Image','Threshold','Contours', 'Result']
        images=[img, th1, vis, vis2]
        for i in range(4):
            plt.subplot(2,2,i+1)
            plt.imshow(images[i],'gray')
            plt.title(titles[i]), plt.xticks([]), plt.yticks([])
        plt.show()