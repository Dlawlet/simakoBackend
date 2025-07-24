// Simako Node.js Backend with MongoDB

// Suppress specific punycode deprecation warning (DEP0040)
process.removeAllListeners('warning');
process.on('warning', (warning) => {
  if (warning.name === 'DeprecationWarning' && warning.code === 'DEP0040') {
    return; // Ignore punycode deprecation
  }
  console.warn(warning.name + ': ' + warning.message);
});

const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');
const Joi = require('joi'); // Validation middleware
require('dotenv').config();

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api/', limiter);

// MongoDB connection with better error handling and debugging
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/simako_db';

console.log('🔗 Attempting MongoDB connection...');
console.log('📍 MongoDB URI:', MONGO_URI);

mongoose.connect(MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
  // Add these options to help with connection issues
  serverSelectionTimeoutMS: 5000, // Keep trying to send operations for 5 seconds
  socketTimeoutMS: 45000, // Close sockets after 45 seconds of inactivity
  maxPoolSize: 10, // Maintain up to 10 socket connections
})
.then(() => {
  console.log('✅ Connected to MongoDB successfully');
  console.log('📊 Database:', mongoose.connection.db.databaseName);
  console.log('🌐 Host:', mongoose.connection.host);
  console.log('🔌 Port:', mongoose.connection.port);
})
.catch((error) => {
  console.error('❌ MongoDB connection error:', error.message);
  console.error('🔍 Full error details:', error);
  
  // Don't exit immediately, try to provide helpful debug info
  console.log('\n🛠️  Debug Information:');
  console.log('📍 URI being used:', MONGO_URI);
  console.log('💻 Make sure MongoDB is running: mongod');
  console.log('🌐 Check if port 27017 is available');
  console.log('🔒 Check firewall/antivirus settings');
  
  process.exit(1);
});

// Add connection event listeners for better debugging
mongoose.connection.on('error', (error) => {
  console.error('🚨 MongoDB connection error:', error);
});

mongoose.connection.on('disconnected', () => {
  console.log('🔌 MongoDB disconnected');
});

mongoose.connection.on('reconnected', () => {
  console.log('🔄 MongoDB reconnected');
});

// MongoDB Schemas
const messageSchema = new mongoose.Schema({
  sim_id: { type: String, required: true, index: true },
  type: { type: String, required: true, enum: ['sms', 'call'] },
  from: { type: String, required: true },
  to: { type: String },
  message: { type: String, required: true },
  timestamp: { type: Date, default: Date.now, index: true },
  processed: { type: Boolean, default: false },
  processed_at: { type: Date },
  metadata: { type: mongoose.Schema.Types.Mixed, default: {} },
  created_at: { type: Date, default: Date.now }
});

const simCardSchema = new mongoose.Schema({
  sim_id: { type: String, required: true, unique: true },
  phone_number: { type: String, required: true },
  carrier: { type: String },
  is_active: { type: Boolean, default: true },
  created_at: { type: Date, default: Date.now },
  last_seen: { type: Date, default: Date.now }
});

// Models
const Message = mongoose.model('Message', messageSchema);
const SimCard = mongoose.model('SimCard', simCardSchema, 'sim_cards'); // Force collection name to match Flask

const messageValidation = Joi.object({
  sim_id: Joi.string().required(),
  type: Joi.string().valid('sms', 'call').required(),
  from: Joi.string().required(),
  to: Joi.string(),
  message: Joi.string().required(),
  timestamp: Joi.date(),
  metadata: Joi.object()
});

const simCardValidation = Joi.object({
  sim_id: Joi.string().required(),
  phone_number: Joi.string().required(),
  carrier: Joi.string(),
  is_active: Joi.boolean()
});

// Routes

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'Simako Node.js Backend',
    mongodb: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
    timestamp: new Date().toISOString()
  });
});

// Messages endpoints
app.post('/api/messages', async (req, res) => {
  try {
    // Validate request body
    const { error, value } = messageValidation.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    // Create message
    const message = new Message({
      ...value,
      timestamp: value.timestamp || new Date()
    });

    const savedMessage = await message.save();

    res.status(201).json({
      status: 'ok',
      message_id: savedMessage._id,
      received: savedMessage
    });

  } catch (error) {
    console.error('Error saving message:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/messages', async (req, res) => {
  try {
    const { sim_id, type, limit = 100, skip = 0 } = req.query;

    // Build query
    const query = {};
    if (sim_id) query.sim_id = sim_id;
    if (type) query.type = type;

    // Get messages with pagination
    const messages = await Message.find(query)
      .sort({ timestamp: -1 })
      .skip(parseInt(skip))
      .limit(parseInt(limit));

    const total = await Message.countDocuments(query);

    res.json({
      messages,
      count: messages.length,
      total
    });

  } catch (error) {
    console.error('Error fetching messages:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.put('/api/messages/:messageId/processed', async (req, res) => {
  try {
    const { messageId } = req.params;

    const message = await Message.findByIdAndUpdate(
      messageId,
      { 
        processed: true, 
        processed_at: new Date() 
      },
      { new: true }
    );

    if (!message) {
      return res.status(404).json({ error: 'Message not found' });
    }

    res.json({
      status: 'ok',
      message: 'Message marked as processed',
      data: message
    });

  } catch (error) {
    console.error('Error updating message:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// SIM Cards endpoints
app.get('/api/sim-cards', async (req, res) => {
  try {
    const sim_Cards = await SimCard.find();
    res.json({ sim_cards: sim_Cards });
  } catch (error) {
    console.error('Error fetching SIM cards:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/sim-cards', async (req, res) => {
  try {
    // Validate request body
    const { error, value } = simCardValidation.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    // Check if SIM already exists
    const existingSim = await SimCard.findOne({ sim_id: value.sim_id });
    if (existingSim) {
      return res.status(409).json({ error: 'SIM card already registered' });
    }

    // Create SIM card
    const simCard = new SimCard(value);
    const savedSimCard = await simCard.save();

    res.status(201).json({
      status: 'ok',
      sim_card: savedSimCard
    });

  } catch (error) {
    console.error('Error saving SIM card:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// SimakoHost integration endpoints
app.get('/api/simakohost/status', (req, res) => {
  res.json({
    status: 'ok',
    message: 'SimakoHost integration endpoint',
    timestamp: new Date().toISOString()
  });
});

app.post('/api/simakohost/send-sms', async (req, res) => {
  try {
    const { sim_id, to, message } = req.body;

    // Validate required fields
    if (!sim_id || !to || !message) {
      return res.status(400).json({ 
        error: 'Missing required fields: sim_id, to, message' 
      });
    }

    // Here you would integrate with SimakoHost to actually send the SMS
    // For now, we'll just log the request
    const smsRequest = {
      sim_id,
      to,
      message,
      status: 'queued',
      created_at: new Date()
    };

    // TODO: Integrate with SimakoHost API
    // const axios = require('axios');
    // const response = await axios.post(`${process.env.SIMAKOHOST_API_URL}/send-sms`, smsRequest);

    res.status(202).json({
      status: 'ok',
      message: 'SMS queued for sending',
      request: smsRequest
    });

  } catch (error) {
    console.error('Error sending SMS:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Start server
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

app.listen(PORT, HOST, () => {
  console.log(`Simako Node.js Backend running on http://${HOST}:${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});
