import copy
import json
import requests
from scrappeycom.scrappey import Scrappey
from flask import Flask, request, jsonify, send_file, abort
import uuid
import time
import os

# Utiliser les variables d'environnement
SCRAPPEY_KEY = os.environ.get('SCRAPPEY_KEY')
YGG_COOKIE = os.environ.get('YGG_COOKIE')
HTTP_PROXY = os.environ.get('HTTP_PROXY')
PORT = int(os.environ.get('PORT', 5000))

requestHeaders = {
    'Cookie': YGG_COOKIE
}

def tprint(*values: object):
    print(f"[{time.strftime('%H:%M:%S', time.localtime())}]", *values)

scrappey = Scrappey(SCRAPPEY_KEY)

# lastSession is a global variable containing the last session created with it's uuid and time of creation
lastSession = None

app = Flask("YGG-Scrappey")

def detect_cloudflare(response):
    cloudflare_keywords = [
        "<title>Just a moment...</title>",
        "<title>Access denied</title>",
        "<title>Attention Required! | Cloudflare</title>",
        "error code: 1020",
        "<title>DDOS-GUARD</title>",
        "cloudflare"
    ]
    response_headers = response[2]
    response_status_code = response[1]
    response_content = response[0]

    if response_status_code == 503 or response_status_code == 403:
        if any(keyword in response_content for keyword in cloudflare_keywords):
            tprint(f"Detected Cloudflare by status code: {response_status_code}")
            return True

    if response_headers.get("vary") == "Accept-Encoding,User-Agent" and not response_headers.get("content-encoding") and "ddos" in response_content:
        tprint(f"Detected Cloudflare by headers: {response_headers}")
        return True

    return False

# Function which takes a request and forwards it to requests
def get_requests(request):
    cookies = dict(request.cookies)
    headers = dict(requestHeaders)
    print("Request headers: ", str(headers))

    response = requests.get(f"https://www.ygg.re{request.path}?{request.query_string.decode()}", headers=headers, stream=True if "download_torrent" in request.path else False)
    response_headers = {key: value for key, value in response.headers.items()}
    print("Response headers: ", response_headers)
    if 'Transfer-Encoding' in response_headers:
        del response_headers['Transfer-Encoding']
    if 'Content-Length' not in response_headers:
        response_headers['Content-Length'] = len(response.text)
    response_text = response.text.replace("https://www.ygg.re/rss/download", "http://scrappey_solverr:5000/rss/download")
    return response_text, response.status_code, response_headers

# Function which takes a request and forwards it to scrappey
def post_scrappey(request):
    data = request.get_json()
    cookies = request.cookies

    cookiejar = []
    for key, value in cookies.items():
        cookiejar.append({
            'name': key,
            'value': value,
            'domain': '.ygg.re',
            'path': '/'
        })

    post_request_result = scrappey.post({
        'url': f"https://www.ygg.re{request.path}",
        'postData': json.dumps(data),
        'cookiejar': cookiejar
    })

    if 'Transfer-Encoding' in post_request_result['solution']['responseHeaders']:
        del post_request_result['solution']['responseHeaders']['Transfer-Encoding']
    if 'Content-Length' not in post_request_result['solution']['responseHeaders']:
        post_request_result['solution']['responseHeaders']['Content-Length'] = len(post_request_result['solution']['response'])
    
    if 'solution' in post_request_result and 'response' in post_request_result['solution']:
        return post_request_result['solution']['response'], 200, post_request_result['solution']['responseHeaders']
    else:
        return {}, 500

