mkdir bkp
cp *.js bkp
mkdir instr
nyc instrument app.js instr
nyc instrument app2.js instr
nyc instrument recur.js instr
nyc instrument utils.js instr
cp instr/*.js . 

