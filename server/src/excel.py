from mongo import Mongo
import base64
import numpy as np
import os

# This class handles conversion and uploading of an excel file to students in the database.
# It contains the function to convert excel rows to python dictionaries and upload those dictionaries to the database (mongoDB)
# It also has a function for redundancy in case a column doesn't exist. This prevents errors where it may be looking for a certain column
# to build a student but it isn't there.

class ExcelFile:
    def __init__(self) -> None:
        self.fileColumns = []
        self.students =  []
    
        
    def upload_to_monogo(self, df): 
        try:
            # Check for columns that may not exist in the excel file so we can
            # add them to stabndardize the data
            df.columns = [x.lower() for x in df.columns]
            df = self.check_for_column(df)
            df = df.dropna(axis=0, how='all')
            df = df.replace(np.nan, '', regex=True)
            data = df.to_dict(orient="records")
            # ID and Name are required on the student object
            for student in data:
                if student["id"] == "" or student["name"] == "":
                    continue
                # Check if the student already exists in the DB using year, class, and name.
                # If they do we need to delete the student and add the new one, keeping previous uploaded image
                result = Mongo().check_and_delete_by_fields(student["year"], student["name"], student["class"])
                if result:
                    student_temp = {
                        "id": student["id"],
                        "name": student["name"],
                        "class": student["class"],
                        "teacher": student['teacher'],
                        "school":  student['school'],
                        "location": student['location'],
                        "year": student['year'],
                        "image": result["image"],
                        "b64_image": result["b64_image"],
                        "use_preset": result["use_preset"]
                    }
                else:
                    # Use the default white as the drawing for now
                    encoded_string = ""
                    if os.path.exists("./src/assets/default.png"):
                        with open("./src/assets/default.png", "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read())
                    student_temp = {
                        "id": student["id"],
                        "name": student["name"],
                        "class": student["class"],
                        "teacher": student['teacher'],
                        "school": student['school'],
                        "location": student['location'],
                        "year": student['year'],
                        "image": student["@image"] if "@image" in student else student["image"],
                        "b64_image": encoded_string,
                        "use_preset": student["preset"] if "preset" in student else student["use_preset"]
                    }              
                self.students.append(student_temp)                  
            inserted = Mongo().insert_all_into_mongodb(self.students)
            Mongo().close_client()
            return {inserted["success"]}
        except Exception as e:
            print(e)

    def check_for_column(self, df):
        if "id" not in df:
            df["id"] = ""
        if "name" not in df:
            df["name"] = ""
        if "class" not in df:
            df["class"] = ""
        if "teacher" not in df:
            df["teacher"] = ""
        if "school" not in df:
            df["school"] = ""
        if "location" not in df:
            df["location"] = ""
        if "year" not in df:
            df["year"] = ""
        if "image" not in df:
            df["image"] = ""
        if "preset" not in df:
            df["use_preset"] =""
        return df
        