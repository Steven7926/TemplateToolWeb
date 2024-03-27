export interface StatusResponse {
    success: boolean;
}

export interface FileFetchResponse {
    success: boolean;
    file: Blob;
}

export interface Student {
    name: string;
    b64_image: string;
    uuid: string;
    class: string;
    teacher: string;
    school: string;
    location: string;
    year: string;
    image: string;
    id: string;
    use_preset: string;
}

export interface ImageModal {
    show: boolean;
    b64: string;
    student_name: string;
}