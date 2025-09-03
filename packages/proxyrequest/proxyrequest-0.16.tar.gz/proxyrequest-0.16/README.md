# proxyrequest

`proxyrequest` is a Python package that allows you to make HTTP requests and retrieve HTML content using a proxy. It supports both standard HTTP requests and Selenium-based requests for more dynamic content fetching.

## Features

- **Proxy Support**: Easily integrate proxies into your HTTP requests.
- **HTML Content Retrieval**: Fetch HTML content using requests or Selenium.
- **Selenium Integration**: Use Selenium for dynamic pages when requests alone don't suffice.

## Installation

You can install `proxyrequest` via pip:

```bash
pip install proxyrequest

# ================================================================

from proxyrequest import proxy_verifier
# Checks whether the given proxy is working by making a simple HTTP request to a test URL.

# Define your proxy settings (this is just an example, use a valid proxy IP and port)
proxy = {
    "http": "http://proxy_ip:port",
    "https": "https://proxy_ip:port"
}

proxy = {
    "http": "http://10.10.1.10:3128",
    "https": "https://10.10.1.10:1080"
}

# Call the function with the proxy
is_working = proxy_verifier(proxy)

# Print the result
if is_working:
    print("The proxy is working!")
else:
    print("The proxy is not working.")


# Define custom headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json'
}

# Call the function with custom headers
is_working = proxy_verifier(proxy, headers=headers)

# Print the result
if is_working:
    print("The proxy is working!")
else:
    print("The proxy is not working.")


# Call the function with a custom timeout of 10 seconds
is_working = proxy_verifier(proxy, timeout=10)

# Print the result
if is_working:
    print("The proxy is working!")
else:
    print("The proxy is not working.")


# Call the function with SSL verification disabled
is_working = proxy_verifier(proxy, verify=False)

# Print the result
if is_working:
    print("The proxy is working!")
else:
    print("The proxy is not working.")

# Without Proxy (Direct Request for Public IP)
proxy_verifier(proxy=None)


from proxyrequest import get_request

url = "https://example.com"
response = get_request(url, country="US", protocol="http", max_retries=5)

# Process the response
if response.status_code == 200:
    print("Request was successful!")
    print(response.content)


# Example to fetch and use proxies for multiple requests
from proxyrequest import fetch_proxy_ips, get_request

# Fetch proxies
proxies = fetch_proxy_ips(country="GB", protocol="https", limit=5)

# Example URL
url = "https://httpbin.org/ip"

for proxy in proxies:
    print(f"Using proxy: {proxy['proxy']}")
    response = get_request(url, country="GB", protocol="https")
    if response and response.status_code == 200:
        print(f"Successful response: {response.text}")
    else:
        print("Request failed")

# dynamic content fetching
from proxyrequest import get_chrome_request_driver

driver = get_chrome_request_driver(
    headless=True,
    proxy="http://127.0.0.1:8080",
    window_size="1366,768"
)

if driver:
    driver.get("https://httpbin.org/ip")
    print(driver.page_source)
    driver.quit()


