import threading
import time
import requests
import sys
from app import app

def run_server():
    app.run(port=5000, debug=False, use_reloader=False)

def test_server():
    # Start server in a separate thread
    thread = threading.Thread(target=run_server)
    thread.daemon = True
    thread.start()
    
    # Give it a moment to start
    time.sleep(3)
    
    try:
        # Poking the auth login endpoint (expecting 400 or 401, not ConnectionError)
        # We just want to know if it's listening
        response = requests.get('http://127.0.0.1:5000/auth/login')
        print(f"Server responded with status code: {response.status_code}")
        # 405 Method Not Allowed is also fine (since it's a POST endpoint)
        return 0
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the server.")
        return 1
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_server())
