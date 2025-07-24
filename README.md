# Simako Backend - Flask & Node.js with MongoDB

This project contains both Flask and Node.js backends for the Simako SMS management system, both integrated with MongoDB and designed to work with SimakoHost.

## Project Structure

```
backend/
├── flask/                 # Flask backend (Python)
│   ├── app.py            # Main Flask application
│   ├── requirements.txt  # Python dependencies
│   └── .env             # Environment configuration
├── nodejs/               # Node.js backend (Express)
│   ├── server.js        # Main Express server
│   ├── package.json     # Node.js dependencies
│   └── .env            # Environment configuration
└── README.md           # This file
```

## Features

Both backends provide:
- **RESTful API** for SMS/Call message management (current implementation)
- MongoDB integration for data persistence
- SIM card registration and management
- SimakoHost integration endpoints
- CORS support for web applications
- Comprehensive error handling
- Health check endpoints

### Architecture: REST API (HTTP Request/Response)
```
Android App → HTTP POST → Backend → MongoDB (Store SMS/Call data)
Android App ← HTTP GET ← Backend ← MongoDB (Retrieve message history)
```

**Why REST API for Simako:**
- ✅ Perfect for storing SMS/call data reliably
- ✅ Simple Android integration via HTTP calls
- ✅ Easy to test and debug
- ✅ Standard caching and scaling patterns
- ✅ Stateless and reliable

## Quick Start

### Prerequisites

1. **MongoDB**: Install and run MongoDB locally or use MongoDB Atlas
2. **Python 3.8+** (for Flask backend)
3. **Node.js 16+** (for Node.js backend)

### Flask Backend Setup

```bash
cd backend/flask

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env file with your MongoDB URI and other settings

# Run the server
python app.py
```

Flask backend will run on: http://localhost:5000

### Node.js Backend Setup

```bash
cd backend/nodejs

# Install dependencies
npm install

# Configure environment
# Edit .env file with your MongoDB URI and other settings

# Run in development mode
npm run dev

# Or run in production mode
npm start
```

Node.js backend will run on: http://localhost:3000

## API Endpoints

Both backends provide the same REST API:

### Health Check
- `GET /health` - Service health and status

### Messages
- `POST /api/messages` - Receive SMS/Call messages from SimakoHost
- `GET /api/messages` - Retrieve messages (with filtering)
- `PUT /api/messages/:id/processed` - Mark message as processed

### SIM Cards
- `GET /api/sim-cards` - Get registered SIM cards
- `POST /api/sim-cards` - Register new SIM card

### SimakoHost Integration
- `GET /api/simakohost/status` - SimakoHost integration status
- `POST /api/simakohost/send-sms` - Send SMS via SimakoHost

## MongoDB Collections

### messages
```json
{
  "_id": "ObjectId",
  "sim_id": "string",
  "type": "sms|call",
  "from": "string",
  "to": "string",
  "message": "string",
  "timestamp": "Date",
  "processed": "boolean",
  "processed_at": "Date",
  "metadata": "object",
  "created_at": "Date"
}
```

### sim_cards
```json
{
  "_id": "ObjectId",
  "sim_id": "string",
  "phone_number": "string",
  "carrier": "string",
  "is_active": "boolean",
  "created_at": "Date",
  "last_seen": "Date"
}
```

## Environment Configuration

### Flask (.env)
```
MONGO_URI=mongodb://localhost:27017/
DATABASE_NAME=simako_db
FLASK_ENV=development
FLASK_DEBUG=True
API_PORT=5000
API_HOST=0.0.0.0
SIMAKOHOST_API_URL=http://localhost:8080
SIMAKOHOST_API_KEY=your_api_key_here
```

### Node.js (.env)
```
MONGO_URI=mongodb://localhost:27017/simako_db
NODE_ENV=development
PORT=3000
HOST=0.0.0.0
SIMAKOHOST_API_URL=http://localhost:8080
SIMAKOHOST_API_KEY=your_api_key_here
```

## Usage Examples

### Receiving a Message from SimakoHost

```bash
curl -X POST http://localhost:5000/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "sim_id": "SIM001",
    "type": "sms",
    "from": "+1234567890",
    "to": "+0987654321",
    "message": "Hello from SimakoHost!"
  }'
```

### Retrieving Messages

```bash
# Get all messages
curl http://localhost:5000/api/messages

# Get messages for specific SIM
curl http://localhost:5000/api/messages?sim_id=SIM001

# Get SMS messages only
curl http://localhost:5000/api/messages?type=sms
```

### Registering a SIM Card

```bash
curl -X POST http://localhost:5000/api/sim-cards \
  -H "Content-Type: application/json" \
  -d '{
    "sim_id": "SIM001",
    "phone_number": "+1234567890",
    "carrier": "Carrier Name"
  }'
```

## Development

### Running Both Backends Simultaneously

You can run both backends at the same time on different ports:
- Flask: http://localhost:5000
- Node.js: http://localhost:3000

This allows you to:
1. Compare implementations
2. Test different approaches
3. Learn both Python and Node.js patterns
4. Choose the best solution for your MVP

### Next Steps

1. **SimakoHost Integration**: Implement actual API calls to SimakoHost
2. **Authentication**: Add JWT or API key authentication
3. **WebSocket Support**: Add real-time notifications for dashboards (optional enhancement)
4. **Message Queuing**: Add Redis for message queuing
5. **Monitoring**: Add logging and monitoring
6. **Testing**: Add comprehensive test suites
7. **Docker**: Containerize both backends

### Future Enhancements (Optional)

**WebSocket Support** - Add real-time features:
- Live dashboard updates when SMS arrives
- Real-time notifications to multiple devices
- Instant status updates and alerts
- Multi-device synchronization

*Note: REST API is perfect for your core SMS storage/retrieval needs. WebSockets would be an additional feature for real-time dashboards and notifications.*

## Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running
- Check MONGO_URI in .env files
- Verify network connectivity

### Port Conflicts
- Change ports in .env files if needed
- Check for other services using the same ports

### Dependency Issues
- Update pip/npm to latest versions
- Clear cache if needed: `pip cache purge` or `npm cache clean --force`
