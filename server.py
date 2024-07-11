from flask import Flask, send_from_directory
import threading

app = Flask(__name__)

@app.route('/payment')
def payment():
    return send_from_directory('.', 'payment/payment.html')

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory('.', path)

def run_server():
    app.run(host='0.0.0.0', port=8000)

if __name__ == '__main__':
    run_server()
