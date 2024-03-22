import { ThreeCircles } from 'react-loader-spinner';

interface LoadingProps {
    isUploading: boolean;
}

export default function Loading(props:LoadingProps) {
    return (
        <div className='absolute flex flex-col bg-transparentDark justify-center items-center w-full h-full z-10'>
            <span className='text-white text-2md font-bold'>{props.isUploading ? 'Uploading...': 'Downloading'}</span>
            <ThreeCircles
              visible={true}
              height="40"
              width="40"
              color="#ffffff"
              ariaLabel="three-circles-loading"
            />
        </div>
    );
}