# Function which takes a request and forwards it to scrappey
def get_scrappey(request):
    cookies = request.cookies

    cookiejar = []
    for key, value in cookies.items():
        cookiejar.append({
            'name': key,
            'value': value,
            'domain': '.ygg.re',
            'path': '/'
        })
    tprint(f"Calling https://www.ygg.re{request.path}?{request.query_string.decode()}")
    get_request_result = scrappey.get({
        'url': f"https://www.ygg.re{request.path}?{request.query_string.decode()}",
        'cookiejar': cookiejar,
        'proxy': HTTP_PROXY,
    })

    if 'solution' in get_request_result and 'cookies' in get_request_result['solution'] and any(cookie['name'] == 'cf_clearance' for cookie in get_request_result['solution']['cookies']):
        global requestHeaders
        requestHeaders = get_request_result['solution']['requestHeaders']
        requestHeaders['cookie'] = get_request_result['solution']['cookieString']
        tprint(f"requestHeaders was:", json.dumps(requestHeaders))
        requestHeaders = {key: value for key, value in requestHeaders.items() if key.lower() in ['user-agent', 'accept', 'accept-language', 'referer', 'connection', 'cookie']}
        requestHeaders['accept-encoding'] = "none"
        tprint(f"requestHeaders set to:", json.dumps(requestHeaders))
    if 'solution' in get_request_result and 'response' in get_request_result['solution']:
        if 'set-cookie' in get_request_result['solution']['responseHeaders']:
            del get_request_result['solution']['responseHeaders']['set-cookie']
        if 'Transfer-Encoding' in get_request_result['solution']['responseHeaders']:
            del get_request_result['solution']['responseHeaders']['Transfer-Encoding']
        if 'Content-Encoding' in get_request_result['solution']['responseHeaders']:
            del get_request_result['solution']['responseHeaders']['Content-Encoding']
        if 'content-encoding' in get_request_result['solution']['responseHeaders']:
            del get_request_result['solution']['responseHeaders']['content-encoding']
        if 'Content-Length' not in get_request_result['solution']['responseHeaders']:
            get_request_result['solution']['responseHeaders']['Content-Length'] = len(get_request_result['solution']['response'])
        tprint("Response headers are:", get_request_result['solution']['responseHeaders'])
        return get_request_result['solution']['response'], 200, get_request_result['solution']['responseHeaders']
    else:
        print(get_request_result)
        return {}, 500

@app.route('/engine/download_torrent')
def download_file():
    id = request.args.get('id')  # Get the value of 'id' from the query parameters
    url = f'https://www.ygg.re/engine/download_torrent?id={id}'  # The URL to the file you want to download
    local_filename = None
    try:
        # Download the file
        r = requests.get(url, headers=dict(requestHeaders))
        
        content_disposition = r.headers['Content-Disposition']
        filename_start = content_disposition.find('filename=') + len('filename=')
        filename_end = content_disposition.find(';', filename_start)
        if filename_end == -1:
            filename_end = len(content_disposition) - 1
        else:
            filename_end -= 1
        filename = content_disposition[filename_start+1:filename_end]
        local_filename = filename

        r.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Save the file locally
        with open(local_filename, 'wb') as f:
            f.write(r.content)

        # Send the file in the response
        return send_file(local_filename, as_attachment=True)

    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        abort(500, description=str(e))
    finally:
        # Clean up the local file if it exists
        if os.path.exists(local_filename):
            os.remove(local_filename)

@app.route('/rss/download')
def rss_download_file():
    url = f'https://www.ygg.re/rss/download?{request.query_string.decode()}'  # The URL to the file you want to download
    local_filename = None
    try:
        # Download the file
        r = requests.get(url, headers=dict(requestHeaders))
        
        content_disposition = r.headers['Content-Disposition']
        filename_start = content_disposition.find('filename=') + len('filename=')
        filename_end = content_disposition.find(';', filename_start)
        if filename_end == -1:
            filename_end = len(content_disposition) - 1
        else:
            filename_end -= 1
        filename = content_disposition[filename_start+1:filename_end]
        local_filename = filename

        r.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Save the file locally
        with open(local_filename, 'wb') as f:
            f.write(r.content)

        # Send the file in the response
        return send_file(local_filename, as_attachment=True)

    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        abort(500, description=str(e))
    finally:
        # Clean up the local file if it exists
        if os.path.exists(local_filename):
            os.remove(local_filename)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def root_proxy(path):
    start_time = time.time()
    if request.method == 'GET':
        res = get_requests(request)
        if detect_cloudflare(res):
            tprint(f"Detected Cloudflare, switching to scrappey")
            res = get_scrappey(request)
        else:
            tprint(f"Detected no Cloudflare, using requests")
    elif request.method == 'POST':
        res =  post_scrappey(request)

    end_time = time.time()
    execution_time = end_time - start_time
    execution_time = round(execution_time, 2)
    tprint(f"Got https://www.ygg.re{path} in {execution_time} seconds")

    return res

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT)
