# proxyrequest/utils.py
# === Standard Library Imports ===
import re
import os
import random
import time
import json
import traceback
from datetime import datetime, timezone
from mimetypes import guess_extension
from typing import Optional, Union, Dict
from urllib.parse import urlparse

# === Third-Party Imports ===
import requests
import tldextract
import filetype
from fake_useragent import UserAgent
from fake_useragent.errors import FakeUserAgentError

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from typing import *

def standardized_string(string: Optional[str] = None) -> str:
    """
    Standardizes a string by:
    - Replacing `\n`, `\t`, and `\r` with spaces.
    - Removing HTML tags.
    - Replacing multiple spaces with a single space.
    - Stripping leading/trailing spaces.

    Args:
    - string (str, optional): The string to be standardized. Defaults to None.

    Returns:
    - str: The standardized string, or an empty string if input is None.
    """
    old_string = string
    if string is None:
        return ""
    if not isinstance(string, str):
        string = str(string)

    # Fix encoding issues (mojibake)
    try:

        string = string.replace("\\n", " ").replace("\\t", " ").replace("\\r", " ")
        string = re.sub(r"<.*?>", " ", string)  # Remove HTML tags
        string = re.sub(r"\s+", " ", string)  # Collapse multiple spaces into one
        string = string.strip()  # Strip leading/trailing spaces
        return string
    except:
        return old_string

def proxy_verifier(proxy: Optional[Dict[str, str]] = None, url: str = "http://httpbin.org/ip", timeout: int = 5, headers: Optional[Dict[str, str]] = None, verify: bool = True) -> bool:
    """
    Checks whether the given proxy is working by making a simple HTTP request to a test URL.
    If no proxy is provided, it fetches the public IP directly.

    Args:
        proxy (dict, optional): The proxy configuration (e.g., {"http": "http://proxy_ip:port", "https": "https://proxy_ip:port"}). Default is None.
        url (str): The URL to test the proxy against. Default is http://httpbin.org/ip.
        timeout (int): The timeout value for the request in seconds. Default is 5 seconds.
        headers (dict, optional): Custom headers to be sent with the request. Default is None, which sends a standard User-Agent.
        verify (bool, optional): Whether to verify SSL certificates. Default is True. Set to False if you want to skip SSL verification.

    Returns:
        bool: True if the proxy is working, False otherwise.
    """
    # If no proxy is provided, default to an empty dictionary
    if proxy is None:
        proxy = {}

    # If no custom headers are provided, use a default User-Agent header
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    try:
        # If no proxy is given, get the public IP directly
        if not proxy:
            print(url)
            response = requests.get(url, headers=headers, timeout=timeout, verify=verify)
        else:
            # Sending a GET request to the test URL using the proxy, custom headers, timeout, and SSL verification
            response = requests.get(url, proxies=proxy, headers=headers, timeout=timeout, verify=verify)
        
        # If the status code is 200, the proxy is working or we got the IP
        if response.status_code == 200:
            if not proxy:
                # If no proxy, just print and return the public IP
                public_ip = response.json().get("origin", "Unknown")
                print(f"Public IP is used: {public_ip}")
                return True
            else:
                # If proxy was used, print success
                print(f"Proxy {proxy} is working!")
                return True
        else:
            print(f"Failed with status code {response.status_code}")
            return False    

    except requests.exceptions.ConnectTimeout:
        print(f"Error: timeout")
        return False

    except requests.exceptions.ConnectionError:
        print(f"Error: check net connections")
        return False

    except requests.exceptions.SSLError:
        print(f"Error: certificate verify failed (SSL)")
        return False

    except requests.exceptions.JSONDecodeError:
        print(f"Error: decoding JSON")
        return False

    except requests.exceptions.ReadTimeout:
        print(f"Error: ReadTimeout")
        return False        

    except Exception as error:
        print(error)
        return False 


