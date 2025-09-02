from bs4 import BeautifulSoup as bS
import requests
import json
from fake_useragent import UserAgent

def get_random_user_agent():
    """
    Generate and return a random User-Agent string using the fake_useragent library.
    
    :return: A random User-Agent string.
    """
    ua = UserAgent(fallback="chrome")
    return ua.random

def make_request(
    url, 
    method="GET", 
    add_user_agent=False, 
    timeout=5, headers=None, 
    params=None, 
    proxies=None):
    """
    Send an HTTP request (GET or POST) and return the resulting requests.Response object.
    
    :param url: The URL to request.
    :param method: HTTP method to use ('GET' or 'POST').
    :param add_user_agent: Whether to add a random User-Agent header to this request.
    :param timeout: How many seconds to wait for the server to send data before giving up.
    :param headers: (Optional) Dictionary of HTTP headers to send with the request.
    :param params: (Optional) For a GET request, this is the query string parameters.
                   For a POST request, this is the form data.
    :param proxies: (Optional) Dictionary mapping protocol to the URL of the proxy.
    :return: requests.Response object.
    """
    if headers is None:
        headers = {}
    if params is None:
        params = {}
    if proxies is None:
        proxies = {}

    # If requested, add a random User-Agent to headers
    if add_user_agent:
        headers["User-Agent"] = get_random_user_agent()

    method = method.upper()
    if method == "GET":
        response = requests.request(
            method, url, headers=headers, params=params,
            proxies=proxies, timeout=timeout
        )
    else:
        # For POST or other methods, treat `params` as form data
        response = requests.request(
            method, url, headers=headers, data=params,
            proxies=proxies, timeout=timeout
        )
    return response

def get_soup(
    url, 
    method="GET", 
    add_user_agent=False, 
    timeout=5, 
    headers=None, 
    params=None, 
    proxies=None
):
    """
    Send an HTTP request and parse the response content with BeautifulSoup.
    
    :param url: The URL to request.
    :param method: HTTP method to use ('GET' or 'POST').
    :param add_user_agent: Whether to add a random User-Agent header to this request.
    :param timeout: How many seconds to wait for the server to send data before giving up.
    :param headers: (Optional) Dictionary of HTTP headers to send with the request.
    :param params: (Optional) For a GET request, this is the query string parameters.
                   For a POST request, this is the form data.
    :param proxies: (Optional) Dictionary mapping protocol to the URL of the proxy.
    :return: A BeautifulSoup object of the retrieved page.
    """
    response = make_request(
        url=url,
        method=method,
        add_user_agent=add_user_agent,
        timeout=timeout,
        headers=headers,
        params=params,
        proxies=proxies
    )
    # Use .content if available, otherwise .text
    content = response.content if hasattr(response, "content") else response.text
    return bS(content, 'html.parser')

def get_soup_from_page(response):
    """
    Parse a previously fetched requests.Response object (or similar) with BeautifulSoup.
    
    :param response: A requests.Response object, or any object with `.content` attribute.
    :return: A BeautifulSoup object parsed from the provided response's content.
    """
    return bS(response.content, 'html.parser')

def get_soup_from_html_content(html_content):
    """
    Convert raw HTML content into a BeautifulSoup object.

    Parameters:
        html_content (str): A string containing valid HTML markup.

    Returns:
        BeautifulSoup: A BeautifulSoup object parsed from the given HTML content.
    """
    return bS(html_content, 'html.parser')

def download_image(image_url, file_path):
    """
    Download an image from a URL and save it to a specified file path.
    
    :param image_url: The URL of the image to be downloaded.
    :param file_path: The local path (including filename) where the image will be saved.
    :return: True if the image was downloaded and saved successfully, False otherwise.
    """
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return True
    except requests.RequestException as e:
        print(f"An error occurred while downloading the image: {e}")
        return False

def find_elements_by_class(
    soup,
    class_name,
    tag=None,
    partial_match=False
):
    """
    Find all elements with a given (or partial) class name. 
    If 'tag' is provided, only search within that specific HTML tag.
    If 'tag' is omitted or None, it will match any tag.

    :param soup: A BeautifulSoup object to search within.
    :param class_name: The class string to match or partially match.
    :param tag: (Optional) The HTML tag to search for (e.g. 'div', 'span', 'p'). 
                If None, search across all tags.
    :param partial_match: If True, match any class that *contains* class_name as a substring. 
                          If False, match the class_name exactly.
    :return: A list of matched BeautifulSoup elements.
    """
    if partial_match:
        # CSS selector that finds elements whose class attribute contains the substring
        if tag:
            selector = f"{tag}[class*=\"{class_name}\"]"
        else:
            # No tag specified, so search across all tags
            selector = f"[class*=\"{class_name}\"]"
        return soup.select(selector)
    else:
        # Exact class match
        if tag:
            return soup.find_all(tag, class_=class_name)
        else:
            # No tag specified, so search across all tags
            return soup.find_all(class_=class_name)

def create_new_session(add_user_agent=False):
    """
    Create and return a new requests.Session object, optionally setting a random User-Agent.
    
    :param add_user_agent: Whether to add a random User-Agent header to this session.
    :return: A requests.Session object.
    """
    session = requests.Session()
    if add_user_agent:
        session.headers.update({"User-Agent": get_random_user_agent()})
    return session

def request_json(url,
    method="GET",
    add_user_agent=False,
    timeout=5,
    headers=None,
    params=None,
    proxies=None,
    return_as_string=False
):
    """
    Send an HTTP request and parse the response as JSON or as raw text.
    
    :param url: The URL to request.
    :param method: HTTP method to use ('GET' or 'POST').
    :param add_user_agent: Whether to add a random User-Agent header to this request.
    :param timeout: How many seconds to wait for the server to send data before giving up.
    :param headers: (Optional) Dictionary of HTTP headers to send with the request.
    :param params: (Optional) For a GET request, this is the query string parameters.
                   For a POST request, this is the form data.
    :param proxies: (Optional) Dictionary mapping protocol to the URL of the proxy.
    :param return_as_string: If True, return the raw response text instead of JSON.
    :return: Parsed JSON data if return_as_string is False, otherwise the response text.
             Returns 'error' if the request or JSON parsing fails.
    """
    try:
        response = make_request(
            url=url,
            method=method,
            add_user_agent=add_user_agent,
            timeout=timeout,
            headers=headers,
            params=params,
            proxies=proxies
        )
        if return_as_string:
            return response.text
        else:
            return json.loads(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}
