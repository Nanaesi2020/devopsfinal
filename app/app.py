from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to Wild Rydes!',
        'service': 'Wild Rydes Monolithic Application',
        'version': '1.0.0',
        'hostname': socket.gethostname(),
        'status': 'healthy'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'wild-rydes',
        'hostname': socket.gethostname()
    }), 200

@app.route('/about')
def about():
    return jsonify({
        'company': 'Wild Rydes',
        'description': 'The fastest way to get a ride on a unicorn',
        'technology': 'ECS Fargate with Python Flask'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)
