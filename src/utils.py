from tkinter import filedialog
from objects.excel_file  import ExcelFile
import os
import zipfile
from pathlib import Path
from PyPDF2 import PdfMerger
import shutil

# A small utils file with functions that help in zipping up files and cleaning up directories made in the process.

def create_pdf_for_student() -> ExcelFile:
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    excel_file = ExcelFile(file_path)
    excel_file.upload_to_monogo()
    return excel_file

def work_on_pdfs():
    merge_pdfs()
    zip_files('./pdfs', "../Templates.zip")

def zip_files(path, zipName):
    downloads_path = str(Path.home() / "Downloads")
    zf = zipfile.ZipFile(zipName,  'w')
    for dirname, subdirs, files in os.walk(path):
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()
    shutil.rmtree(path)

def merge_pdfs():
    pdfs = [f for f in os.listdir('./pdfs') if os.path.isfile(os.path.join('./pdfs',f)) and '.pdf' in f]
    merger = PdfMerger()
    for pdf in pdfs:
        merger.append('./pdfs/' +pdf)
    merger.write("./pdfs/All_PDFs.pdf")
    merger.close()

def check_path_exists(parent, school_name,  class_name):
    if not os.path.exists(parent):
        os.mkdir(parent)
                
    if not os.path.exists(parent + school_name + "/"):
        os.mkdir(parent + school_name + "/")
    
    if not os.path.exists(parent + school_name + "/" + class_name + "/"):
            os.mkdir(parent + school_name + "/" + class_name + "/")
    
    return parent + school_name + "/" + class_name + "/"
