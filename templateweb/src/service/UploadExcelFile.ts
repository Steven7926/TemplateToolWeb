import { StatusResponse } from "../common/interfaces";

// Takes an uploaded excel file and sends it to the server to handle uploading
// the students into the database in the proper format
export async function UploadExcelFile(uploadedFile: File): Promise<StatusResponse> {
    const formData = new FormData();
    formData.append('file_upload', uploadedFile);
    try {
        const response = await fetch(process.env.REACT_APP_API_PATH + '/students_upload_excel/', {
            method: 'POST',
            headers: {
            "Access-Control-Allow-Origin": "*"
            },
            body: formData
        });
        if (!response.ok) 
            throw new Error('Network response was not ok');
        const data = await response.json();
        console.log(data);
        if (data["status"] === "success")
            return {success: true};
        else
            return {success: false};
    }
    catch (error) {
        console.error('Error uploading student data:', error);
        return {success: false};
    }

    // An effort to chunk larger files and transmit them in smaller pieces, the server-side code is not yet implemented.
    // Could beused  inthe future if data gets too large 
    // const CHUNK_SIZE = 1024;
    // const totalChunks = Math.ceil(content["byteLength"] / CHUNK_SIZE);
    // for (let chunk = 0; chunk < totalChunks; chunk++) {
    //   let CHUNK = content.slice(chunk * CHUNK_SIZE, (chunk + 1) * CHUNK_SIZE)
    //   await fetch('http://localhost:8000/students_upload_excel/', {
    //     method: 'POST',
    //     headers: {
    //       "Access-Control-Allow-Origin": "*", 
    //       "Content-Type": "application/json"
    //     },
    //     body: CHUNK
    //   }).then(response => response.json())
    // }
}