// =============================
// SAMGRAHA DASHBOARD SCRIPT
// =============================


// API endpoint
const API_URL =
"https://bbpzt86hx1.execute-api.us-east-1.amazonaws.com/prod/patient";



// =============================
// FETCH PATIENT DATA
// =============================

async function loadPatientData(){

 try{

  const response = await fetch(API_URL);

  const data = await response.json();

  console.log("API DATA:",data);

  const visits = data.visits || [];

  if(visits.length === 0) return;

  const latest = visits[visits.length - 1];


  // =============================
  // PATIENT INFO
  // =============================

  document.getElementById("patientName").innerText =
  latest.patient_name || "Unknown";

  document.getElementById("patientAge").innerText =
  latest.age || "-";

  document.getElementById("patientID").innerText =
  latest.patientId || "-";


  // =============================
  // CLINICAL SIGNALS
  // =============================

  document.getElementById("riskAlert").innerText =
  data.risk_flag || "No major risk detected";

  document.getElementById("doctorInsight").innerText =
  (data.doctor_insights || []).join(", ") || "No insights";

  document.getElementById("aiBriefing").innerText =
  data.clinical_briefing || "Clinical briefing unavailable";


  // =============================
  // RISK INDICATOR
  // =============================

  const riskIndicator =
  document.getElementById("riskIndicator");

  if(data.risk_flag){

   riskIndicator.innerText = "HIGH";

   riskIndicator.style.background = "red";
   riskIndicator.style.color = "white";

  }else{

   riskIndicator.innerText = "LOW";

   riskIndicator.style.background = "green";
   riskIndicator.style.color = "white";

  }



  // =============================
  // TIMELINE TABLE
  // =============================

  const table =
  document.getElementById("timelineTable");

  visits.forEach(v => {

   const row = table.insertRow();

   row.innerHTML = `
    <td>${v.visitTimestamp || "-"}</td>
    <td>${v.diagnosis || "-"}</td>
    <td>${(v.tests || []).join(", ")}</td>
    <td>${(v.treatment || []).join(", ")}</td>
   `;

  });



  // =============================
  // RISK TIMELINE CHART
  // =============================

  const labels = visits.map(v => v.visitTimestamp);

  const scores = visits.map((v,i)=> i+1);


  const ctx =
  document.getElementById("riskChart");

  if(ctx){

   new Chart(ctx,{

    type:'line',

    data:{

     labels:labels,

     datasets:[{

      label:"Clinical Risk Progression",

      data:scores,

      borderColor:"red",

      fill:false

     }]

    }

   });

  }



 }catch(err){

  console.error("Error loading patient data",err);

 }

}

loadPatientData();



// =============================
// AI COPILOT
// =============================

async function askCopilot(){

 const question =
 document.getElementById("copilotQuestion").value;

 document.getElementById("copilotAnswer").innerText =
 "Analyzing patient history...";

 // placeholder (later connect to Bedrock)

 setTimeout(()=>{

  document.getElementById("copilotAnswer").innerText =
  "AI Copilot suggests monitoring cardiovascular risk.";

 },1000);

}



// =============================
// DRAG DROP UPLOAD BOX
// =============================

const uploadBox =
document.getElementById("uploadBox");

if(uploadBox){

 uploadBox.addEventListener("dragover",(e)=>{
  e.preventDefault();
 });

 uploadBox.addEventListener("drop",(e)=>{

  e.preventDefault();

  const file = e.dataTransfer.files[0];

  if(file){

   alert("File uploaded: " + file.name);

   // Later connect to S3 upload API

  }

 });

}
