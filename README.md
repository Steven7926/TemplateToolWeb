# Tool that takes the .xlsx and generates pdf templates as described per customer requirements. 
## This tool does a few things
1. Takes the example xlsx data as an upload and displays the data in a datatable
    - Data is selectable, deleteable, sortable and searchable, as well as paginated.
    - Can be exported to CSV or XLSX
2. Data is used to generate pdfs to use for drawing images
    - QR code attached to pdf that maps to document in Mongo
3. The pdfs are meant to be scanned and uploaded into the tool using the PDF uplaod button next to the Excel upload.
    - PDF is mapped to document in Mongo via the QR code so that the drawing can be cropped and uploaded to proper mongo doc
    - Images are displayed in table
4. Drawings can be exported and downloaded.

## To run:
### Everything is dockerized and theres no authentication (for now) as per requirements,
### So to run it you just need to install docker and run:
    - docker-compose build && docker compose up
#### from your favorite terminal. Then open localhost:3000 and upload the "Example Template Data.xlsx"

### Some future considerations if wanted
1. Authentication
    - Right now everything is no auth, but a SSO could be beneficial  along with DB secrets
    - If this is ever to be hosted it will need plenty of authentication
2. Speed
    - If we begin working with larger and larger datasets, then multiprocessing and threading needs to be investigated for generating pdfs and downloading drawings
3. Datatables
    - The frontend currently just grabs everything for display, this obviously is not ideal especially the larger the data gets
    - There needs to be some data pagination implemented so we can return the total amount of students as a count but the front end
    - only loads maybe 300 students max until the user navigates past that.
    - Its this way right now to simplify the generation and downloading process
4. Exports
    - The frontend exports are all client side and I have no idea how these may get bogged down with larger datasets
5. Large File uploads
    - If larger files are uploaded and uploading starts taking a while, chunking should be considered to mitigate issues.
6. Loading/Uploading Progress
    - Returning progress percentages as the upload or download process is happening would be cool.
7. Context providing
    - More of a nice to have but make things less prop drilly on the front end.