// server.js
import express from 'express';
import bodyParser from 'body-parser';
import cors from 'cors';
import dotenv from 'dotenv';
import fetch from 'node-fetch';
import { WebSocketServer } from 'ws';

dotenv.config();
const app = express();
const PORT = process.env.PORT || 8000;

app.use(cors());
app.use(bodyParser.json());

// In-memory storage for demo (replace with DB in production)
const alertClients = new Set();

// Simple health endpoint
app.get('/', (req, res) => res.json({ status: 'ok', time: new Date().toISOString() }));

// CHAT endpoint: proxies messages to LLM or returns canned reply if no key
app.post('/chat', async (req, res) => {
  // req.body: { userId, message, context }
  const { userId, message, context } = req.body || {};
  if (!message) return res.status(400).json({ error: 'message required' });

  // Minimal prompt building
  const systemPrompt = "You are HANNA, an empathetic health coach. Ask clarifying questions when needed. Never provide a medical diagnosis; advise clinical visit for red flags.";
  const payload = {
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: systemPrompt },
      ...(context || []),
      { role: 'user', content: message }
    ],
    max_tokens: 512
  };

  if (!process.env.OPENAI_API_KEY) {
    // fallback canned reply (useful for dev)
    const canned = `HANNA: Thanks — I heard: "${message}". (Dev mode: no LLM key configured.) Try asking "What's my heart rate?" or "What should I do if SpO2 is low?"`;
    return res.json({ reply: canned });
  }

  try {
    const r = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    const j = await r.json();
    const text = j?.choices?.[0]?.message?.content || 'Sorry, I could not generate a response.';
    // TODO: Save chat to DB
    res.json({ reply: text });
  } catch (err) {
    console.error('LLM error', err);
    res.status(500).json({ error: 'LLM failure' });
  }
});

// Vitals analyzer: rules + optional calls to prediction endpoints
app.post('/analyze/vitals', async (req, res) => {
  // body: { patientId, vitals: { heart_rate, spo2, resp_rate, ... }, timestamp }
  const body = req.body || {};
  const vitals = body.vitals || {};
  const patientId = body.patientId || 'unknown';
  const issues = [];

  // simple rule checks
  if (vitals.spo2 !== undefined && vitals.spo2 < 92) {
    issues.push({ level: 'high', code: 'low_spo2', text: 'Oxygen saturation below 92%' });
  }
  if (vitals.heart_rate !== undefined && vitals.heart_rate > 120) {
    issues.push({ level: 'high', code: 'tachycardia', text: 'Elevated heart rate (>120 bpm)' });
  }

  // Optionally call existing prediction endpoints (if accessible)
  try {
    if (process.env.API_BASE_URL) {
      // Example: call asthma predict endpoint if vitals include respiration or wheeze indicators
      // This is optional and depends on your backend; adjust endpoints as needed.
      if (vitals.FEV1 || vitals.resp_rate || vitals.Age) {
        const p = await fetch(`${process.env.API_BASE_URL}/predict_asthma/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(vitals)
        }).catch(()=>null);
        if (p && p.ok) {
          const pj = await p.json().catch(()=>null);
          if (pj && pj.prediction === 1 && pj.confidence > 0.7) {
            issues.push({ level: 'high', code: 'asthma_risk', text: `Asthma risk detected (${Math.round(pj.confidence*100)}%)` });
          }
        }
      }
    }
  } catch(e) {
    console.warn('prediction call failed', e);
  }

  // Broadcast high issues via WS
  for (const issue of issues) {
    if (issue.level === 'high') {
      for (const ws of alertClients) {
        try {
          ws.send(JSON.stringify({ patientId, issue }));
        } catch(e) { /* ignore */ }
      }
    }
  }

  // TODO: persist vitals and issues to DB
  res.json({ issues });
});

// Start server and WS upgrade handling
import http from 'http';
const server = http.createServer(app);

const wss = new WebSocketServer({ noServer: true });
wss.on('connection', (ws) => {
  alertClients.add(ws);
  ws.on('close', () => alertClients.delete(ws));
  ws.on('message', (msg) => {
    // optionally handle subscription messages
    // console.log('ws msg', msg.toString());
  });
});

server.on('upgrade', (request, socket, head) => {
  // Accept upgrade for path '/alerts'
  const { url } = request;
  if (url === '/alerts') {
    wss.handleUpgrade(request, socket, head, (ws) => {
      wss.emit('connection', ws, request);
    });
  } else {
    socket.destroy();
  }
});

server.listen(PORT, () => console.log(`HANNA backend listening on ${PORT}`));
