# TemplateTool

### Prerequisites: 
    1. This will be for a windows machine, let me know if you need Mac instructions.
    2. Make sure you have python3 installed: https://www.python.org/downloads/

#### This is a template tool that that does 3 things
    1. Allows for uploading an excel file (I used the format given in the provided xlsx) of students and display them in a table while also downloading a zip of generated pdf files
        -Ensure the excel has the following columns [ID, NAME, CLASS, TEACHER, @image, SCHOOL, LOCATION, YEAR]
    2. Allows for searching for students in the table and downloading individual generated pdfs and drawing files.
    3. Allows for uploading pdfs of finished drawings and crop them out and download them to an images folder. 


#### In order to start the app, you have to first have a database connection. As per request this will be handled locally:
    1. Install MongoDB community: https://www.mongodb.com/try/download/community-kubernetes-operator
    2. Install MongoDB Compass: https://www.mongodb.com/products/tools/compass
    3. In MongoDB compass connect to "mongodb://localhost:27017"
    4. Create a new database called "templateTool"
    5. Create a collection in that database called "students"

#### From there you need to cd into the the project:
    1. Open Command Prompt on windows.
    2. cd (change directory) to TemplateTool folder
        - So if you have the TempateTool folder on your desktop then run "cd Desktop/TemplateTool"
    3. Now run "pip3 install -r requirements.txt"
        - This will install all the necessary python libraries needed.
    4. Now run "cd src"
        - This is where the main.py file lives that kickes off the app.
    5. Run "python3 main.py" and a window should appear with the app.


Please feel free to ask me any questions.
