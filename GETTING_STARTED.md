# 🚀 Simako Backend Quick Start Guide

This guide will help you get both Flask and Node.js backends running with MongoDB integration.

## Prerequisites Check ✅

Before starting, ensure you have:

- [ ] **Python 3.8+** installed (`python --version`)
- [ ] **Node.js 16+** installed (`node --version`)
- [ ] **MongoDB** installed and running (`mongod --version`)
- [ ] **Git** for version control

## Option 1: Docker Setup (Recommended for beginners) 🐳

The easiest way to run everything:

```bash
# Navigate to backend directory
cd backend

# Start all services (MongoDB + both backends)
docker-compose up -d

# Check if everything is running
docker-compose ps
```

This will start:
- MongoDB on port 27017
- Flask backend on port 5000
- Node.js backend on port 3000
- MongoDB Express UI on port 8081

## Option 2: Manual Setup (Recommended for learning) 🛠️

### Step 1: Start MongoDB

```bash
# Start MongoDB service
mongod

# Or if using MongoDB as a service
net start MongoDB  # Windows
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # macOS
```

### Step 2: Setup Flask Backend

```bash
cd backend

# Windows
setup-flask.bat

# Linux/macOS
chmod +x setup-flask.sh
./setup-flask.sh

# Manual setup (if scripts don't work)
cd flask
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python app.py
```

Flask will be available at: http://localhost:5000

### Step 3: Setup Node.js Backend (in new terminal)

```bash
cd backend

# Windows
setup-nodejs.bat

# Linux/macOS
chmod +x setup-nodejs.sh
./setup-nodejs.sh

# Manual setup (if scripts don't work)
cd nodejs
npm install
npm run dev
```

Node.js will be available at: http://localhost:3000

## Testing Your Setup 🧪

### Quick Health Check

Open these URLs in your browser:
- Flask: http://localhost:5000/health
- Node.js: http://localhost:3000/health
- MongoDB Express: http://localhost:8081 (if using Docker)

### Run Comprehensive Tests

```bash
cd backend
pip install requests  # If not already installed
python test_backends.py
```

### Manual API Testing

#### Register a SIM Card (Flask)
```bash
curl -X POST http://localhost:5000/api/sim-cards \
  -H "Content-Type: application/json" \
  -d '{
    "sim_id": "SIM001",
    "phone_number": "+1234567890",
    "carrier": "Test Carrier"
  }'
```

#### Send a Message (Node.js)
```bash
curl -X POST http://localhost:3000/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "sim_id": "SIM001",
    "type": "sms",
    "from": "+1234567890",
    "message": "Hello from Simako!"
  }'
```

#### Get Messages (Both)
```bash
# Flask
curl http://localhost:5000/api/messages

# Node.js
curl http://localhost:3000/api/messages
```

## Next Steps 🎯

### For Learning Python/Flask:
1. Explore `backend/flask/app.py`
2. Try adding new endpoints
3. Experiment with MongoDB queries
4. Add validation and error handling

### For Learning Node.js/Express:
1. Explore `backend/nodejs/server.js`
2. Try adding middleware
3. Experiment with Mongoose schemas
4. Add authentication

### For Production MVP:
1. Choose your preferred backend (Node.js recommended for scalability)
2. Add proper authentication (JWT)
3. Implement rate limiting
4. Add comprehensive logging
5. Set up monitoring

## SimakoHost Integration 🔗

Both backends have placeholder endpoints for SimakoHost integration:
- `GET /api/simakohost/status`
- `POST /api/simakohost/send-sms`

To integrate with your actual SimakoHost:
1. Update the `.env` files with your SimakoHost URL and API key
2. Implement the actual API calls in the send-sms endpoints
3. Add webhook endpoints for receiving messages from SimakoHost

## Troubleshooting 🔧

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
mongod --version
netstat -an | findstr 27017  # Windows
netstat -an | grep 27017     # Linux/macOS
```

### Port Already in Use
```bash
# Find process using port
netstat -ano | findstr 5000  # Windows
lsof -i :5000                # Linux/macOS

# Kill process if needed
taskkill /PID <PID> /F       # Windows
kill -9 <PID>                # Linux/macOS
```

### Python Virtual Environment Issues
```bash
# Recreate virtual environment
cd backend/flask
rmdir /s venv     # Windows
rm -rf venv       # Linux/macOS
python -m venv venv
```

### Node.js Module Issues
```bash
cd backend/nodejs
rm -rf node_modules package-lock.json
npm install
```

## Development Workflow 💻

1. **Start MongoDB** (once)
2. **Run both backends** in separate terminals
3. **Test changes** using the test script or curl commands
4. **Monitor logs** for errors and debugging
5. **Use MongoDB Express** to inspect database changes

## Environment Variables 📋

### Flask (.env)
```
MONGO_URI=mongodb://localhost:27017/
DATABASE_NAME=simako_db
FLASK_ENV=development
SIMAKOHOST_API_URL=http://localhost:8080
```

### Node.js (.env)
```
MONGO_URI=mongodb://localhost:27017/simako_db
NODE_ENV=development
PORT=3000
SIMAKOHOST_API_URL=http://localhost:8080
```

## Support 📞

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Check firewall and antivirus settings
4. Review the logs for specific error messages

Happy coding! 🎉
