const https = require('https');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

class FigmaMCPAuth {
  constructor() {
    this.baseUrl = 'https://mcp.figma.com/mcp';
    this.requestId = 1;
  }

  async sendRequest(method, params = {}, token = null) {
    return new Promise((resolve, reject) => {
      const data = JSON.stringify({
        jsonrpc: '2.0',
        id: this.requestId++,
        method: method,
        params: params
      });

      const headers = {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
        'User-Agent': 'Careloop-Figma-Integration/1.0'
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const options = {
        hostname: 'mcp.figma.com',
        port: 443,
        path: '/mcp',
        method: 'POST',
        headers: headers
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

  async authenticate(token) {
    try {
      console.log('Attempting authentication with Figma MCP...');
      const response = await this.sendRequest('initialize', {
        protocolVersion: '2024-11-05',
        capabilities: {
          tools: {}
        },
        clientInfo: {
          name: 'Careloop-Figma-Integration',
          version: '1.0.0'
        }
      }, token);
      
      console.log('Authentication successful!');
      return response;
    } catch (error) {
      console.error('Authentication failed:', error.message);
      throw error;
    }
  }

  async getAvailableTools(token) {
    try {
      const response = await this.sendRequest('tools/list', {}, token);
      return response;
    } catch (error) {
      console.error('Failed to get tools:', error.message);
      throw error;
    }
  }
}

// Authentication flow
async function authenticateFigma() {
  const auth = new FigmaMCPAuth();
  
  console.log('\n=== Figma MCP Authentication ===');
  console.log('To authenticate with Figma MCP, you need a Figma access token.');
  console.log('You can get one from: https://www.figma.com/developers/api#access-tokens');
  console.log('');
  
  return new Promise((resolve, reject) => {
    rl.question('Please enter your Figma access token: ', async (token) => {
      if (!token) {
        console.log('No token provided. Authentication cancelled.');
        rl.close();
        reject(new Error('No authentication token provided'));
        return;
      }

      try {
        // Test authentication
        await auth.authenticate(token.trim());
        
        // Get available tools
        const tools = await auth.getAvailableTools(token.trim());
        console.log('\nAvailable Figma MCP tools:');
        console.log(JSON.stringify(tools, null, 2));
        
        console.log('\n=== Authentication Successful! ===');
        console.log('You can now use Figma MCP tools.');
        console.log('Your token:', token.substring(0, 10) + '...');
        
        rl.close();
        resolve(token.trim());
        
      } catch (error) {
        console.error('Authentication failed:', error.message);
        rl.close();
        reject(error);
      }
    });
  });
}

// Test without token first to see what we get
async function testWithoutAuth() {
  const auth = new FigmaMCPAuth();
  
  try {
    console.log('Testing Figma MCP without authentication...');
    const response = await auth.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: { tools: {} },
      clientInfo: { name: 'Careloop-Figma-Integration', version: '1.0.0' }
    });
    console.log('Unexpected success:', response);
  } catch (error) {
    console.log('Expected authentication error:', error.message);
    console.log('Now proceeding with authentication...');
    
    // Try authentication
    try {
      await authenticateFigma();
    } catch (authError) {
      console.log('Authentication failed. Please check your Figma access token.');
    }
  }
}

testWithoutAuth();
