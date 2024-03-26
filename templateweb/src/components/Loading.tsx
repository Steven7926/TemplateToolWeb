import { ProgressSpinner } from 'primereact/progressspinner';

interface LoadingProps {
    isUploading: boolean;
}

export default function Loading(props:LoadingProps) {
    return (
        <div className='absolute flex flex-col bg-transparentDark justify-center items-center w-full h-full z-10'>
            <span className='text-white text-2md font-bold'>{props.isUploading ? 'Uploading...': 'Downloading'}</span>
            <ProgressSpinner style={{width: '50px', height: '50px'}} strokeWidth="8" fill="transparent" animationDuration=".5s" />
        </div>
    );
}