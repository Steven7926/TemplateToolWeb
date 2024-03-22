import pandas as pd
from objects.mongo import Mongo
import base64
import numpy as np

# This class handles conversion and uploading of an excel file to students in the database.
# It contains the function to convert excel rows to python dictionaries and upload those dictionaries to the database (mongoDB)
# It also has a function for redundancy in case a column doesn't exist. This prevents errors where it may be looking for a certain column
# to build a student but it isn't there.

class ExcelFile:
    def __init__(self, filePath) -> None:
        self.filePath = filePath
        self.fileFields = []
        self.students =  []
    
        
    def upload_to_monogo(self): 
        if (self.filePath):
            try:
                df = pd.read_excel(self.filePath)
                df = self.check_for_column(df)
                df = df.dropna(axis=0, how='all')
                df = df.replace(np.nan, '', regex=True)
                data = df.to_dict(orient="records")
                # ID and Name are required on the student object
                for student in data:
                    if student["ID"] == "":
                        continue
                    # Check if the student already exists in the DB using id and name, if they do we need to delete the student and add the new one, keeping previous uploaded image
                    result = Mongo().check_and_delete_by_fields(int(student["ID"]), str(student["NAME"]), str(student["CLASS"]))
                    if result:
                        student_temp = {
                            "id": int(student["ID"]),
                            "name": str(student["NAME"]),
                            "class": str(student["CLASS"]),
                            "teacher": str(student['TEACHER']),
                            "school":  str(student['SCHOOL']),
                            "location": str(student['LOCATION']),
                            "year": str(student['YEAR']),
                            "image": str(result["image"]),
                            "b64_image": result["b64_image"],
                            "use_preset": result["use_preset"]
                        }
                    else:
                        with open("./assets/default.png", "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read())
                        student_temp = {
                            "id": int(student["ID"]),
                            "name": str(student["NAME"]),
                            "class": str(student["CLASS"]),
                            "teacher": str(student['TEACHER']),
                            "school": str(student['SCHOOL']),
                            "location": str(student['LOCATION']),
                            "year": str(student['YEAR']),
                            "image": str(student["@image"]),
                            "b64_image": encoded_string,
                            "use_preset": student["PRESET"]
                        }              
                    self.students.append(student_temp)                  
                inserted = Mongo().insert_all_into_mongodb(self.students)
                Mongo().close_client()

            except Exception as e:
                print(e)

    def check_for_column(self, df):
        if "TEACHER" not in df:
            df["TEACHER"] = ""
        if "SCHOOL" not in df:
            df["SCHOOL"] = ""
        if "LOCATION" not in df:
            df["LOCATION"] = ""
        if "YEAR" not in df:
            df["YEAR"] = ""
        if "CLASS" not in df:
            df["CLASS"] = ""
        if "PRESET" not in df:
            df["PRESET"] =""
        return df
        