export default function RiskIndicator({risk}){

 let color="green";

 if(risk==="HIGH") color="red";
 if(risk==="MEDIUM") color="orange";

 return(

  <div style={{
   background:color,
   padding:"10px",
   color:"white"
  }}>

  Risk Level: {risk}

  </div>

 );

}
