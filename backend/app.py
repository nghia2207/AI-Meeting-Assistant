"""
AI Meeting Assistant - Backend API Server (Python/Flask)
Entry point: Khởi động Flask server và kết nối MongoDB
"""
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timezone
import os
import sys

# Load environment variables
load_dotenv()

# Import routes
from routes.meetings import meetings_bp

# Import config
from config.database import get_database

# Serve static files
import os

app = Flask(__name__, static_folder='static', static_url_path='')

# CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Routes
app.register_blueprint(meetings_bp, url_prefix='/api/meetings')

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

# Dashboard endpoint
@app.route('/', methods=['GET'])
def dashboard():
    from flask import send_from_directory
    return send_from_directory(app.static_folder, 'dashboard.html')

# Error handling
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    print(f'Server error: {e}', file=sys.stderr)
    return jsonify({'error': 'Internal Server Error'}), 500

PORT = int(os.getenv('PORT', 3000))

if __name__ == '__main__':
    try:
        # Connect to MongoDB (optional)
        db = get_database()
        if db:
            print('[OK] MongoDB connected')
        else:
            print('[WARNING] Running with in-memory storage')

        print(f'[OK] Server running on http://localhost:{PORT}')
        app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)

    except Exception as e:
        print(f'Failed to start server: {e}', file=sys.stderr)
        print('[WARNING] Running with in-memory storage instead')
        print(f'[OK] Server running on http://localhost:{PORT}')
        app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)