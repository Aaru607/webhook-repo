from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['github_webhooks']
collection = db['events']

@app.route('/')
def index():
    """Render the main UI page"""
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming GitHub webhooks"""
    try:
        data = request.json
        event_type = request.headers.get('X-GitHub-Event')
        
        # Process different event types
        if event_type == 'push':
            event_data = process_push_event(data)
        elif event_type == 'pull_request':
            event_data = process_pull_request_event(data)
        else:
            # Just acknowledge other events but don't store them
            return jsonify({'status': 'acknowledged'}), 200
        
        if event_data:
            # Store in MongoDB
            collection.insert_one(event_data)
            return jsonify({'status': 'success', 'message': 'Event stored successfully'}), 200
        
        return jsonify({'status': 'ignored'}), 200
        
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def process_push_event(data):
    """Extract relevant data from push event"""
    try:
        author = data['pusher']['name']
        ref = data['ref']
        branch = ref.split('/')[-1]  # Extract branch name from refs/heads/branch-name
        timestamp = data['head_commit']['timestamp']
        
        return {
            'request_id': data['head_commit']['id'][:7],  # Short commit hash
            'author': author,
            'action': 'PUSH',
            'from_branch': None,
            'to_branch': branch,
            'timestamp': timestamp
        }
    except KeyError as e:
        print(f"Missing key in push event: {e}")
        return None

def process_pull_request_event(data):
    """Extract relevant data from pull request event"""
    try:
        action = data['action']
        
        # Only process 'opened' and 'closed' actions
        if action == 'opened':
            pr_action = 'PULL_REQUEST'
        elif action == 'closed' and data['pull_request'].get('merged', False):
            pr_action = 'MERGE'
        else:
            return None
        
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = data['pull_request']['updated_at']
        
        return {
            'request_id': str(data['pull_request']['id']),
            'author': author,
            'action': pr_action,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
    except KeyError as e:
        print(f"Missing key in pull request event: {e}")
        return None

@app.route('/api/events', methods=['GET'])
def get_events():
    """API endpoint to fetch latest events for UI polling"""
    try:
        # Get the latest 20 events, sorted by timestamp descending
        events = list(collection.find(
            {},
            {'_id': 0}  # Exclude MongoDB's _id field
        ).sort('timestamp', -1).limit(20))
        
        return jsonify(events), 200
    except Exception as e:
        print(f"Error fetching events: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)