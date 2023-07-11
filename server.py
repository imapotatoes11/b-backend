from flask import Flask, jsonify, request
import json, time, os, requests
from log_client import Log

LOCALAUTH = os.environ.get("LOCALAUTH")

# confirm environment variable is active
if LOCALAUTH is None or LOCALAUTH == "None":
    assert (
        False, "The environment variable is not active.")

app = Flask(__name__)
log = Log('142.198.243.59', 1018, log=True)

# Endpoint to handle POST requests and store key-value pairs in a JSON file
@app.route('/store', methods=['POST'])
def store_data():
    start = time.time()
    log.info("-" * 25)
    log.info("POST request received for store")

    # Load existing data from the JSON file
    log.info("DAT > Loading existing data from JSON file")
    existing_data = {}

    # attempt to get data from backup server
    try:
        log.info("DAT > LOC > Attempting to get data from backup server...")
        r = requests.get("http://142.198.243.59:1017/data", headers = {"Authentication": LOCALAUTH})
        if r.status_code == 200:
            log.info("DAT > LOC > FOU > Existing data found from backup, loading into memory...")
            existing_data = r.json()
    except Exception as e:
        log.error(f"DAT > LOC > ERR > The request failed: {e}")

    try:
        with open('data.json', 'r') as f:
            existing_data = json.load(f)
            log.info("DAT > FOU > Existing data found, loading into memory...")
    except FileNotFoundError:
        log.info("DAT > NON > No existing data found")
    log.info("DAT > Existing data loaded")

    # Get key-value pair from the request body
    log.info("KEY > Getting key-value pair from request body and storing data...")
    try:
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
    except Exception as e: log.error(f"KEY > ERR > The request body failed: {e}")

    # Store the key-value pair in the existing data
    log.info("STOR > Storing key-value pair into data")
    existing_data[key] = value

    log.info("SAVE > Saving data to JSON file")
    # Save the updated data back to the JSON file
    with open('data.json', 'w') as f:
        json.dump(existing_data, f)
        log.info("KEY > Data stored successfully")

    end = time.time()

    # repeat the request to locally mirrored server
    log.info("BAC > Repeating request to local server...")
    try:
        req = requests.post("142.198.243.59:1017", headers = {"Authentication": LOCALAUTH, "Content-Type": "application/json"}, data=data)
        if req.status_code == 200:
            log.info("BAC > POST > SUCC > The data was synced successfully!")
        else:
            log.warning(f"BAC > POST > WARN > Data failed to sync, HTTP error {req.status_code}")
    except Exception as e:
        log.error(f"BAC > ERR > The request failed: {e}")

    log.info("POST complete! Return message: " + str({'message': 'Data stored successfully.', 'stats': {'response_time': end-start}}))
    return jsonify({'message': 'Data stored successfully.', 'stats': {'response_time': end-start}})

# Endpoint to handle GET requests and retrieve the JSON file
@app.route('/data', methods=['GET'])
def get_data():
    start = time.time()
    log.info("-" * 25)
    log.info("GET request received for data")
    try:
        log.info("RET > Attempting to retrieve data...")
        with open('data.json', 'r') as f:
            data = json.load(f)
            end = time.time()
            # append stats to data
            data['stats'] = {'response_time': end-start}
            log.info(f"RET > SUCC > Data retrieval success! Response time was {round(end-start,3)} seconds")
            return jsonify(data)
    except FileNotFoundError:
        end = time.time()
        log.info("RET > ERR > The file was not found, returning the following json:")
        log.info("            " + str({'message': 'No data found.', 'stats': {'response_time': end-start}}))
        return jsonify({'message': 'No data found.', 'stats': {'response_time': end-start}})
    
# Return a simple html page with modern css that just confirms the site works
@app.route('/', methods=['GET'])
def index():
    start = time.time()
    log.info("-" * 25)
    log.info("GET request received for INDEX")
    log.info("GET > Status nominal")
    try: dat = "\n".join([i for i in open("data.json", "r").read()])
    except Exception: dat = "No data found"
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
                .code_snippet {"{"}
                        background-color: #f2f2f2;
                        border-radius: 10px;
                        padding: 10px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.2);
                        font-family: monospace;
                        margin-top: 20px;
                        max-width: 500px;
                        overflow: auto;
                    {"}"}
            </style>
        </head>
        <body>
            <div class="divv">
                <h1>Status</h1>
                <p>Backend is running!</p>
                <p>Response time: {time.time() - start}</p>
                <p>Data:</p>
                <p class="code_snippet">{dat}</p>
            </div>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=False)
