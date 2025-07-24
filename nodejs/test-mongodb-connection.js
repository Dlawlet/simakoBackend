// MongoDB Connection Test for Node.js
// Run this to debug MongoDB connection issues

const mongoose = require('mongoose');
require('dotenv').config();

async function testConnection() {
    console.log('🧪 Testing MongoDB Connection...\n');
    
    // Test different connection strings
    const connectionStrings = [
        process.env.MONGO_URI || 'mongodb://localhost:27017/simako_db',
        'mongodb://127.0.0.1:27017/simako_db',
        'mongodb://localhost:27017/simako_db?authSource=admin',
        'mongodb://localhost:27017/simako_db?directConnection=true'
    ];
    
    for (let i = 0; i < connectionStrings.length; i++) {
        const uri = connectionStrings[i];
        console.log(`🔗 Testing connection ${i + 1}/${connectionStrings.length}`);
        console.log(`📍 URI: ${uri}`);
        
        try {
            await mongoose.connect(uri, {
                useNewUrlParser: true,
                useUnifiedTopology: true,
                serverSelectionTimeoutMS: 3000, // Short timeout for testing
            });
            
            console.log('✅ SUCCESS! Connected to MongoDB');
            console.log('📊 Database:', mongoose.connection.db.databaseName);
            console.log('🌐 Host:', mongoose.connection.host);
            console.log('🔌 Port:', mongoose.connection.port);
            console.log('📡 Ready State:', mongoose.connection.readyState);
            
            // Test a simple operation
            const collections = await mongoose.connection.db.listCollections().toArray();
            console.log('📂 Collections:', collections.map(c => c.name));
            
            await mongoose.disconnect();
            console.log('✅ Connection test completed successfully!\n');
            console.log('🎯 Use this URI in your .env file:');
            console.log(`MONGO_URI=${uri}`);
            return;
            
        } catch (error) {
            console.log('❌ FAILED:', error.message);
            await mongoose.disconnect().catch(() => {}); // Silent disconnect
        }
        
        console.log(''); // Empty line for readability
    }
    
    console.log('🚨 All connection attempts failed!');
    console.log('\n🛠️  Troubleshooting Steps:');
    console.log('1. Make sure MongoDB is running:');
    console.log('   Windows: net start MongoDB');
    console.log('   Linux/Mac: sudo systemctl start mongod');
    console.log('   Manual: mongod');
    console.log('');
    console.log('2. Check if MongoDB is listening:');
    console.log('   netstat -an | findstr 27017  (Windows)');
    console.log('   netstat -an | grep 27017     (Linux/Mac)');
    console.log('');
    console.log('3. Try connecting with MongoDB Compass:');
    console.log('   URI: mongodb://localhost:27017');
    console.log('');
    console.log('4. Check MongoDB logs for errors');
    console.log('5. Try different ports: 27017, 27018, 27019');
}

// Run the test
testConnection().catch(console.error);
