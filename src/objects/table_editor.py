from tkinter import *
from tkinter.ttk import *
from objects.mongo import Mongo
from objects.student  import Student
from objects.template import Template
from utils import create_pdf_for_student,  zip_files, work_on_pdfs, merge_pdfs, check_path_exists
from PIL import Image, ImageTk
import io, os
import base64
import pandas as pd
import threading

from tkinter import filedialog
from objects.pdf_file import PDFFile

# This is the main UI, most things kick off from.
# This class has functions for adding UI elements but also includes functions that kick off other processes
# like making templates and cropping images as well as searching and pulling back students from the database based on the table row info.


class TableEditor:
    def __init__(self, root) -> None:
        self.root = root
        self.image_list = []
    
    def buildUI(self):
        self.configureStyle()
        self.addButtons()
        self.buildTable()

    def configureStyle(self):
        style = Style()
        style.configure('TButton', font='calibri 10 bold', background='#192428')
        style.configure('Treeview', font='calibri 12', background='#829ab1', rowheight=60)
        style.configure('Treeview.Heading', font='calibri 12 bold', background='#829ab1')
        style.configure('Button.TFrame', font='calibri 10', background='#192428')
    
    def addButtons(self):
        button_frame = Frame(self.root, style='Button.TFrame')
        button_frame.pack(pady=20)

        upload_excel = Button(button_frame, text="Upload Excel File", command=self.return_uploaded_students, cursor='hand2')
        upload_excel.grid(row=0, column=0, sticky=W, padx=10, pady=10)

        upload_pdf = Button(button_frame, text="Upload PDF File", command=self.crop_image_update, cursor='hand2')
        upload_pdf.grid(row=0, column=1, sticky=W, padx=10, pady=10)

        dump_to_csv = Button(button_frame, text="Database to CSV", command=self.dump_db_csv, cursor='hand2')
        dump_to_csv.grid(row=0, column=2, sticky=W, padx=10, pady=10)


        self.search_entry = Entry(button_frame)
        self.search_entry.grid(row=0, column=3, sticky=E, padx=0, pady=10)
        search_button = Button(button_frame, text="Search", command=self.filter_table)
        search_button.grid(row=0, column=4, sticky=E, padx=0, pady=10)

    def buildTable(self):
        frame = Frame(self.root, name="studentTable")
        frame.pack(fill='both', expand=True)
        results = Mongo().return_certain_count_no_id(400)
        res = list(results)
        Mongo().close_client()
        if len(res) != 0:

            keys = list(res[0].keys())
            keys.pop()
            keys.pop()
            self.tree = Treeview(frame, columns=keys, show='headings')
            self.tree.tag_configure("font_tag", font=("Helvetica", 24))

            self.tree.heading('#0', text="IMAGE")
            for column in keys:
                if column == "image":
                    self.tree.heading(column, text="IMAGE NAME")
                elif column == "_id":
                    self.tree.heading(column, text="UNIQUE ID")
                else:
                    self.tree.heading(column, text=column.upper())
                if column == "location":
                    self.tree.column(column, width=150)
                elif column == "id":
                    self.tree.column(column, width=50)
                else:
                    self.tree.column(column, width=50)

            self.tree.bind("<Double-1>", self.edit_item)
            self.tree.bind("<Button-3>", self.display_menu)
            self.tree["show"] = ("headings", "tree")

            for row in res:
                b64_image = row["b64_image"]
                image = Image.open((io.BytesIO(base64.b64decode(b64_image))))
                width, height = image.size
                width_new=int(width/8)
                height_new=int(height/8)
                img_resized=image.resize((width_new, height_new))
                final_drawing = ImageTk.PhotoImage(img_resized)
                self.image_list.append(final_drawing)
                row["b64_image"] = final_drawing

                values = list(row.values())
                self.tree.insert("", "end", image=final_drawing, values=values)

            scrollbar = Scrollbar(frame, orient="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="both")

            self.tree.pack(fill='both', expand=True)
        else:
            headings  =  ["image", "unique id" "id", "name", "class", "teacher", "school", "location",  "year", 'image name']
            self.tree = Treeview(frame, columns=headings, show='headings')
            self.tree.tag_configure("font_tag", font=("Helvetica", 24))
            for column in headings:
                self.tree.heading(column, text=column.upper())
                self.tree.column(column, width=100)
            self.tree.pack(fill='both', expand=True)
    
    def return_uploaded_students(self):
        excel_file = create_pdf_for_student()
        returned_excel = excel_file
        self.buildTable()
        make_pdfs(excel_file=returned_excel)
        

    def crop_image_update(self):
        t = threading.Thread(target = self.crop_image)
        t.daemon = True
        t.start()

    def crop_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        pdf_file = PDFFile(file_path)
        if not os.path.exists("./processed_images"):
            os.mkdir("./processed_images")
        pdf_file.crop_image()
        self.buildTable()
        print("Done")
        zip_files('./processed_images', "../Drawings.zip")

    
    def filter_table(self):
        search_text = self.search_entry.get().lower()
        filtered_data = Mongo().return_any_like(search_text=search_text)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in filtered_data:
            b64_image = row["b64_image"]
          
            image = Image.open((io.BytesIO(base64.b64decode(b64_image))))
            width, height = image.size
            width_new=int(width/8)
            height_new=int(height/8)
            img_resized=image.resize((width_new, height_new))
            final_drawing = ImageTk.PhotoImage(img_resized)
            self.image_list.append(final_drawing)
            row["b64_image"] = final_drawing

            values = list(row.values())
            self.tree.insert("", "end", image=final_drawing, values=values)

    def edit_item(self, event):
        if self.tree.selection():
            item = self.tree.selection()[0]
            column = self.tree.identify_column(event.x)
            column = int(column.split("#")[-1])  # Extract column number

            # Check if the column is not column 1 (the "id" column) before allowing editing
            if column != 0 and column != 1 and column != 2 and column != 9:
                # Create an entry widget for editing
                edit_window = Toplevel(self.root)
                edit_window.iconbitmap("./assets/icon.ico")
                edit_window.title("Edit Item")

                old_value = self.tree.item(item, "values")[column - 1]
                edit_entry = Entry(edit_window, justify="center")
                edit_entry.insert(0, old_value)
                edit_entry.pack(pady=10)

                save_button = Button(
                    edit_window, text="Save", command=lambda: self.save_item(item, column, edit_entry)
                )
                save_button.pack()

    def save_item(self, item, column, edit_entry):
        new_value = edit_entry.get()
        values = self.tree.item(item, "values")
        values = list(values)
        values[column - 1] = new_value
        self.tree.item(item, values=values)

        Mongo().update_student(values=values, column_updated=column, columns=list(self.tree["columns"]))
        Mongo().close_client()
        edit_entry.master.destroy()

    def display_menu(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            menu = Menu(self.root, tearoff=0)
            menu.add_command(label="Download Image", command=self.download_drawing)
            menu.add_command(label="Download PDF Blank Template", command=self.download_pdf_template_blank)
            menu.add_command(label="Download PDF Preset Template", command=self.download_pdf_template_preset)
            menu.add_command(label="", activebackground="SystemButtonFace", activeforeground="black")
            menu.add_command(label="", activebackground="SystemButtonFace", activeforeground="black")
            menu.add_command(label="", activebackground="SystemButtonFace", activeforeground="black")
            menu.add_command(label="Delete Student", command=self.delete_student)
            menu.post(event.x_root, event.y_root)

    def delete_student(self):
        student_temp = self.get_student()
        if len(student_temp) > 0:
            for student in student_temp:
                Mongo().check_and_delete(student_id=student.mongo_id)
                Mongo().close_client()
            self.filter_table()
       
        
    def download_pdf_template_blank(self):
        student_temp = self.get_student()
        
        if len(student_temp) > 0:
            for student in student_temp:
                pdfTemplate = Template(student=student, isBlank=True)
                main_path = check_path_exists("./pdfs/", student.school, student.student_class)        
                pdfTemplate.generate_pdf(path=main_path)

            merge_pdfs()
            if len(student_temp) > 1:
                zip_files('./pdfs', "../" + str(len(student_temp)) + " Templates.zip")
            else:
                zip_files('./pdfs', "../" + student_temp[0].name + " Template.zip")
    
    def download_pdf_template_preset(self):
        student_temp = self.get_student()
        if not os.path.exists("./pdfs"):
            os.mkdir("./pdfs")
        
        if len(student_temp) > 0:
            for student in student_temp:
                pdfTemplate = Template(student=student, isBlank=False)
                main_path = check_path_exists("./pdfs/", student.school, student.student_class)   
                pdfTemplate.generate_pdf(path=main_path)
            merge_pdfs()
            if len(student_temp) > 1:
                zip_files('./pdfs', "../" + str(len(student_temp)) + " Templates.zip")
            else:
                zip_files('./pdfs', "../" + student_temp[0].name + " Template.zip")
    
    def download_drawing(self):
        student_temp = self.get_student()
        
        if len(student_temp) > 0:
            for student in student_temp:
                drawing = student.b64_image
                drawing_image = Image.open(io.BytesIO(base64.b64decode(drawing)))
                main_path = check_path_exists("./processed_images/", student.school, student.student_class)
                drawing_image.save(main_path + student.name + ".png")
            if len(student_temp) > 1:                           
                zip_files('./processed_images', "../" + str(len(student_temp)) + " Drawings.zip")
            else:
                zip_files('./processed_images', "../" + student_temp[0].name + " Drawing.zip")
            

    def get_student(self):
        selected_item = self.tree.selection()
        if selected_item:
            asList = list(selected_item)
            students = []
            for selected in asList:
                item = self.tree.item((selected))
                values = item["values"]
                student = Mongo().find_student(student_id=values[0])
                student_temp = self.convert_student(student)
                Mongo().close_client()
                students.append(student_temp)
            return students
        return None
    
    def dump_db_csv(self):
        all_students = Mongo().return_all()
        students = []
        for student in all_students:
            student.popitem()
            students.append(student)
        df = pd.DataFrame(students)
        df.to_csv('All_Students.csv')

    def convert_student(self, student):
        return Student({
            "mongo_id": student["_id"],
            "id": student["id"],
            "name": student["name"],
            "class": student["class"],
            "teacher": student["teacher"],
            "school": student["school"],
            "location": student["location"],
            "year": student["year"],
            "image": student["image"],
            "b64_image": student["b64_image"],
            "use_preset": student["use_preset"]
        })

def make_pdfs(excel_file):
    students = excel_file.students
    chunks = [students[x:x+100] for x in range(0, len(students), 100)]
    t = threading.Thread(target = build_pdfs, args=(students,))
    t.daemon = True
    t.start()

def build_pdfs(students):
    for student in students:
        print("Building template for " + student["name"])
        student_temp = convert_to_student(student)
        isBlank = True
        if student["use_preset"] !="":
            isBlank = False
        pdfTemplate = Template(student=student_temp, isBlank=isBlank)
        main_path = check_path_exists("./pdfs/", student_temp.school, student_temp.student_class)   
        pdfTemplate.generate_pdf(main_path)  
    work_on_pdfs()
    print("Done")  

def convert_to_student(student):
    return Student({
        "mongo_id": student["_id"],
        "id": student["id"],
        "name": student["name"],
        "class": student["class"],
        "teacher": student["teacher"],
        "school": student["school"],
        "location": student["location"],
        "year": student["year"],
        "image": student["image"],
        "b64_image": student["b64_image"],
        "use_preset": student["use_preset"]
    })