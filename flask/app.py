# Simako Flask Backend with MongoDB

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'simako_db')

# Initialize MongoDB client with PROPER connection testing
try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    messages_collection = db.messages
    sim_cards_collection = db.sim_cards
    
    # ACTUALLY test the connection by performing a real operation
    client.admin.command('ping')  # This will fail if MongoDB isn't running
    print(f"✅ Successfully connected to MongoDB: {DATABASE_NAME}")
    print(f"📍 MongoDB URI: {MONGO_URI}")
    print(f"🌐 Server info: {client.server_info()['version']}")
    
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    print(f"📍 Attempted URI: {MONGO_URI}")
    print(f"🛠️  Make sure MongoDB is running: mongod")
    client = None
    db = None

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(JSONEncoder, self).default(obj)

# Configure Flask to use our custom JSON encoder
app.json_encoder = JSONEncoder

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with REAL MongoDB connection test"""
    
    # Test ACTUAL MongoDB connection
    mongo_status = "disconnected"
    mongo_error = None
    
    if client is not None:
        try:
            # Perform actual ping to test connection
            client.admin.command('ping')
            mongo_status = "connected"
        except Exception as e:
            mongo_status = "disconnected"
            mongo_error = str(e)
    
    response_data = {
        'status': 'ok',
        'service': 'Simako Flask Backend',
        'mongodb': mongo_status,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Add error details if connection failed
    if mongo_error:
        response_data['mongodb_error'] = mongo_error
        response_data['debug_info'] = {
            'mongo_uri': MONGO_URI,
            'database_name': DATABASE_NAME,
            'suggestion': 'Make sure MongoDB is running: mongod'
        }
    
    return jsonify(response_data)

@app.route('/api/messages', methods=['POST'])
def receive_message():
    """Receive and store SMS/Call messages from SimakoHost"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['sim_id', 'type', 'from', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        message = {
            'sim_id': data.get('sim_id'),
            'type': data.get('type'),  # 'sms' or 'call'
            'from': data.get('from'),
            'to': data.get('to'),
            'message': data.get('message'),
            'timestamp': data.get('timestamp') or datetime.utcnow(),
            'processed': False,
            'metadata': data.get('metadata', {}),
            'created_at': datetime.utcnow()
        }
        
        # Store in MongoDB
        if db is not None:
            result = messages_collection.insert_one(message)
            message['_id'] = str(result.inserted_id)  # Convert ObjectId to string
            
            return jsonify({
                'status': 'ok',
                'message_id': str(result.inserted_id),
                'received': message
            }), 201
        else:
            return jsonify({'error': 'Database connection failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Retrieve messages with optional filtering"""
    try:
        sim_id = request.args.get('sim_id')
        message_type = request.args.get('type')
        limit = int(request.args.get('limit', 100))
        skip = int(request.args.get('skip', 0))
        
        # Build query
        query = {}
        if sim_id:
            query['sim_id'] = sim_id
        if message_type:
            query['type'] = message_type
        
        if db is not None:
            # Get messages with pagination
            cursor = messages_collection.find(query).sort('timestamp', -1).skip(skip).limit(limit)
            messages = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for message in messages:
                message['_id'] = str(message['_id'])
                
            return jsonify({
                'messages': messages,
                'count': len(messages),
                'total': messages_collection.count_documents(query)
            })
        else:
            return jsonify({'error': 'Database connection failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sim-cards', methods=['GET'])
def get_sim_cards():
    """Get list of registered SIM cards"""
    try:
        if db is not None:
            sim_cards = list(sim_cards_collection.find())
            for card in sim_cards:
                card['_id'] = str(card['_id'])
            return jsonify({'sim_cards': sim_cards})
        else:
            return jsonify({'error': 'Database connection failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sim-cards', methods=['POST'])
def register_sim_card():
    """Register a new SIM card"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('sim_id') or not data.get('phone_number'):
            return jsonify({'error': 'sim_id and phone_number are required'}), 400
        
        sim_card = {
            'sim_id': data.get('sim_id'),
            'phone_number': data.get('phone_number'),
            'carrier': data.get('carrier'),
            'is_active': data.get('is_active', True),
            'created_at': datetime.utcnow(),
            'last_seen': datetime.utcnow()
        }
        
        if db is not None:
            # Check if SIM already exists
            existing = sim_cards_collection.find_one({'sim_id': sim_card['sim_id']})
            if existing:
                return jsonify({'error': 'SIM card already registered'}), 409
            
            result = sim_cards_collection.insert_one(sim_card)
            sim_card['_id'] = str(result.inserted_id)
            
            return jsonify({
                'status': 'ok',
                'sim_card': sim_card
            }), 201
        else:
            return jsonify({'error': 'Database connection failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<message_id>/processed', methods=['PUT'])
def mark_message_processed(message_id):
    """Mark a message as processed"""
    try:
        if db is not None:
            result = messages_collection.update_one(
                {'_id': ObjectId(message_id)},
                {'$set': {'processed': True, 'processed_at': datetime.utcnow()}}
            )
            
            if result.matched_count:
                return jsonify({'status': 'ok', 'message': 'Message marked as processed'})
            else:
                return jsonify({'error': 'Message not found'}), 404
        else:
            return jsonify({'error': 'Database connection failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SimakoHost integration endpoints
@app.route('/api/simakohost/status', methods=['GET'])
def simakohost_status():
    """Get status from SimakoHost"""
    return jsonify({
        'status': 'ok',
        'message': 'SimakoHost integration endpoint',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/simakohost/send-sms', methods=['POST'])
def send_sms_via_simakohost():
    """Send SMS through SimakoHost"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['sim_id', 'to', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Here you would integrate with SimakoHost to actually send the SMS
        # For now, we'll just log the request
        sms_request = {
            'sim_id': data.get('sim_id'),
            'to': data.get('to'),
            'message': data.get('message'),
            'status': 'queued',
            'created_at': datetime.utcnow()
        }
        
        # TODO: Integrate with SimakoHost API
        # result = simakohost_client.send_sms(sms_request)
        
        return jsonify({
            'status': 'ok',
            'message': 'SMS queued for sending',
            'request': sms_request
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host=os.getenv('API_HOST', '0.0.0.0'), port=os.getenv('API_PORT', 5000))
