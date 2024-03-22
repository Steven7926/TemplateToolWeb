import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import { ImageModal } from "../common/interfaces";

interface ImageProps {
    imageModal: ImageModal;
    setImageModal: Function;
}

export default function StudentDrawing(props:ImageProps) {

    return (
        <Dialog header={props.imageModal.student_name + "'s Drawing"} visible={props.imageModal.show}
                style={{ width: '30vw' }} onHide={() => props.setImageModal({show: false, b64: '', student_name: ''})}
                closeOnEscape 
        >
            <div className='flex flex-col items-center justify-center' >
                <img alt="student drawing" src={'data:image/png;base64,' + props.imageModal.b64} width="250" className='rounded-lg'/>
            </div>    
        </Dialog>
    );
}