def get_base_domain(url: str) -> Optional[str]:
    """
    Extracts the registered base domain from a given URL using tldextract.

    Args:
        url (str): The full URL or hostname.

    Returns:
        Optional[str]: The base domain (e.g., 'example.com', 'example.co.uk'),
                       or None if it cannot be extracted.

    Examples:
        >>> get_base_domain("https://sub.example.co.uk/path")
        'example.co.uk'

        >>> get_base_domain("example.com")
        'example.com'

        >>> get_base_domain("invalid_url")
        None
    """
    if not isinstance(url, str) or not url.strip():
        print("Invalid input: URL must be a non-empty string.")
        return None

    try:
        # Normalize the URL
        parsed_url = urlparse(url.strip())
        netloc = parsed_url.netloc or parsed_url.path  # handle URLs without scheme

        extracted = tldextract.extract(netloc)
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}"
        else:
            print(f"Could not extract base domain from: {url}")
            return None
    except Exception as e:
        print(f"Error extracting base domain from URL '{url}': {e}")
        return None

def get_header(referer:str = "", authority:str=""):
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54'
    ]
    user_agent = random.choice(user_agent_list)

    headers = {
        'Authority': authority,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
        'Cache-Control': 'no-cache',
        'Accept-Encoding': 'gzip, deflate, br',
        'Pragma': 'no-cache',
        'Referer': referer,
        'Sec-CH-UA': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent
    }

    return headers

def fetch_proxy_ips(country:str="all",protocol:str="http",port:int=None,limit:int=None):
    """
    Displays the details of the proxies fetched from the API.

    Args:
        proxies (Optional[list]): List of proxies to display. Each proxy is a dictionary.
    """
    API_URL = f"https://api.proxyscrape.com/v4/free-proxy-list/get?request=displayproxies&protocol={protocol}&timeout=10000&country={country}&ssl=all&anonymity=all&skip=0&limit=2000&proxy_format=ipport&format=json"
    try:
        response = get_request(url=API_URL, proxy=False)
        proxies = response.json()
        
        if proxies is None:
            print("No proxies available.")
            return

        data_list = list()
        for idx, proxy in enumerate(proxies.get("proxies",""), start=1):
            data_dict = dict()

            ip = proxy.get("ip")
            json_port = proxy.get("port")
            ssl = proxy.get("ssl")
            protocol = proxy.get("protocol")
            uptime = proxy.get("uptime")
            uptime = f"{uptime:.2f}%"
            last_update = proxy.get("ip_data_last_update")
            last_update = datetime.fromtimestamp(last_update, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

            as_name = proxy.get("ip_data", {}).get("as", "")
            asname = proxy.get("ip_data", {}).get("asname", "")
            isp = proxy.get("ip_data", {}).get("isp", "")
            lat = proxy.get("ip_data", {}).get("lat", "")
            lon = proxy.get("ip_data", {}).get("lon", "")
            country = proxy.get("ip_data", {}).get("country", "Unknown")

            if port is None:
                data_dict["ip"] = ip
                data_dict["port"] = json_port
                data_dict["proxy"] = f"{ip}:{json_port}"
                data_dict["protocol"] = protocol
                data_dict["uptime"] = uptime
                data_dict["last_update"] = last_update
                data_dict["as"] = as_name
                data_dict["asname"] = asname
                data_dict["isp"] = isp
                data_dict["lat"] = lat
                data_dict["lon"] = lon
                data_dict["country"] = country
                data_list.append(data_dict)
            
            else:
                if port == json_port:
                    data_dict["ip"] = ip
                    data_dict["port"] = json_port
                    data_dict["proxy"] = f"{ip}:{json_port}"
                    data_dict["protocol"] = protocol
                    data_dict["uptime"] = uptime
                    data_dict["last_update"] = last_update
                    data_dict["as"] = as_name
                    data_dict["asname"] = asname
                    data_dict["isp"] = isp
                    data_dict["lat"] = lat
                    data_dict["lon"] = lon
                    data_dict["country"] = country
                    data_list.append(data_dict)

        if limit is None:
            return data_list
        return data_list[:limit]
    
    except Exception as e:
        print(e)

def get_request(url, max_retries=5, header=None, country:str="all", protocol:str="http", port:int=None, proxy:bool=True):
    if "api.proxyscrape.com" not in url:
        print(f"Request:{url}")
    request_obj = None
    attempts = 0

    while attempts < max_retries:
        attempts += 1
        
        if proxy:
            if "api.proxyscrape.com" not in url:
                proxies = fetch_proxy_ips(country=country,protocol=protocol, port=port)
                proxy_list = [item.get("proxy") for item in proxies]
                proxy_ele = random.choice(proxy_list)
                proxy_dict = {"http": f"http://{proxy_ele}", "https": f"http://{proxy_ele}"}

            if header is None:
                domain_url = get_base_domain(url = url)
                header = get_header(referer = domain_url, authority = domain_url)

        try:
            time.sleep(random.randint(3, 7))
            if proxy:
                print(f"[Attempt {attempts}] Using proxy: {proxy_ele}")
                request_obj = requests.get(url, headers=header, proxies=proxy_dict, timeout=10)
            elif not proxy:
                request_obj = requests.get(url, timeout=10)

        except (requests.exceptions.SSLError, requests.exceptions.ProxyError, requests.exceptions.ConnectTimeout) as e:
            try:
                time.sleep(random.randint(3, 7))
                if proxy:
                    request_obj = requests.get(url, headers=header, proxies=proxy_dict, verify=False, timeout=15)
                elif not proxy:
                    request_obj = requests.get(url, verify=False, timeout=15)
            except Exception as e:
                continue
        
        except requests.exceptions.ConnectionError as error:
            print("Check Net Connection")
            continue

        except Exception as e:
            print(f"Unexpected error: {e}")
            continue

        if request_obj and request_obj.status_code == 200:
            if "api.proxyscrape.com" not in url:
                print(f"Response:{request_obj.status_code}")
            return request_obj
        else:
            print(f"Request failed with status: {request_obj.status_code if request_obj else 'No response'}")
            print("Re-trying...")

    print(f"Failed to get a successful response after {max_retries} attempts.")


def browser_wait(driver: WebDriver, wait_time: int = 5, element_selector: Optional[str] = "body"):
    if not driver or not element_selector:
        return
    try:
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, element_selector))
        )
    except Exception as e:
        print(f"Browser_wait Error: {e}")


