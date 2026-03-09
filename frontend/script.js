fetch("https://bbpzt86hx1.execute-api.us-east-1.amazonaws.com/prod/patient")
.then(res => res.json())
.then(data => {

console.log(data);

});
