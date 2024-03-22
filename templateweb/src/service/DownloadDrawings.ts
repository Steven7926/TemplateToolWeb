import { FileFetchResponse, Student } from "../common/interfaces";

// Takes an uploaded pdf file and sends it to the server to handle uploading
// the students drawing into the database in the proper format
export async function DownloadDrawings(selectedStudents: Student[]): Promise<FileFetchResponse> {
    let response = null;

    try{
        if (selectedStudents.length > 0){
            let ids = selectedStudents.map(dict => dict.uuid);
            response = await fetch('http://localhost:8000/downloadDrawings_list/', {
                method: 'POST',
                headers: {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json" 
                },
                body: JSON.stringify({students: ids})
            }) 
        }
        else {
            response = await fetch('http://localhost:8000/downloadDrawings_all/', {
                method: 'GET',
                headers: {
                    "Access-Control-Allow-Origin": "*"
                }
            });
        }
        const data = await response.blob();
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return {success: true, file: data};
    }
    catch (error) {
        console.error('Error generating student pdf data:', error);
        return {success: false, file: new Blob()};
    }
}