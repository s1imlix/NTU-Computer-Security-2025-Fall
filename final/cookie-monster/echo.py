from flask import Flask, request
from urllib.parse import unquote

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def reflect(path):
    # unquote converts %7b to { and %7d to }
    decoded_payload = unquote(path)
    print(f"Delivering payload: {decoded_payload}")
    return decoded_payload

if __name__ == '__main__':
    # Use port 80 or 5000 depending on your environment
    app.run(host='0.0.0.0', port=5000)
