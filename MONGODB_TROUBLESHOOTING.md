# MongoDB Connection Troubleshooting Guide

## 🚨 Node.js "Connection Refused" Error

### Quick Diagnosis Commands

```bash
# 1. Check if MongoDB is running
netstat -an | findstr 27017    # Windows
netstat -an | grep 27017       # Linux/Mac

# 2. Test connection with Node.js
cd backend/nodejs
node test-mongodb-connection.js

# 3. Check MongoDB status
mongod --version               # Check if MongoDB is installed
mongo --eval "db.stats()"      # Test MongoDB shell connection
```

## 🔍 Common Causes & Solutions

### 1. MongoDB Not Running

**Symptoms**: Connection refused, can't connect to localhost:27017

**Solutions**:

```bash
# Start MongoDB (choose one method):

# Method 1: Windows Service
net start MongoDB

# Method 2: Linux/Mac Service
sudo systemctl start mongod
brew services start mongodb-community  # macOS with Homebrew

# Method 3: Manual Start
mongod

# Method 4: With specific config
mongod --dbpath /path/to/your/data/directory
```

### 2. Wrong MongoDB URI Format

**Python works, Node.js doesn't** - Different URI handling

**Python (Flask)**:

```python
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "simako_db"
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
```

**Node.js (Fixed)**:

```javascript
MONGO_URI = "mongodb://localhost:27017/simako_db";
mongoose.connect(MONGO_URI);
```

### 3. Port Conflicts

**Symptoms**: Port 27017 in use by another service

**Check what's using the port**:

```bash
# Windows
netstat -ano | findstr 27017

# Linux/Mac
lsof -i :27017
```

**Solution**: Use different port

```bash
# Start MongoDB on different port
mongod --port 27018

# Update .env file
MONGO_URI=mongodb://localhost:27018/simako_db
```

### 4. Firewall/Antivirus Blocking

**Symptoms**: Connection timeout, security software blocking

**Solutions**:

- Add MongoDB to firewall exceptions
- Add Node.js to antivirus exceptions
- Temporarily disable firewall/antivirus for testing

### 5. localhost vs 127.0.0.1

**Sometimes localhost resolution fails**

**Try both**:

```bash
# In .env file, try:
MONGO_URI=mongodb://127.0.0.1:27017/simako_db
# Instead of:
MONGO_URI=mongodb://localhost:27017/simako_db
```

## 🛠️ Step-by-Step Fix

### Step 1: Verify MongoDB Installation

```bash
mongod --version
mongo --version
```

### Step 2: Start MongoDB

```bash
# Try each method until one works:
mongod
# OR
net start MongoDB
# OR
sudo systemctl start mongod
```

### Step 3: Test Basic Connection

```bash
# Test with MongoDB shell
mongo
# Should connect without errors
```

### Step 4: Test Node.js Connection

```bash
cd backend/nodejs
node test-mongodb-connection.js
```

### Step 5: Update Connection String

Use the working URI from the test in your `.env` file.

## 🎯 Most Likely Solutions

**For Windows Users**:

1. Start MongoDB service: `net start MongoDB`
2. Use `127.0.0.1` instead of `localhost`
3. Check Windows Defender/antivirus

**For Linux/Mac Users**:

1. Start MongoDB: `sudo systemctl start mongod`
2. Check permissions on MongoDB data directory
3. Verify MongoDB is installed via package manager

**For Docker Users**:

```bash
# Start MongoDB container
docker run --name mongodb -p 27017:27017 -d mongo:latest

# Update .env
MONGO_URI=mongodb://localhost:27017/simako_db
```

## 🔍 Advanced Debugging

### Enable MongoDB Logs

```bash
# Start MongoDB with verbose logging
mongod --verbose --logpath /tmp/mongodb.log
```

### Test with Different Drivers

```javascript
// Test with native MongoDB driver instead of Mongoose
const { MongoClient } = require("mongodb");

async function testNativeConnection() {
  try {
    const client = new MongoClient("mongodb://localhost:27017");
    await client.connect();
    console.log("Native driver connection successful!");
    await client.close();
  } catch (error) {
    console.error("Native driver failed:", error.message);
  }
}
```

## ✅ Success Indicators

When working, you should see:

```
🔗 Attempting MongoDB connection...
📍 MongoDB URI: mongodb://localhost:27017/simako_db
✅ Connected to MongoDB successfully
📊 Database: simako_db
🌐 Host: localhost
🔌 Port: 27017
```

## 🆘 Still Not Working?

1. **Check process list**: Is `mongod` running?
2. **Check ports**: `netstat -an | findstr 27017`
3. **Try MongoDB Compass**: GUI tool to test connection
4. **Check MongoDB data directory**: Permissions and disk space
5. **Restart computer**: Sometimes fixes network/port issues
6. **Try different MongoDB version**: Install latest stable version
