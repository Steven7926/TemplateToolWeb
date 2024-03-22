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
#### from your favorite terminal. Then upload the "Example Template Data.xlsx"