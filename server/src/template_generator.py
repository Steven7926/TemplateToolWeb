from fpdf import FPDF
import qrcode
import os
from os import listdir, remove, open
from os.path import isfile, join
from student import Student

# This file is entirely responsible for any pdf template building.
# We can pass it a student and it will build a pdf for that student based off the the "student" passed
# The student is a student object that contains things about the student. This makes it easy to address any peice of student
# information that may be needed to build the template.

class Template:
    def __init__(self, student: Student, use_presets: bool):
        self.pdf = (FPDF(orientation = 'P', unit = 'mm', format = 'A4'))
        self.student = student
        self.use_presets = use_presets
        self.title = 'Draw your picture inside the lines'
        self.caption = 'Any drawing outside will be lost on the card'
        self.warning_message =  '*Any damage to the alignment marks or QR code will render this template void\nand we cannot be held responsible for any issues this may cause*'
    
    def _set_attributes(self):
        self.pdf.add_page()
        self.pdf.set_auto_page_break(False)
        font = os.path.abspath('../../usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        self.pdf.add_font('DejaVuSans','', font, uni=True)
        self.pdf.set_font('DejaVuSans', '', 10)
        self.pdf.set_text_color(0, 0, 0)
    
    def _generate_qr_code(self):
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=40,
            border=4,
        )
        qr.add_data(self.student.uuid)
        qr.make(fit=True)
        qrimage = qr.make_image(fill_colour="black", back_colour="white")
        student_name_list = self.student.split_name() +  "_qr_code.png"
        qrimage.save(student_name_list, 'PNG')
        return qrimage, student_name_list
    
    def _generate_header_and_box(self, template=None):
        self.pdf.set_font('DejaVuSans', '', 15)
        self.pdf.set_xy(5, 0)
        self.pdf.multi_cell(0, 10, "Id: " + str(self.student.id), 0, 0, 'C')

        self.pdf.set_font('DejaVuSans', '', 25)
        self.pdf.set_xy(21, 8)
        self.pdf.multi_cell(0, 10, self.title, 0, 0, 'C')

        self.pdf.set_xy(25, 24)
        self.pdf.set_line_width(4)
        self.pdf.cell(160, 170, "", 1, 1, 'C')

        if template != None:
            self.pdf.image('./assets/templates/' + template, 35, 35, 140, 140, type="png")

        self.pdf.set_font('DejaVuSans', '', 24)
        self.pdf.set_xy(20, 205)
        self.pdf.multi_cell(0, 10, self.caption, 0, 0, 'C')

    def _generate_footer(self):
        self.pdf.set_font('DejaVuSans', '', 10)
        self.pdf.set_xy(2, -10)
        self.pdf.multi_cell(150, 3, self.warning_message, 0, 0, 'L')

        _, qr_png = self._generate_qr_code()
        self.pdf.image(qr_png, 165, 265, 30, 30, type="png")
        remove(qr_png)
    
    def _generate_student_details(self):
        self.pdf.set_xy(15, 230)
        self.pdf.set_font('DejaVuSans', '', 18)
        self.pdf.cell(0, 6, 'Name:', 0, 0, 'L')

        self.pdf.set_xy(35, 230)
        self.pdf.multi_cell(80, 6, self.student.name, 0, 0, 'L')

        self.pdf.set_xy(120, 230)
        self.pdf.set_font('DejaVuSans', '', 18)
        self.pdf.cell(0, 6, 'Class:', 0, 0, 'L')

        self.pdf.set_xy(139, 230)
        self.pdf.multi_cell(60, 6, self.student.student_class, 0, 0, 'L')

        self.pdf.set_xy(15, 250)
        self.pdf.set_font('DejaVuSans', '', 18)
        self.pdf.cell(0, 6, 'Teacher:', 0, 0, 'L')

        self.pdf.set_xy(42, 250)
        self.pdf.multi_cell(80, 6, self.student.teacher, 0, 0, 'L')

        self.pdf.set_xy(120, 250)
        self.pdf.set_font('DejaVuSans', '', 18)
        self.pdf.cell(0, 6, 'School:', 0, 0, 'L')

        self.pdf.set_xy(143, 250)
        self.pdf.multi_cell(60, 6, self.student.school, 0, 0, 'L')


    def generate_pdf(self, path):
        if self.use_presets:
          templates = [f for f in listdir('./assets/templates') if isfile(join('./assets/templates', f))]
          for file in templates:
            self._set_attributes()
            self._generate_header_and_box(file)
            self._generate_student_details()
            self._generate_footer()
          self.pdf.output(path + self.student.name+'.pdf')
        else:    
            self._set_attributes()
            self._generate_header_and_box()
            self._generate_student_details()
            self._generate_footer()
            self.pdf.output(path + self.student.name+'.pdf')
        return path + self.student.name+'.pdf'