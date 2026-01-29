from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os

# Load .env ONLY when running locally
if os.environ.get("RENDER") is None:
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection (local + Render)
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable not set")

client = MongoClient(MONGO_URI)
db = client["github_webhooks"]
collection = db["events"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        event_type = request.headers.get('X-GitHub-Event')

        if event_type == 'push':
            event_data = process_push_event(data)
        elif event_type == 'pull_request':
            event_data = process_pull_request_event(data)
        else:
            return jsonify({'status': 'acknowledged'}), 200

        if event_data:
            collection.insert_one(event_data)
            return jsonify({'status': 'success'}), 200

        return jsonify({'status': 'ignored'}), 200

    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def process_push_event(data):
    try:
        author = data['pusher']['name']
        branch = data['ref'].split('/')[-1]
        timestamp = data['head_commit']['timestamp']

        return {
            'request_id': data['head_commit']['id'][:7],
            'author': author,
            'action': 'PUSH',
            'from_branch': None,
            'to_branch': branch,
            'timestamp': timestamp
        }
    except KeyError:
        return None

def process_pull_request_event(data):
    try:
        action = data['action']

        if action == 'opened':
            pr_action = 'PULL_REQUEST'
        elif action == 'closed' and data['pull_request'].get('merged'):
            pr_action = 'MERGE'
        else:
            return None

        return {
            'request_id': str(data['pull_request']['id']),
            'author': data['pull_request']['user']['login'],
            'action': pr_action,
            'from_branch': data['pull_request']['head']['ref'],
            'to_branch': data['pull_request']['base']['ref'],
            'timestamp': data['pull_request']['updated_at']
        }
    except KeyError:
        return None

@app.route('/api/events', methods=['GET'])
def get_events():
    try:
        events = list(
            collection.find({}, {'_id': 0})
            .sort('timestamp', -1)
            .limit(20)
        )
        return jsonify(events), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
