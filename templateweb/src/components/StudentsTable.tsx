import { useState, useRef, useEffect, useMemo } from "react";
import { Student, StatusResponse, ImageModal, FileFetchResponse } from "../common/interfaces";
import {DeleteStudents} from '../service/DeleteStudents';
import {EditStudentInfo} from '../service/EditStudentInfo';
import {GeneratePDFs} from '../service/GeneratePDFs';
import {DownloadDrawings} from '../service/DownloadDrawings';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { ContextMenu } from 'primereact/contextmenu';
import Warning from "./Warning";
import StudentDrawing from "./StudentDrawing";
import { downloadFile } from "../common/utils";
import { Dropdown } from 'primereact/dropdown';
import Header from './Header'

interface TableProps {
    students: Array<any>;
    fetchTableData: Function;
    setIsLoading: Function;
}

export default function StudentsTable ({students, fetchTableData, setIsLoading}: TableProps) {

    const [globalFilterValue, setGlobalFilterValue] = useState('');
    const [filters, setFilters] = useState(null);
    const [selectedStudents, setSelectedSudents] = useState([] as Student[]);
    const [warningVisible, setWarningVisible] = useState(false);
    const [imageModal, setImageModal] = useState({show: false, b64: '', student_name: ''} as ImageModal);
    const dt = useRef(null);
    const cm = useRef(null);

    const columns = [
        { field: 'name', header: 'Name', sortable: true, editable: true},
        { field: 'b64_image', header: 'Drawing', sortable: false, editable: false },
        { field: 'uuid', header: 'Unique ID', sortable: false, editable: false },
        { field: 'class', header: 'Class', sortable: true, editable: true },
        { field: 'teacher', header: 'Teacher', sortable: true, editable: true },
        { field: 'school', header: 'School', sortable: true, editable: true },
        { field: 'location', header: 'Location', sortable: true, editable: true },
        { field: 'year', header: 'Year', sortable: true, editable: true },
        { field: 'image', header: 'Drawing Name', sortable: false, editable: true },
    ];

    const menuModel = [{ label: 'Delete Selected', icon: 'pi pi-fw pi-times', command: () => setWarningVisible(true)}];
    const globalFilterFields = ['name', 'class', 'teacher', 'school', 'location', 'year', 'image'];

    const delete_students = async () => {
        const response: StatusResponse = await DeleteStudents(selectedStudents.length> 0 ? selectedStudents :  [] );
        if (response.success) {
            fetchTableData();
            setSelectedSudents([]);
        }
    }

    const updateField = async (id, field, value) => {
        await EditStudentInfo({student_id: id, field: field, value: value});
    };

    const genereatePDFs = async ()  => {
        setIsLoading({loading: true, uploading: false});
        const response: FileFetchResponse = await GeneratePDFs(selectedStudents);
        const blob = new Blob([response.file], { type: 'application/zip' });
        downloadFile(blob);
        setIsLoading({loading: false, uploading: false});
    }

    const downloadDrawings = async () => {
        setIsLoading({loading: true, uploading: false});
        const response: FileFetchResponse = await DownloadDrawings(selectedStudents);
        const blob = new Blob([response.file], { type: 'application/zip' });
        downloadFile(blob);
        setIsLoading({loading: false, uploading: false});
    }
    
    const paginatorLeft = <Button type="button" icon="pi pi-refresh" onClick={() => fetchTableData()}/>;
    const paginatorRight = <Button type="button" icon="pi pi-trash" onClick={() => setWarningVisible(true)}/>;
    

    const drawingBodyTemplate = (rowData) => {
        const drawing = rowData.b64_image;
        const name = rowData.name;
        return (         
            <div className="flex align-items-center gap-2 items-center justify-center">
                <Button onClick={() => setImageModal({show:true, b64:drawing, student_name: name})}>
                    <img alt="student drawing" src={'data:image/png;base64,' + drawing} width="42"/>
                </Button>
            </div>
        );
    };

    const cellEditor = (options) => {
        return textEditor(options);
    };

    const textEditor = (options) => {
        return <InputText type="text" value={options.value} onChange={(e) => options.editorCallback(e.target.value)} className="w-3/4 text-center" />;
    };

    
    const onCellEditComplete = (e) => {
        let { rowData, newValue, field, originalEvent: event } = e;      
        newValue = field === 'year' ? newValue.toString() : newValue
        if (field === 'use_preset'){
            rowData[field] = newValue;
            updateField(rowData['uuid'], field, newValue);
        }
        else if (newValue.trim().length > 0){
            rowData[field] = newValue;
            updateField(rowData['uuid'], field, newValue);            
        }
        else 
            event.preventDefault();
    };
    
    const presetDropDown = (rowData) => {
        return (
            <Dropdown value={rowData.use_preset} 
                options={[{label: 'Yes', value: true}, {label: 'No', value: false}]} 
                placeholder="Use Preset"
                onChange={(e) => onCellEditComplete({rowData: rowData, newValue: e.value, field: 'use_preset', originalEvent: null})}
            />
        )
    }

    const head = (() =>         
        <Header setSelectedSudents = {setSelectedSudents} selectedStudents={selectedStudents} 
                downloadDrawings={downloadDrawings} genereatePDFs={genereatePDFs} 
                dtRef={dt} students={students} setFilters={setFilters} setGlobalFilterValue={setGlobalFilterValue} 
                filters={filters} globalFilterValue={globalFilterValue}
        />
    )

    const memoWarning = useMemo( () => 
        <Warning  
            warningVisible={warningVisible} 
            setWarningVisible={setWarningVisible} 
            delete_students={delete_students} 
            selectedStudents={selectedStudents}
        />
        ,[warningVisible, selectedStudents]
    )

    const memoDrawing = useMemo( () =>
        <StudentDrawing 
            imageModal={imageModal} 
            setImageModal={setImageModal}
        />
        ,[imageModal]
    )

    const addToSelection = (e) => {
        if (selectedStudents.length === 0)
            setSelectedSudents([...selectedStudents, e.data as Student]);
        cm.current.show(e.originalEvent)
    }
        

    return (
        <div className='mb-5'>
            <ContextMenu model={menuModel} ref={cm} />
            <DataTable value={students} tableStyle={{ minWidth: '50rem' }} paginator rows={5} rowsPerPageOptions={[5, 10, 20, 50]}
                        paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink RowsPerPageDropdown"
                        currentPageReportTemplate="{first} to {last} of {totalRecords}" paginatorLeft={paginatorLeft} paginatorRight={paginatorRight}
                        stripedRows sortField='name' sortOrder={-1} resizableColumns columnResizeMode='expand' removableSort
                        emptyMessage="No students found." dataKey="id" filters={filters} globalFilterFields={globalFilterFields} ref={dt} 
                        header={head} selectionMode='multiple' selection={selectedStudents} onSelectionChange={(e) => {setSelectedSudents(e.value)}}
                        onContextMenu={(e) => addToSelection(e)}
                        contextMenuSelection={selectedStudents} 
                        onContextMenuSelectionChange={(e) => setSelectedSudents(e.value)}
            >
                {columns.map((col, index) => {
                return <Column key={index} field={col.field !== 'b64_image' ? col.field : ""} body={col.field === 'b64_image' ? drawingBodyTemplate : null} header={col.header} sortable={col.sortable}
                                editor={col.editable ? (options) => cellEditor(options): null} onCellEditComplete={onCellEditComplete} 
                                className='text-center'/>;

                })}
                <Column key={columns.length} field={"use_preset"} header={"Use Preset"} sortable={false} 
                        editor = {false} body={presetDropDown} className='text-center'
                />
            </DataTable>
            {memoWarning}
            {memoDrawing}
        </div>
    )
}