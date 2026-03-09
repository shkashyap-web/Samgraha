import {
 LineChart,
 Line,
 XAxis,
 YAxis,
 Tooltip,
 CartesianGrid
} from "recharts";

export default function PatientTimelineChart({data}) {

 return (

  <LineChart width={700} height={300} data={data}>

   <CartesianGrid strokeDasharray="3 3"/>

   <XAxis dataKey="visitTimestamp"/>

   <YAxis/>

   <Tooltip/>

   <Line type="monotone"
         dataKey="risk_score"
         stroke="#ff0000"/>

  </LineChart>

 );
}
