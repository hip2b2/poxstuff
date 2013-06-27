/** 
 * node.js http example
 * wyu@ateneo.edu
**/

// load libraries
var http = require('http');
var url = require("url");

var server = http.createServer(function(req, res) {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  var data = '';
  var path = url.parse(req.url).pathname;

  // handle request and display POST data on session end
  req
    .on('data', function(chunk) {
      data += chunk;
    })
    .on('end', function() {
      console.log('POST data to %s: %s', path, data);
    })

  // always return this per session
  res.end('Hello World\n');
});

console.log("Server listenning.")
server.listen(8080);

// sample run of test http server with POST data
// curl -d "data=ASDFASF&data2=34534534" localhost:8080/somepath
