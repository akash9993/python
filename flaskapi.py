from flask import Flask, request, Response, jsonify
import delta_sharing
import pandasql as psql
import requests  # To check Delta Sharing server status
import json
import time
import os

app = Flask(__name__)

# Path to Delta Sharing Profile
PROFILE_FILE = r"/home/ubuntu/project/python/profile.json"

def get_delta_sharing_server_url():
    """Extract endpoint from env var or profile.json"""
    
    try:
        env_url = os.getenv("DELTA_SHARING_ENDPOINT")
        if env_url:
            print("env_url: ",env_url)
            return env_url
        with open(PROFILE_FILE, 'r') as file:
            profile_data = json.load(file)
            return profile_data.get("endpoint")
    except Exception as e:
        print("Exception while getting Delta Sharing endpoint:", e)
        return None

def is_delta_sharing_server_up(server_url, timeout=30):
    """Checks if the Delta Sharing server is up within the specified timeout."""
    if not server_url:
        return False
    
    try:
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = requests.get(server_url+"/shares", timeout=10)
            if response.status_code == 200:
                return True
            time.sleep(1)  # Retry after 1 second
    except requests.RequestException:
        pass
    return False

@app.route('/query-data', methods=['POST'])
def query_data():
    try:
        # Extract Delta Sharing server URL
        server_url = get_delta_sharing_server_url()
        if not server_url:
            return Response("Delta Sharing server URL not found in profile.json.", status=500)
        print(server_url)

        # Check if Delta Sharing server is running
        if not is_delta_sharing_server_up(server_url):
            return Response("Delta Sharing server is down or not running.", status=503)

        # Get parameters from POST request
        request_data = request.get_json()
        if not request_data:
            return Response("Invalid JSON input", status=400)
        
        table_name = request_data.get('tableName')
        query = request_data.get('query')

        if not table_name or not query:
            return Response("Both 'tableName' and 'query' are required.", status=400)

        # Form full table URL
        table_url = f"{PROFILE_FILE}#gold_share.default.{table_name}"

        try:
            # Load data
            data = delta_sharing.load_as_pandas(table_url)
        except Exception:
            return Response(f"'{table_name}' table not found.", status=404)

        try:
            # Execute SQL query on the loaded DataFrame
            result = psql.sqldf(query, {"data": data})
        except Exception:
            return Response("Invalid SQL query.", status=400)

        return jsonify(result.to_dict(orient='records'))

    except Exception:
        return Response("Server error.", status=500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
