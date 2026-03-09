import {useDropzone} from "react-dropzone";

export default function UploadBox(){

 const {getRootProps,getInputProps}=useDropzone({
  onDrop:acceptedFiles=>{
   console.log(acceptedFiles);
  }
 });

 return(

  <div {...getRootProps()}
   style={{
    border:"2px dashed gray",
    padding:"40px"
   }}>

   <input {...getInputProps()} />

   Drag Prescription Here

  </div>

 );

}
