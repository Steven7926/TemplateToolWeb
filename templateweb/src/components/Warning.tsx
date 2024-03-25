import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import { Student } from "../common/interfaces";

interface Props  {
    warningVisible: boolean;
    setWarningVisible: Function;
    delete_students: Function;
    selectedStudents: Student[];
}

export default function Warning(props:Props) {

    const footerContent = (
        <div>
            <Button label="No" icon="pi pi-times" onClick={() => props.setWarningVisible(false)} className="p-button-text mr-10" />
            <Button label="Yes" icon="pi pi-check" onClick={() => {props.delete_students(true); props.setWarningVisible(prev => !prev)}} autoFocus />
        </div>
    );
    const selected = props.selectedStudents.map((student) => student.name).join(", ")
    const header = props.selectedStudents.length > 0  ? "You are about to delete " + selected : "You are about to Delete ALL Students in the Database."

    return (
        <Dialog header="Delete Students?" visible={props.warningVisible} style={{ width: '50vw' }} onHide={() => props.setWarningVisible(false)} footer={footerContent}>
            <p className="m-0 font-extrabold">
                {header}
            </p>
            <p className="m-0">
                Are you sure you want to continue?
            </p>
        </Dialog>
    );
}