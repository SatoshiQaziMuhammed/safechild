const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const fs = require('fs-extra');
const path = require('path');
const axios = require('axios');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = 8002;
const SHARED_DIR = '/tmp/forensics_uploads'; // Shared with Python Backend

// Store active clients in memory (for demo purposes)
const clients = {};

// Helper: Generate a unique ID
const generateId = () => Math.random().toString(36).substring(2, 15);

app.post('/session/start', async (req, res) => {
    const { clientNumber } = req.body;
    const sessionId = `wa_${clientNumber}_${generateId()}`;
    
    console.log(`[WA] Starting session for ${clientNumber} (${sessionId})`);

    const client = new Client({
        authStrategy: new LocalAuth({ clientId: sessionId }),
        puppeteer: {
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        }
    });

    clients[sessionId] = {
        client,
        qr: null,
        status: 'initializing'
    };

    client.on('qr', (qr) => {
        console.log(`[WA] QR received for ${sessionId}`);
        qrcode.toDataURL(qr, (err, url) => {
            if (clients[sessionId]) {
                clients[sessionId].qr = url;
                clients[sessionId].status = 'qr_ready';
            }
        });
    });

    client.on('ready', async () => {
        console.log(`[WA] Client ${sessionId} is ready!`);
        if (clients[sessionId]) {
            clients[sessionId].status = 'connected';
            clients[sessionId].qr = null; // Clear QR
            
            // Start extraction automatically
            await extractData(sessionId, client, clientNumber);
        }
    });

    client.on('auth_failure', () => {
        if (clients[sessionId]) clients[sessionId].status = 'failed';
    });

    client.initialize();

    res.json({ success: true, sessionId });
});

app.get('/session/:sessionId/status', (req, res) => {
    const { sessionId } = req.params;
    const session = clients[sessionId];

    if (!session) {
        return res.status(404).json({ error: 'Session not found' });
    }

    res.json({
        status: session.status,
        qr: session.qr
    });
});

async function extractData(sessionId, client, clientNumber) {
    try {
        console.log(`[WA] Extracting chats for ${sessionId}...`);
        clients[sessionId].status = 'extracting';

        const chats = await client.getChats();
        console.log(`[WA] Found ${chats.length} chats`);

        let fullTranscript = "";
        
        // Limit to last 50 chats for performance in this demo
        const recentChats = chats.slice(0, 50);

        for (const chat of recentChats) {
            fullTranscript += `\n--- CHAT WITH ${chat.name || chat.id.user} ---\n`;
            
            // Fetch last 100 messages per chat
            const messages = await chat.fetchMessages({ limit: 100 });
            
            for (const msg of messages) {
                const date = new Date(msg.timestamp * 1000).toLocaleString();
                const sender = msg.fromMe ? "ME" : (chat.name || "Other");
                fullTranscript += `[${date}] ${sender}: ${msg.body}\n`;
            }
        }

        // Save to file
        await fs.ensureDir(SHARED_DIR);
        const filename = `WHATSAPP_AUTO_${clientNumber}_${Date.now()}.txt`;
        const filePath = path.join(SHARED_DIR, filename);
        
        await fs.writeFile(filePath, fullTranscript, 'utf8');
        console.log(`[WA] Saved transcript to ${filePath}`);

        // Notify Python Backend
        // In Docker, backend is at http://backend:8001
        const backendUrl = 'http://backend:8001/api/forensics/analyze-internal';
        
        try {
            await axios.post(backendUrl, {
                file_path: filePath,
                client_number: clientNumber,
                source: 'whatsapp_automation'
            });
            console.log(`[WA] Notified backend successfully.`);
            clients[sessionId].status = 'completed';
        } catch (err) {
            console.error(`[WA] Failed to notify backend:`, err.message);
            clients[sessionId].status = 'completed_error';
        }

        // Cleanup after a delay
        setTimeout(async () => {
            await client.destroy();
            delete clients[sessionId];
        }, 60000);

    } catch (err) {
        console.error(`[WA] Extraction failed:`, err);
        clients[sessionId].status = 'failed';
    }
}

app.listen(PORT, () => {
    console.log(`WhatsApp Service running on port ${PORT}`);
});