def java_script_click(
    driver: WebDriver,
    css_selector: Optional[str] = None,
    java_script: Optional[str] = None,
    timeout: int = 10
) -> bool:
    """
    Waits for an element and clicks it using JavaScript.

    Parameters:
        driver (WebDriver): The Selenium WebDriver instance.
        css_selector (str, optional): CSS selector of the element to click. Ignored if `java_script` is provided.
        java_script (str, optional): Custom JavaScript to execute. If provided, takes precedence over css_selector.
        timeout (int): Maximum wait time in seconds for the element (applies only to css_selector).

    Returns:
        bool: True if the click was successful, False otherwise.
    """
    if driver is None or (not css_selector and not java_script):
        return False  # Invalid input

    try:
        if java_script:
            # Run the custom JS directly
            driver.execute_script(java_script)
        else:
            # Wait until the element is present in the DOM
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
            )
            # Escape the selector safely for JS
            safe_selector = json.dumps(css_selector)
            # Run JS click
            driver.execute_script(f"document.querySelector({safe_selector}).click();")
        return True
    except Exception as e:
        print(f"java_script_click Error: {e}")
        return False


def random_delay(min_delay: float = 1.5, max_delay: float = 3.0):
    """Injects a random delay to simulate human hesitation."""
    delay = random.uniform(min_delay, max_delay)
    # print(f"Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)


