import {useState} from "react";

export default function AICopilot(){

 const [question,setQuestion]=useState("");
 const [response,setResponse]=useState("");

 return(

  <div>

  <h3>AI Doctor Assistant</h3>

  <input
   value={question}
   onChange={(e)=>setQuestion(e.target.value)}
  />

  <button>Ask</button>

  <p>{response}</p>

  </div>

 );

}
