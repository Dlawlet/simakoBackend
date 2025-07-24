# WebSocket Enhancement for Simako Backend

## Flask with WebSocket Support

```python
from flask import Flask
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Keep existing REST API endpoints
@app.route('/api/messages', methods=['POST'])
def receive_message():
    # ... existing code to save to MongoDB ...
    
    # After saving to database, notify all connected clients
    if result.inserted_id:
        # Broadcast to all connected dashboards/devices
        socketio.emit('new_message', {
            'message_id': str(result.inserted_id),
            'sim_id': message['sim_id'],
            'type': message['type'],
            'from': message['from'],
            'message': message['message'],
            'timestamp': message['timestamp']
        })
    
    return jsonify({'status': 'ok'})

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'msg': 'Connected to Simako backend'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('subscribe_sim')
def handle_subscribe(data):
    sim_id = data.get('sim_id')
    # Join room for specific SIM updates
    join_room(f"sim_{sim_id}")
    emit('status', {'msg': f'Subscribed to {sim_id} updates'})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
```

## Node.js with WebSocket Support

```javascript
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Keep existing REST API endpoints
app.post('/api/messages', async (req, res) => {
  // ... existing code to save to MongoDB ...
  
  // After saving, emit to all connected clients
  if (savedMessage) {
    io.emit('new_message', {
      message_id: savedMessage._id,
      sim_id: savedMessage.sim_id,
      type: savedMessage.type,
      from: savedMessage.from,
      message: savedMessage.message,
      timestamp: savedMessage.timestamp
    });
  }
  
  res.status(201).json({status: 'ok'});
});

// WebSocket connection handling
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  socket.emit('status', {msg: 'Connected to Simako backend'});
  
  socket.on('subscribe_sim', (data) => {
    const simId = data.sim_id;
    socket.join(`sim_${simId}`);
    socket.emit('status', {msg: `Subscribed to ${simId} updates`});
  });
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

server.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

## Android WebSocket Client (Optional Enhancement)

```kotlin
// Add to build.gradle.kts
implementation("io.socket:socket.io-client:2.0.0")

// WebSocket service
class WebSocketService {
    private var socket: Socket? = null
    
    fun connect() {
        try {
            socket = IO.socket("http://10.0.2.2:5000")
            
            socket?.on(Socket.EVENT_CONNECT) {
                Log.d("WebSocket", "Connected to backend")
            }
            
            socket?.on("new_message") { args ->
                val data = args[0] as JSONObject
                Log.d("WebSocket", "New message received: $data")
                // Update UI or notify user
            }
            
            socket?.connect()
        } catch (e: Exception) {
            Log.e("WebSocket", "Connection failed: ${e.message}")
        }
    }
    
    fun subscribeToSim(simId: String) {
        socket?.emit("subscribe_sim", JSONObject().put("sim_id", simId))
    }
}
```

## Web Dashboard with WebSocket

```html
<!DOCTYPE html>
<html>
<head>
    <title>Simako Live Dashboard</title>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
</head>
<body>
    <h1>Simako Live SMS Dashboard</h1>
    <div id="messages"></div>
    
    <script>
        const socket = io('http://localhost:5000');
        
        socket.on('connect', () => {
            console.log('Connected to Simako backend');
        });
        
        socket.on('new_message', (data) => {
            const messageDiv = document.createElement('div');
            messageDiv.innerHTML = `
                <p><strong>From:</strong> ${data.from}</p>
                <p><strong>SIM:</strong> ${data.sim_id}</p>
                <p><strong>Message:</strong> ${data.message}</p>
                <p><strong>Time:</strong> ${data.timestamp}</p>
                <hr>
            `;
            document.getElementById('messages').prepend(messageDiv);
        });
    </script>
</body>
</html>
```
