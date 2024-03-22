
# The main student class, creates a student object that can be addressable elsewhere.

class Student: 
    def __init__(self, student):
        self.mongo_id = student["mongo_id"]
        self.id = student["id"]
        self.name = student["name"]
        self.student_class = student["class"]
        self.teacher = student["teacher"]
        self.school = student["school"]
        self.location = student["location"]
        self.year = student["year"]
        self.image = student["image"]
        self.b64_image = student["b64_image"]
        self.use_preset = student["use_preset"]

    def to_dict(self) -> dict:
        return {
            "id": int(self.id),
            "name": str(self.name),
            "class": str(self.student_class),
            "teacher": str(self.teacher),
            "school": str(self.school),
            "location": str(self.location),
            "year": str(self.year),
            "image": str(self.image),
            "b64_image": self.b64_image,
            "use_preset": str(self.use_preset),
        }
