const express = require('express');
const WebSocket = require('ws');
const os = require('os');
const pty = require('node-pty');

const app = express();
const port = 8000;

// Serve static files
app.use(express.static('static'));

// Create HTTP server
const server = app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});

// Create WebSocket server
const wss = new WebSocket.Server({ server });

// Terminal settings
const shell = os.platform() === 'win32' ? 'powershell.exe' : 'bash';
const shellArgs = os.platform() === 'win32' ? [] : [];

wss.on('connection', (ws) => {
    console.log('Client connected');

    // Create terminal
    const term = pty.spawn(shell, shellArgs, {
        name: 'xterm-color',
        cols: 80,
        rows: 24,
        cwd: process.cwd(),
        env: process.env
    });

    // Handle incoming data from client
    ws.on('message', (data) => {
        term.write(data);
    });

    // Handle terminal output
    term.on('data', (data) => {
        try {
            ws.send(data);
        } catch (ex) {
            // Client probably closed
        }
    });

    // Handle client disconnect
    ws.on('close', () => {
        term.kill();
        console.log('Client disconnected');
    });
});
