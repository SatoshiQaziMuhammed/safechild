import requests

def test_health_check():
    """
    Tests if the backend service is running and responding to basic requests.
    """
    try:
        response = requests.get("http://localhost:8001/")
        # We expect a 404 Not Found if no root endpoint is defined, which is still a success.
        # A successful connection means the server is alive.
        # A 200 is also acceptable.
        assert response.status_code in [200, 404]
    except requests.exceptions.ConnectionError as e:
        assert False, f"Backend service is not reachable at http://localhost:8001/. Is it running? Error: {e}"

