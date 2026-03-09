export default function DocumentViewer({url}){

 return(

  <iframe
   src={url}
   width="100%"
   height="500"
   title="Medical Document"
  />

 );

}
