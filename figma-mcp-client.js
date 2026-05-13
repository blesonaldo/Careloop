const https = require('https');

class FigmaMCPClient {
  constructor(baseUrl = 'https://mcp.figma.com/mcp') {
    this.baseUrl = baseUrl;
    this.requestId = 1;
  }

  async sendRequest(method, params = {}) {
    return new Promise((resolve, reject) => {
      const data = JSON.stringify({
        jsonrpc: '2.0',
        id: this.requestId++,
        method: method,
        params: params
      });

      const options = {
        hostname: 'mcp.figma.com',
        port: 443,
        path: '/mcp',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(data),
          'User-Agent': 'Careloop-Figma-Integration/1.0'
        }
      };

      const req = https.request(options, (res) => {
        let responseData = '';
        
        res.on('data', (chunk) => {
          responseData += chunk;
        });
        
        res.on('end', () => {
          try {
            const response = JSON.parse(responseData);
            if (response.error) {
              reject(new Error(`MCP Error: ${response.error.message}`));
            } else {
              resolve(response);
            }
          } catch (e) {
            reject(new Error(`Invalid JSON response: ${responseData}`));
          }
        });
      });

      req.on('error', (e) => {
        reject(e);
      });

      req.write(data);
      req.end();
    });
  }

  async initialize() {
    try {
      const response = await this.sendRequest('initialize', {
        protocolVersion: '2024-11-05',
        capabilities: {
          tools: {}
        },
        clientInfo: {
          name: 'Careloop-Figma-Integration',
          version: '1.0.0'
        }
      });
      console.log('Figma MCP initialized:', response);
      return response;
    } catch (error) {
      console.error('Failed to initialize Figma MCP:', error.message);
      throw error;
    }
  }

  async listTools() {
    try {
      const response = await this.sendRequest('tools/list');
      console.log('Available Figma tools:', response);
      return response;
    } catch (error) {
      console.error('Failed to list tools:', error.message);
      throw error;
    }
  }

  async getFigmaFile(fileId) {
    try {
      const response = await this.sendRequest('tools/call', {
        name: 'get_file',
        arguments: { file_id: fileId }
      });
      console.log('Figma file data:', response);
      return response;
    } catch (error) {
      console.error('Failed to get Figma file:', error.message);
      throw error;
    }
  }
}

// Test the client
async function testFigmaMCP() {
  const client = new FigmaMCPClient();
  
  try {
    console.log('Testing Figma MCP connection...');
    
    // Initialize the connection
    await client.initialize();
    
    // List available tools
    await client.listTools();
    
    console.log('Figma MCP client is working!');
    
  } catch (error) {
    console.error('Figma MCP test failed:', error.message);
  }
}

testFigmaMCP();
