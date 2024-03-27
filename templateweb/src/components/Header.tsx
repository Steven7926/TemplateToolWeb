import { useEffect } from "react";
import { FilterMatchMode, FilterOperator } from 'primereact/api';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Student} from "../common/interfaces";

interface Props {
    setSelectedSudents: Function;
    selectedStudents: Student[];
    downloadDrawings: Function;
    genereatePDFs: Function;
    dtRef: any;
    students: Student[];
    setFilters: Function;
    setGlobalFilterValue: Function;
    filters: any;
    globalFilterValue: string;
}

export default function Header(props: Props) {

    const clearFilter = () => {
        initFilters();
        props.setSelectedSudents([]);
    };

    const initFilters = () => {
        props.setFilters({
            global: { value: null, matchMode: FilterMatchMode.CONTAINS },
            name: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }] },
            class: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }] },
            teacher: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }] },
            school: { operator: FilterOperator.AND, constraints: [{ value: null, matchMode: FilterMatchMode.STARTS_WITH }] }
        });
        props.setGlobalFilterValue('');
    };

    const onGlobalFilterChange = (e) => {
        props.setSelectedSudents([])
        const value = e.target.value;
        let _filters = { ...props.filters };

        _filters['global'].value = value;

        props.setFilters(_filters);
        props.setGlobalFilterValue(value);
    };

    const exportCSV = (selectionOnly) => {
        props.dtRef.current.exportCSV({ selectionOnly });
    };

    const exportExcel = () => {
        import('xlsx').then((xlsx) => {
            const export_all = props.selectedStudents.length > 1 ? false : true;
            
            // Removing b64 image for now from export because it leads to a character overflow in excel
            let studentCopy = export_all ? props.students.map((student) => {return { ...student, b64_image: '' }}): 
                              props.selectedStudents.map((student) => {return { ...student, b64_image: '' }});

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

    useEffect(() => {
        initFilters();
    }, []);

    return (
        <div className="flex sm:flex-row flex-col items-center justify-between max-w-[95vw]">
                <div className='flex flex-row'>
                  <Button type="button" label="Clear" icon="pi pi-filter-slash" outlined onClick={clearFilter} className='mx-2 py-2'/>
                  <span className="p-input-icon-right flex flex-row justify-center items-center">
                      <InputText value={props.globalFilterValue} onChange={onGlobalFilterChange} placeholder="Search" className='py-2 ml-1'/>
                      <i className="pi pi-search"/>
                  </span>
                </div>
                <div>
                  <Button type="button" icon="pi pi-file" onClick={() => props.downloadDrawings()} data-pr-tooltip="CSV" 
                          className='m-2 pl-2 bg-button text-white'
                  >
                    <span className='m-1 pl-1 pr-1'>Download Drawing(s)</span>
                  </Button>
                  <Button type="button" icon="pi pi-file-pdf" data-pr-tooltip="CSV" 
                          className='m-2 pl-2 bg-button text-white' onClick={() => props.genereatePDFs()}
                  >
                    <span className='m-1 pl-1 pr-1'>Generate PDF(s)</span>
                  </Button>
                </div>
                <div>
                  <Button type="button" icon="pi pi-file" aria-label='export csv' onClick={() => exportCSV(props.selectedStudents.length  > 0 ? true : false)} data-pr-tooltip="CSV" 
                          className='m-2 pl-2 bg-button text-white'
                  >
                    <span className='m-1 pl-1 pr-1'>CSV</span>
                  </Button>
                  <Button type="button" icon="pi pi-file-excel" aria-label='export excel' onClick={exportExcel} data-pr-tooltip="CSV" 
                          className='m-2 pl-2 bg-button text-white'
                  >
                    <span className='m-1 pl-1 pr-1'>Excel</span>
                  </Button>
                </div>
            </div>
    );
}
