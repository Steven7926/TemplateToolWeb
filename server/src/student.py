
# The main student class, creates a student object that can be addressable elsewhere.

class Student: 
    def __init__(self, student):
        self.uuid = str(student["_id"]) if "_id" in student else student["uuid"]
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

    def split_name(self):
        if len(self.name.split(' ')) > 2:
            return self.name.split(' ')[0] + '_' + self.name.split(' ')[1] + '_' + self.name.split(' ')[2]
        elif len(self.name.split(' ')) > 1:
            return self.name.split(' ')[0] + '_' + self.name.split(' ')[1]
        else:
            return self.name.split(' ')[0]

    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "id": self.id,
            "name": self.name,
            "class": self.student_class,
            "teacher": self.teacher,
            "school": self.school,
            "location": self.location,
            "year": self.year,
            "image": self.image,
            "b64_image": self.b64_image,
            "use_preset": self.use_preset,
        }