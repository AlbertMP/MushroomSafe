from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/images', methods=['POST'])
def images():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    # Receive for further processing
    print(file)
    return 'File uploaded successfully'

if __name__ == '__main__':
    app.run(debug=True)
