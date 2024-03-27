import { StatusResponse } from "../common/interfaces";

interface NewStudentInfo {
    student_id: string;
    field: string;
    value: string;
}

export async function EditStudentInfo(edited: NewStudentInfo): Promise<StatusResponse> {
    try {
        const response = await fetch(process.env.REACT_APP_API_PATH + '/student_update/', {
          method: 'POST',
          headers: {
            "Access-Control-Allow-Origin": "*", 
            "Content-Type": "application/json"
          },
          body: JSON.stringify(edited)
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        if (data.ok === 1)
            return {success: true};
        else
            return {success: false};
    } catch (error) {
        console.error('Error editing student data:', error);
    }
}