const https = require('https');

// Test direct connection to Figma MCP server
function testFigmaConnection() {
  const options = {
    hostname: 'mcp.figma.com',
    port: 443,
    path: '/mcp',
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'Careloop-Figma-Integration/1.0'
    }
  };

  const req = https.request(options, (res) => {
    console.log(`Status: ${res.statusCode}`);
    console.log(`Headers: ${JSON.stringify(res.headers, null, 2)}`);
    
    let data = '';
    res.on('data', (chunk) => {
      data += chunk;
    });
    
    res.on('end', () => {
      console.log(`Response: ${data}`);
      try {
        const parsed = JSON.parse(data);
        console.log('Figma MCP server is accessible!');
        console.log('Available methods:', parsed);
      } catch (e) {
        console.log('Raw response from Figma MCP server');
      }
    });
  });

  req.on('error', (e) => {
    console.error(`Problem with request: ${e.message}`);
  });

  req.end();
}

// Test the connection
testFigmaConnection();