def random_click(driver: WebDriver, element_selector: str):
    """Injects a random mouse click on a selected element."""
    try:
        element = driver.find_element(By.CSS_SELECTOR, element_selector)
        actions = ActionChains(driver)
        actions.move_to_element(element).click().perform()
        random_delay(min_delay=0.5, max_delay=1.5)  # Delay after click
        print(f"Clicked on {element_selector}")
    except Exception as e:
        print(f"Error during click: {e}")


def random_scroll(driver: WebDriver):
    """Simulates scrolling behavior by scrolling to a random position on the page."""
    try:
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        random_scroll_position = random.randint(0, scroll_height)
        driver.execute_script(f"window.scrollTo(0, {random_scroll_position});")
        random_delay(min_delay=1.0, max_delay=2.0)  # Delay after scroll
        print("Scrolled randomly.")
    except Exception as e:
        print(f"Error during scroll: {e}")


def get_chrome_request_driver(headless: bool = False, proxy: Optional[str] = None, window_size: Optional[str] = None) -> Optional[WebDriver]:
    try:
        try:
            ua = UserAgent()
            user_agent = ua.random
        except FakeUserAgentError:
            print("[WARNING] Failed to get user-agent from fake-useragent. Using fallback.")
            fallback_user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.89 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
            ]
            user_agent = random.choice(fallback_user_agents)

        options = webdriver.ChromeOptions()

        if headless:
            options.add_argument("--headless=new")  # Modern headless mode for Chrome 109+
            options.add_argument("--disable-gpu")

        if proxy:
            options.add_argument(f'--proxy-server={proxy}')

        if window_size:
            options.add_argument(f'--window-size={window_size}')
        else:
            options.add_argument('--window-size=1920,1080')

        # Anti-detection options
        options.add_argument('--incognito')
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("disable-infobars")
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

        driver = webdriver.Chrome(options=options)

        # Evaluate JS to stealth webdriver and spoof browser properties before any page loads
        stealth_js = """
        // Pass the Chrome Test.
        window.chrome = {
            runtime: {},
        };

        // Pass the Plugins Length Test.
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });

        // Pass the Languages Test.
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });

        // Pass the WebGL Vendor and Renderer Test.
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            // UNMASKED_VENDOR_WEBGL
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            // UNMASKED_RENDERER_WEBGL
            if (parameter === 37446) {
                return 'Intel Iris OpenGL Engine';
            }
            return getParameter(parameter);
        };

        // Permissions polyfill
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );

        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        """

        # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": stealth_js})
        browser_wait(driver=driver, wait_time=5)

        return driver

    except WebDriverException as e:
        if "net::ERR_INTERNET_DISCONNECTED" in str(e):
            print("Error: Internet disconnected. Please check your internet connection.")
        else:
            print(f"Error initializing WebDriver: {e}")
            traceback.print_exc()
        return None

def get_selector_content(driver: WebDriver, css_selector_ele: Optional[str] = None,
                         css_selector: Optional[str] = None, attr: Optional[str] = None) -> Any:
   
    if driver is None:
        return None  # No driver provided.

    try:
        # Return a list of matching elements if `css_selector_ele` is provided.
        if css_selector_ele is not None and css_selector is None and attr is None:
            elements = driver.find_elements(By.CSS_SELECTOR, css_selector_ele)
            return elements if elements else None

        # Return the text content of the first matching element for `css_selector`.
        elif css_selector is not None and css_selector_ele is None and attr is None:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
            )
            return standardized_string(element.text) if element else None

        # Return the value of the specified attribute for `css_selector`.
        elif css_selector is not None and attr is not None and css_selector_ele is None:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
            )
            return standardized_string(element.get_attribute(attr)) if element else None

        # # Return the value of the specified attribute from the entire page (the driver itself).
        elif attr is not None and css_selector_ele is None and css_selector is None:
            return driver.get_attribute(attr)

        # # Return the text content of the entire page if no selectors or attributes are provided.
        # elif attr is None and css_selector_ele is None and css_selector is None:
        #     return standardized_string(driver.page_source)

        else:
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None        