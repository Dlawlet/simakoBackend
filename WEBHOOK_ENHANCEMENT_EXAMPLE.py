# Future Webhook Enhancement Example

# This would be added to your Flask backend if you want webhook notifications

from typing import List
import requests
import asyncio

# Webhook configuration (would be stored in database)
webhook_subscribers = [
    {
        'id': 'dashboard',
        'url': 'http://dashboard.example.com/webhook/sms',
        'events': ['sms_received', 'call_received'],
        'active': True
    },
    {
        'id': 'crm_system',
        'url': 'http://crm.example.com/api/webhook',
        'events': ['sms_received'],
        'active': True
    }
]

async def send_webhook_notification(event_type: str, data: dict):
    """Send webhook notifications to subscribed services"""
    for subscriber in webhook_subscribers:
        if (subscriber['active'] and 
            event_type in subscriber['events']):
            
            webhook_payload = {
                'event': event_type,
                'timestamp': datetime.utcnow().isoformat(),
                'data': data
            }
            
            try:
                response = requests.post(
                    subscriber['url'],
                    json=webhook_payload,
                    timeout=5,
                    headers={'Content-Type': 'application/json'}
                )
                print(f"Webhook sent to {subscriber['id']}: {response.status_code}")
            except Exception as e:
                print(f"Webhook failed for {subscriber['id']}: {e}")

# Modified message endpoint with webhook notifications
@app.route('/api/messages', methods=['POST'])
def receive_message_with_webhooks():
    """Enhanced version that sends webhook notifications"""
    # ... existing message processing code ...
    
    # After saving to MongoDB, send webhook notifications
    if result.inserted_id:
        event_type = 'sms_received' if message['type'] == 'sms' else 'call_received'
        
        # Send webhooks asynchronously (don't block the API response)
        asyncio.create_task(
            send_webhook_notification(event_type, message)
        )
        
        return jsonify({
            'status': 'ok',
            'message_id': str(result.inserted_id),
            'webhooks_triggered': True
        }), 201
