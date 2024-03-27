from fastapi import FastAPI, File, UploadFile
from mongo import Mongo
from excel import ExcelFile
from student import Student
from template_generator import Template
from utils import check_path_exists, zip_and_merge_pdfs, create_all_files_path, zip_files, find_contours_and_crop
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pypdfium2 as pdfium
import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import base64
import  os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()
API_PATH_STRING = os.getenv('API_PATH_STRING')
origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://" + API_PATH_STRING + ":3000",
    "https://" + API_PATH_STRING + ":3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/all_students/", response_description="Get all students for datatable display")
def read_all_students() -> dict:
    mongoInstance = Mongo()
    students = mongoInstance.return_all_with_uuid()
    res = []
    for student in students:
        uuid =  str(student.pop('_id'))
        res.append({"uuid": uuid, **student})
    mongoInstance.close_client()
    return {"students": res}

@app.post("/student_update/", response_description="Update a field value for a student")
def update_student_one_field(body: dict) -> dict:
    mongoInstance = Mongo()
    res = mongoInstance.update_student_one_field(body['student_id'], body["field"], body["value"])
    mongoInstance.close_client()
    return res

@app.post("/students_upload_excel/", response_description="Upload an excel file of student data")
async def upload_students(file_upload: UploadFile = File(...)) -> dict:
    contents = await file_upload.read()
    status = ExcelFile().upload_to_monogo(contents)
    return status

@app.post("/students_delete/", response_description="Delete a single or list of students that were selected for deletion")
def delete_selected_students(body: dict) -> dict:
    mongoInstance = Mongo()

    # Check if students keys value is list, if not just delete the single student
    if not isinstance(body["students"], list):
        res = mongoInstance.check_and_delete(body["students"]['uuid'])
        mongoInstance.close_client()
        if res["name"] is not None:
            return {"status": "success"}
        else:
            return {"status": "failed"}
    else:
        res_names  = []
        for student in body["students"]:
            res = mongoInstance.check_and_delete(student["uuid"])
            res_names.append(res["name"])
        mongoInstance.close_client()
        if len(res_names) == len(body["students"]):
            return {"status": "success"}
        else:
            return {"status": "failed"}

@app.get("/students_delete_all/", response_description="Delete All Students in the DB")
def delete_all_students() -> dict:
    mongoInstance = Mongo()
    res = mongoInstance.delete_all()
    mongoInstance.close_client()
    if res["success"]:
        return {"status": "success"}
    else:
        return {"status": "failed"}
    
@app.get("/generatePDFs_all/", response_description="Generate PDFs for all students")
def generatePDFs_for_all_students() -> FileResponse:
    mongoInstance = Mongo()
    students = mongoInstance.return_all_with_uuid()
    pdfs_for_merger = []
    for student in students:
        student = Student(student)
        template = Template(student)
        main_path = check_path_exists("./pdfs/", student.school, student.student_class)
        pdf = template.generate_pdf(main_path)
        pdfs_for_merger.append(pdf)
    mongoInstance.close_client()
    zip_and_merge_pdfs(pdfs_for_merger)

    response = FileResponse("../Templates.zip", filename="Templates.zip")

    return response

@app.post("/generatePDFs_list/", response_description="Generate PDFs for a list of students")
def generatePDFs_for_student_list(body: dict) -> FileResponse:
    mongoInstance = Mongo()
    pdfs_for_merger = []
    for uuid in body["students"]:
        student = mongoInstance.find_student(uuid)
        student = Student(student)
        template = Template(student, student.use_preset)
        main_path = check_path_exists("./pdfs/", student.school, student.student_class)
        pdf = template.generate_pdf(main_path)
        pdfs_for_merger.append(pdf)
    mongoInstance.close_client()
    zip_and_merge_pdfs(pdfs_for_merger)

    response = FileResponse("../Templates.zip", filename="Templates.zip")

    return response

