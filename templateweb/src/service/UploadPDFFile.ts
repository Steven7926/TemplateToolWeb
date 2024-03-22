import { StatusResponse } from "../common/interfaces";

// Takes an uploaded pdf file and sends it to the server to handle uploading
// the students drawing into the database in the proper format
export async function UploadPDFFile(uploadedFile: File): Promise<StatusResponse> {
    const formData = new FormData();
    formData.append('file_upload', uploadedFile);
    try {
        const response = await fetch('http://localhost:8000/upload_student_pdfs/', {
            method: 'POST',
            headers: {
            "Access-Control-Allow-Origin": "*"
            },
            body: formData
        });
        if (!response.ok) 
            throw new Error('Network response was not ok');
        const data = await response.json();
        if (data)
            return {success: true};
        else
            return {success: false};
    }
    catch (error) {
        console.error('Error uploading student data:', error);
        return {success: false};
    }
}