const WebSocket = require('ws');

const ws = new WebSocket('wss://dusty-steel-atlasaurus.glitch.me');

ws.on('open', () => {
  console.log('Connected to WebSocket server');
  ws.send(JSON.stringify({ type: 'sender' })); // Kirim pesan sebagai sender
});

ws.on('message', (message) => {
  console.log('Received:', message);
});

ws.on('close', () => {
  console.log('Connection closed');
});
