const http = require('http');
const https = require('https');

// Simple Figma MCP proxy server
const server = http.createServer((req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  // Proxy to Figma's MCP server
  const targetUrl = 'https://mcp.figma.com/mcp' + req.url;
  
  const options = {
    hostname: 'mcp.figma.com',
    port: 443,
    path: req.url,
    method: req.method,
    headers: {
      ...req.headers,
      'host': 'mcp.figma.com',
      'origin': 'https://mcp.figma.com'
    }
  };
  
  const proxyReq = https.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });
  
  proxyReq.on('error', (err) => {
    console.error('Proxy error:', err);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      error: 'Proxy error', 
      message: 'Failed to connect to Figma MCP server',
      details: err.message 
    }));
  });
  
  req.pipe(proxyReq);
});

server.listen(3845, '127.0.0.1', () => {
  console.log('Figma MCP proxy server running on http://127.0.0.1:3845');
  console.log('You can now connect to Figma MCP at: http://127.0.0.1:3845/mcp');
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down Figma MCP proxy server...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
