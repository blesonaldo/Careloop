require('dotenv').config();
const express = require('express');
const fetch = require('node-fetch');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// OpenAI API integration
app.post('/api/generate-message', async (req, res) => {
  const { customer, userName, userBusiness } = req.body;

  // Validate OpenAI API key
  if (!process.env.OPEN_AI_API_KEY) {
    return res.status(500).json({ error: 'OpenAI API key is not configured. Please set OPEN_AI_API_KEY in your environment variables.' });
  }

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.OPEN_AI_API_KEY}` 
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        max_tokens: 300,
        messages: [
          {
            role: 'system',
            content: `You are a helpful assistant for a small business owner using Careloop, a customer relationship tool. Generate short, warm, and natural follow-up messages that business owners can send to their customers via WhatsApp. The message should feel personal and human — not like a marketing email. No subject line, no sign-off placeholder, no bullet points. Just the message body, 3-5 sentences max.` 
          },
          {
            role: 'user',
            content: `Generate a WhatsApp follow-up message for this customer:
Name: ${customer.name}
Their business/context: ${customer.business}
Last contacted: ${customer.lastContact}
Notes: ${customer.notes}

The message is from: ${userName} at ${userBusiness}.`
          }
        ]
      })
    });

    const data = await response.json();

    if (data.error) {
      return res.status(500).json({ error: `OpenAI API Error: ${data.error.message}` });
    }

    if (!data.choices || data.choices.length === 0) {
      return res.status(500).json({ error: 'No response generated from OpenAI API' });
    }

    res.json({ message: data.choices[0].message.content.trim() });

  } catch (err) {
    console.error('OpenAI API Error:', err);
    if (err.response && err.response.status === 401) {
      res.status(500).json({ error: 'Invalid OpenAI API key. Please check your OPEN_AI_API_KEY environment variable.' });
    } else if (err.response && err.response.status === 429) {
      res.status(500).json({ error: 'OpenAI API rate limit exceeded. Please try again later.' });
    } else {
      res.status(500).json({ error: 'Failed to generate message. Please try again.' });
    }
  }
});

// Customer data management (in-memory for now)
let customers = [];

// Get all customers
app.get('/api/customers', (req, res) => {
  res.json({ customers });
});

// Add new customer
app.post('/api/customers', (req, res) => {
  const { name, business, phone, email } = req.body;
  const newCustomer = {
    id: Date.now(),
    name,
    business,
    phone,
    email,
    lastContact: new Date().toISOString(),
    notes: ''
  };
  customers.push(newCustomer);
  res.json({ customer: newCustomer });
});

app.listen(3001, () => console.log('Careloop follow-up service running on http://localhost:3001'));
