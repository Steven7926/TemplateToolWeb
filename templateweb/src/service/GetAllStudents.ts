export interface GetResponse {
    students: Array<{}>;
}

export async function GetAllStudents(): Promise<GetResponse> {
    try {
        const response = await fetch('http://localhost:8000/all_students/', {
          headers: {
            "Access-Control-Allow-Origin": "*", 
            "Content-Type": "application/json"
          }
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}