import time
import requests
import sys
import urllib3

start = time.time()
since = lambda: time.time() - start
remaining = lambda: 300 - since()

while True:
    if remaining() < 0:
        raise TimeoutError("Wait timeout")

    try:
        response = requests.get("http://server:8000/v1/models", timeout=20) 
        # if that didn't raise an exception, we got through to the server
        print(response)
        break
    except requests.exceptions.RequestException as e:
        print(f"Connection to vLLM server failed with {e}. Retrying for {round(remaining(),1)} more seconds")

    time.sleep(20)

print("vLLM server is up")
