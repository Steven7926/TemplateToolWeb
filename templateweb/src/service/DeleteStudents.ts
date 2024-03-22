import { StatusResponse } from "../common/interfaces";

export async function DeleteStudents(students: Array<{}>): Promise<StatusResponse> {

    try {
        const response =  students.length < 1 ?    
            await fetch('http://localhost:8000/students_delete_all/', {
                method: 'GET',
                headers: {
                "Access-Control-Allow-Origin": "*", 
                }
            })
            :
            await fetch('http://localhost:8000/students_delete/', {
            method: 'POST',
            headers: {
                "Access-Control-Allow-Origin": "*", 
                "Content-Type": "application/json"
            },
            body: JSON.stringify({students: students})
            });
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        if (data)
          return {success: true};
        else
          return {success: false}; 
      } catch (error) {
        console.error('Error deleting student data:', error);
        return {success: false};
      }
}