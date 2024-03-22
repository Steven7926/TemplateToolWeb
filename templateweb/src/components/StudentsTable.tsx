import { useState, useRef, useEffect } from "react";
import { Student, StatusResponse, ImageModal, FileFetchResponse } from "../common/interfaces";
import {DeleteStudents} from '../service/DeleteStudents';
import {EditStudentInfo} from '../service/EditStudentInfo';
import {GeneratePDFs} from '../service/GeneratePDFs';
import {DownloadDrawings} from '../service/DownloadDrawings';
import { FilterMatchMode, FilterOperator } from 'primereact/api';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { ContextMenu } from 'primereact/contextmenu';
import Warning from "./Warning";
import StudentDrawing from "./StudentDrawing";
import { downloadFile } from "../common/utils";

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
        { field: 'image', header: 'Drawing Name', sortable: false, editable: true }
    ];

    const menuModel = [{ label: 'Delete Selected', icon: 'pi pi-fw pi-times', command: () => delete_students(false) }];
    const globalFilterFields = ['name', 'class', 'teacher', 'school', 'location', 'year', 'image'];

    const delete_students = async (delete_all: boolean) => {
        const response: StatusResponse = await DeleteStudents(delete_all ? [] :selectedStudents);
        if (response.success) {
        fetchTableData();
        setSelectedSudents([]);
        }
    }

    const updateField = async (id, field, value) => {
        const response: StatusResponse = await EditStudentInfo({student_id: id, field: field, value: value});
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

    const exportCSV = (selectionOnly) => {
        dt.current.exportCSV({ selectionOnly });
    };
    
    const paginatorLeft = <Button type="button" icon="pi pi-refresh" onClick={() => fetchTableData()}/>;
    const paginatorRight = <Button type="button" icon="pi pi-trash" onClick={() => setWarningVisible(true)}/>;
    
    const clearFilter = () => {
        initFilters();
        setSelectedSudents([]);
    };

    const onGlobalFilterChange = (e) => {
        const value = e.target.value;
        let _filters = { ...filters };

        _filters['global'].value = value;

        setFilters(_filters);
        setGlobalFilterValue(value);
    };
    
    const initFilters = () => {
        setFilters({
            global: { value: null, matchMode: FilterMatchMode.CONTAINS },
            name: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }] },
            class: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }] },
            teacher: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }] },
            school: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }] }
        });
        setGlobalFilterValue('');
    };
    
    const exportExcel = () => {
        import('xlsx').then((xlsx) => {
            const export_all = selectedStudents.length > 1 ? false : true;
            
            // Removing b64 image for now from export because it leads to a character overflow in excel
            let studentCopy = export_all ? students.map((student) => {return { ...student, b64_image: '' }}): 
                                            selectedStudents.map((student) => {return { ...student, b64_image: '' }});

            const worksheet = xlsx.utils.json_to_sheet(studentCopy);
            const workbook = { Sheets: { data: worksheet }, SheetNames: ['data'] };
            const excelBuffer = xlsx.write(workbook, {
                bookType: 'xlsx',
                type: 'array'
            });

            saveAsExcelFile(excelBuffer, 'students');
        });
    };
    
    const saveAsExcelFile = (buffer, fileName) => {
        import('file-saver').then((module) => {
            if (module && module.default) {
                let EXCEL_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8';
                let EXCEL_EXTENSION = '.xlsx';
                const data = new Blob([buffer], {
                    type: EXCEL_TYPE
                });

                module.default.saveAs(data, fileName + '_export_' + new Date().getTime() + EXCEL_EXTENSION);
            }
        });
    };

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
        return <InputText type="text" value={options.value} onChange={(e) => options.editorCallback(e.target.value)} />;
    };

    
    const onCellEditComplete = (e) => {
        let { rowData, newValue, field, originalEvent: event } = e;      
        newValue = field === 'year' ? newValue.toString() : newValue
        if (newValue.trim().length > 0){
            rowData[field] = newValue;
            updateField(rowData['uuid'], field, newValue);            
        }
        else 
            event.preventDefault();
    };

    const renderHeader = () => {
        return (
            <div className="flex flex-row">
                <div className='flex justify-start items-start w-1/3'>
                  <Button type="button" label="Clear" icon="pi pi-filter-slash" outlined onClick={clearFilter} className='m-2'/>
                  <span className="p-input-icon-left flex flex-row">
                      <i className="pi pi-search ml-40"/>
                      <InputText value={globalFilterValue} onChange={onGlobalFilterChange} placeholder="Search" className='p-2'/>
                  </span>
                </div>
                <div className='flex flex-row justify-center items-center w-1/3'>
                  <Button type="button" icon="pi pi-file" onClick={() => downloadDrawings()} data-pr-tooltip="CSV" 
                          className='m-2 pl-2 border-solid bg-button text-white'
                  >
                    <span className='m-1 pl-1 pr-1'>Download Drawing(s)</span>
                  </Button>
                  <Button type="button" icon="pi pi-file-pdf" data-pr-tooltip="CSV" 
                          className='m-2 pl-2 border-solid bg-button text-white' onClick={() => genereatePDFs()}
                  >
                    <span className='m-1 pl-1 pr-1'>Generate PDF(s)</span>
                  </Button>
                </div>
                <div className='flex flex-row justify-end items-end w-1/3'>
                  <Button type="button" icon="pi pi-file" aria-label='export csv' onClick={() => exportCSV(selectedStudents.length  > 0 ? true : false)} data-pr-tooltip="CSV" 
                          className='m-2 pl-2 border-solid bg-button text-white'
                  >
                    <span className='m-1 pl-1 pr-1'>CSV</span>
                  </Button>
                  <Button type="button" icon="pi pi-file-excel" aria-label='export excel' onClick={exportExcel} data-pr-tooltip="CSV" 
                          className='m-2 pl-2 border-solid bg-button text-white'
                  >
                    <span className='m-1 pl-1 pr-1'>Excel</span>
                  </Button>
                </div>
            </div>
        );
    };
    const header = renderHeader();
    
    useEffect(() => {
        initFilters();
    }, []);  

    return (
        <div className='rounded-lg mb-5'>
            <ContextMenu model={menuModel} ref={cm} onHide={() => setSelectedSudents([])} />
            <DataTable value={students} tableStyle={{ minWidth: '90rem' }} paginator rows={5} rowsPerPageOptions={[5, 10, 20, 50]}
                        paginatorTemplate="FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink RowsPerPageDropdown"
                        currentPageReportTemplate="{first} to {last} of {totalRecords}" paginatorLeft={paginatorLeft} paginatorRight={paginatorRight}
                        stripedRows sortField='name' sortOrder={-1} resizableColumns columnResizeMode='expand' removableSort
                        emptyMessage="No students found." dataKey="id" filters={filters} globalFilterFields={globalFilterFields} 
                        header={header} selectionMode='multiple' selection={selectedStudents} onSelectionChange={(e) => {setSelectedSudents(e.value)}}
                        ref={dt} onContextMenu={(e) => cm.current.show(e.originalEvent)} contextMenuSelection={selectedStudents} 
                        onContextMenuSelectionChange={(e) => setSelectedSudents(e.value)}
            >
                <Column selectionMode="multiple" headerStyle={{ width: '3rem' }}/>
                {columns.map((col, index) => {
                return <Column key={index} field={col.field != 'b64_image' ? col.field : ""} body={col.field == 'b64_image' ? drawingBodyTemplate : null} header={col.header} sortable={col.sortable}
                                editor={col.editable ? (options) => cellEditor(options): null} onCellEditComplete={onCellEditComplete} 
                                className='text-center'/>;

                })}
            </DataTable>
            <Warning warningVisible={warningVisible} setWarningVisible={setWarningVisible} delete_students={delete_students}/>
            <StudentDrawing imageModal={imageModal} setImageModal={setImageModal}/>
        </div>
    )
}