@app.post("/upload_student_pdfs/", response_description="Upload student pdf files and update the students drawing")
async def upload_student_pdfs(file_upload: UploadFile = File(...)) -> dict:
    contents = await file_upload.read()
    try:
        with open("./"+file_upload.filename, "wb") as f:
            f.write(contents)
        pdf = pdfium.PdfDocument("./"+file_upload.filename)

        for i in range(len(pdf)):
            bitmap = pdf[i].render(
                scale = 1,
                rotation = 0
            )
            pil_img  = bitmap.to_pil()
            processed_path = "./out_" + str(i) +".png"
            pil_img.save(processed_path)

            # Load the image
            image = cv2.imread(processed_path)
            original = image.copy()
            find_contours_and_crop(image, "drawing", True)

            # Cut image in half
            w, h = image.shape[1], image.shape[0]
            image_cropped = original[int(h/2):int(h), int(w/2):int(w)]
            cv2.imwrite("./image.png", image_cropped)
            find_contours_and_crop(image_cropped, "qr_code")

            data = decode(Image.open("qr_code.png"))

            mongoInstance = Mongo()
            with open("drawing.png", "rb") as f:
                encoded = base64.b64encode(f.read())
                result = mongoInstance.update_raw_image(data[0].data.decode('utf-8'), encoded)
            os.remove("drawing.png") if os.path.exists("drawing.png") else None
            os.remove("qr_code.png") if os.path.exists("qr_code.png") else None
            os.remove("out_" + str(i) + ".png") if os.path.exists("out_" + str(i) + ".png") else None
            os.remove("image.png") if os.path.exists("image.png") else None
            mongoInstance.close_client()
        os.remove("./"+file_upload.filename) if os.path.exists("./"+file_upload.filename) else None
        return {"status": "success"}
    except Exception as e:
        print(e)
        return {"status": "failed"}
    finally:
        os.remove("drawing.png") if os.path.exists("drawing.png") else None
        os.remove("qr_code.png") if os.path.exists("qr_code.png") else None
        os.remove("out_" + str(i) + ".png") if os.path.exists("out_" + str(i) + ".png") else None
        os.remove("image.png") if os.path.exists("image.png") else None
        os.remove("./"+file_upload.filename) if os.path.exists("./"+file_upload.filename) else None

# Downloading all drawings
@app.get("/downloadDrawings_all/", response_description="Download all drawings for all students")
def downloadDrawings_all() -> FileResponse:
    mongoInstance = Mongo()
    students = mongoInstance.return_all_with_uuid()
    res = [Student(student) for student in students]
    mongoInstance.close_client()

    for student in res:
        image_name = student.split_name() + '_drawing.png' 
        main_path = check_path_exists("./processed_images/", student.school, student.student_class)
        all_files_path =  create_all_files_path("./processed_images/")
        decoded = base64.b64decode(student.b64_image)

        with open(all_files_path + image_name, "wb") as f:
            f.write(decoded)
        with open(main_path + image_name, "wb") as f:
            f.write(decoded)
    zip_files('./processed_images', "../Drawings.zip")

    response = FileResponse("../Drawings.zip", filename="Drawings.zip")
    return response

# Downloading a list of students drawings
@app.post("/downloadDrawings_list/", response_description="Download all drawings for students listed")
def downloadDrawings_list(body: dict) -> FileResponse:
    mongoInstance = Mongo()
    res = [Student(mongoInstance.find_student(uuid)) for uuid in body["students"]]
    mongoInstance.close_client()

    for student in res:
        image_name = student.split_name() + '_drawing.png' 
        main_path = check_path_exists("./processed_images/", student.school, student.student_class)
        all_files_path =  create_all_files_path("./processed_images/")
        decoded = base64.b64decode(student.b64_image)

        with open(all_files_path + image_name, "wb") as f:
            f.write(decoded)
        with open(main_path + image_name, "wb") as f:
            f.write(decoded)
    zip_files('./processed_images', "../Drawings.zip")

    response = FileResponse("../Drawings.zip", filename="Drawings.zip")
    return response