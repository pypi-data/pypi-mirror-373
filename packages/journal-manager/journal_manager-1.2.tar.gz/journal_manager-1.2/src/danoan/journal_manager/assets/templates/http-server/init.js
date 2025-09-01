const promisify = require('util').promisify;
const execFile = require('child_process').execFile;
const path = require('path');
const fileURLToPath = require('url').fileURLToPath;
const express = require('express');


const app = express();
const p_execFile = promisify(execFile);


const port = 4960;
const HTTP_SERVER_ROOT = path.resolve(__dirname);
const PROJECT_ROOT = path.dirname(HTTP_SERVER_ROOT);

app.use('/',express.static(`${PROJECT_ROOT}/site`));


//Not able to make it work inside a container when specifying the hostname
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});


