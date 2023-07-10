from flask import Flask, jsonify, request
import json

app = Flask(__name__)

# Endpoint to handle POST requests and store key-value pairs in a JSON file
@app.route('/store', methods=['POST'])
def store_data():
    # Load existing data from the JSON file
    existing_data = {}
    try:
        with open('data.json', 'r') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        pass

    # Get key-value pair from the request body
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')

    # Store the key-value pair in the existing data
    existing_data[key] = value

    # Save the updated data back to the JSON file
    with open('data.json', 'w') as f:
        json.dump(existing_data, f)

    return jsonify({'message': 'Data stored successfully.'})

# Endpoint to handle GET requests and retrieve the JSON file
@app.route('/data', methods=['GET'])
def get_data():
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
            return jsonify(data)
    except FileNotFoundError:
        return jsonify({'message': 'No data found.'})

if __name__ == '__main__':
    app.run(debug=True)
