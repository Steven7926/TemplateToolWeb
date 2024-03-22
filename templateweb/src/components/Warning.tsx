import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';

interface Props  {
    warningVisible: boolean;
    setWarningVisible: Function;
    delete_students: Function;
}

export default function Warning(props:Props) {

    const footerContent = (
        <div>
            <Button label="No" icon="pi pi-times" onClick={() => props.setWarningVisible(false)} className="p-button-text mr-10" />
            <Button label="Yes" icon="pi pi-check" onClick={() => {props.delete_students(true); props.setWarningVisible(prev => !prev)}} autoFocus />
        </div>
    );

    return (
        <Dialog header="Delete All Students?" visible={props.warningVisible} style={{ width: '50vw' }} onHide={() => props.setWarningVisible(false)} footer={footerContent}>
            <p className="m-0">
                You are about to Delete All Students in the Database.
            </p>
            <p className="m-0">
                Are you sure you want to continue?
            </p>
        </Dialog>
    );
}