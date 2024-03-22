export const downloadFile = (blob: Blob) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const date = new Date().getDate() + '_' + (new Date().getMonth() + 1) + '_' + new Date().getFullYear();
    link.setAttribute('download', date + '_student_templates.zip');
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
}