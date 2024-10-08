import {useEffect, useState, useRef} from 'react';
import { Fade } from "react-awesome-reveal";
import excel from './assets/excel.svg';
import pdf from './assets/pdf.svg';
import 'primereact/resources/themes/viva-dark/theme.css';
import 'primeicons/primeicons.css';
import './css/App.css';
import {GetAllStudents, GetResponse} from './service/GetAllStudents';
import {UploadExcelFile} from './service/UploadExcelFile';
import {UploadPDFFile} from './service/UploadPDFFile';
import {StatusResponse, Student} from './common/interfaces';
import Loading from './components/Loading';
import StudentsTable from './components/StudentsTable';

function App() {
  const [students, setStudents] = useState([] as Student[]);
  const [isLoading, setIsLoading] = useState({loading: false, uploading: false});
  const inputExcelFile = useRef<HTMLInputElement | null>(null); 
  const inputPDFFile = useRef<HTMLInputElement | null>(null);

  const [classFilters, setClassFilters] = useState(["None"])
  const [schoolFilters, setSchoolFilters] = useState(["None"])

  const fetchTableData = async (schoolFilter: string = "None", classFilter: string = "None") => {
    try {
        const response: GetResponse = await GetAllStudents();
        const students = response.students as Student[];

        if (schoolFilter == "None" && classFilter == "None"){
          setSchoolFilters([...new Set(students.map(student => student.school)), "None"])
          setClassFilters([...new Set(students.map(student => student.class)), "None"])
        }

        if (schoolFilter != "None"){
          setClassFilters([...new Set(students.filter(student => student.school == schoolFilter).map(student => student.class)), "None"])

          if (classFilter != "None")
            setStudents(students.filter(student => student.school == schoolFilter && student.class == classFilter))
          else
            setStudents(students.filter(student => student.school == schoolFilter))
        }
        else if (schoolFilter == "None" && classFilter != "None"){
          setSchoolFilters([...new Set(students.filter(student => student.class == classFilter).map(student => student.school)), "None"])
          setStudents(students.filter(student => student.class == classFilter))
        }
        else setStudents(students)

    } catch (error) {
        console.error('Error fetching data:', error);
    }
  };

  const uploadExcelFile = () => {
    inputExcelFile.current.click();
    inputExcelFile.current.onchange = async () => {
      const file = inputExcelFile.current.files[0];
      setIsLoading({loading: true, uploading: true});
      try {
        const response: StatusResponse = await UploadExcelFile(file);
        if (response.success) {
          fetchTableData();
        }
      } catch (error) {
        console.error('Error uploading student data:', error);
      }
      setIsLoading({loading: false, uploading: true});
    }
  };

  const uploadPDFFile = () => {
    inputPDFFile.current.click();
    inputPDFFile.current.onchange = async () => {
      const file = inputPDFFile.current.files[0];
      setIsLoading({loading: true, uploading: true});
      try {
        const response: StatusResponse = await UploadPDFFile(file);
        if (response.success) {
          fetchTableData();
        }
      } catch (error) {
        console.error('Error uploading student pdf data:', error);
      }
      setIsLoading({loading: false, uploading: true});
    }
  };

  useEffect(() => {
    fetchTableData();
  }, []);

  return (
    <div className="App flex flex-col items-center justify-center bg-main text-white">
      {isLoading.loading && 
        <Loading isUploading = {isLoading.uploading}/>
      }
      <Fade duration={800} direction="down" triggerOnce = {true} fraction={0} damping={0.5}>
        <header className="font-bold">
          Template Tool
        </header>
      </Fade>
      <div className='flex flex-col items-center justify-center my-4'>
        <Fade duration={800} delay={250} direction="down" triggerOnce = {true} fraction={0} damping={0.5}>
          <div className='flex flex-row items-center'>
              <button onClick = {uploadExcelFile} className='p-2 border-0 rounded-lg text-sm bg-button shadow-xl flex flex-row justify-center items-center'>
                <input type='file' id='excel_file' ref={inputExcelFile} accept=".XLS,.XLSX,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel" className='hidden'/>
                <span className='font-bold'>Upload Excel File</span>
                <img src={excel}  alt="excel icon"/>
              </button>
              <button onClick = {uploadPDFFile} className='p-2 border-0 rounded-lg text-sm bg-button shadow-xl m-2 flex flex-row justify-center items-center'>
                <input type='file' id='pdf_file' ref={inputPDFFile} accept=".pdf" className='hidden'/>
                <span className='font-bold'>Upload PDF File </span>
                <img src={pdf} alt="pdf icon"/>
              </button>
          </div>
        </Fade>
      </div>
      <div className='flex flex-col items-center justify-center'>
        <Fade duration={800} delay={500} direction="down" triggerOnce = {true} fraction={0} damping={0.5}>
          <StudentsTable 
            students={students} 
            setStudents={setStudents} 
            fetchTableData={fetchTableData} 
            setIsLoading={setIsLoading} 
            schools={schoolFilters} 
            classes={classFilters}
          />
        </Fade>
      </div>
    </div>
  );
}

export default App;
