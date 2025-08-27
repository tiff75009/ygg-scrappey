import copy
import json
import requests
from scrappeycom.scrappey import Scrappey
from flask import Flask, request, jsonify, send_file, abort
import uuid
import time
import os

# Variables d'environnement
SCRAPPEY_KEY = os.environ.get('SCRAPPEY_KEY')
YGG_COOKIE = os.environ.get('YGG_COOKIE')
HTTP_PROXY = os.environ.get('HTTP_PROXY')
PORT = int(os.environ.get('PORT', 5000))

def tprint(*values: object):
    print(f"[{time.strftime('%H:%M:%S', time.localtime())}]", *values)

# Debug: afficher le cookie au démarrage
tprint(f"Cookie YGG chargé: {YGG_COOKIE[:50] if YGG_COOKIE else 'AUCUN'}...")

# En-têtes globaux
requestHeaders = {
    'Cookie': YGG_COOKIE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Accept-Encoding': 'identity'
}

scrappey = Scrappey(SCRAPPEY_KEY)
app = Flask("YGG-Scrappey")

def detect_cloudflare(response_text, response_status_code, response_headers):
    """Détecte si la réponse est un défi Cloudflare"""
    cloudflare_keywords = [
        "<title>Just a moment...</title>",
        "<title>Access denied</title>",
        "<title>Attention Required! | Cloudflare</title>",
        "error code: 1020",
        "<title>DDOS-GUARD</title>",
        "cloudflare"
    ]
    
    if response_status_code in [403, 503]:
        tprint(f"Détection Cloudflare par status code: {response_status_code}")
        return True

    content_lower = response_text.lower()
    for keyword in cloudflare_keywords:
        if keyword.lower() in content_lower:
            tprint(f"Détection Cloudflare par mot-clé: {keyword}")
            return True

    return False

def get_requests(req):
    """Fait un GET direct via requests"""
    headers = dict(requestHeaders)
    headers = {k: v for k, v in headers.items() if v and v.strip()}
    headers['Accept-Encoding'] = 'identity'
    
    url = f"https://www.yggtorrent.top{req.path}?{req.query_string.decode()}"
    tprint("Appel GET sur:", url)
    
    response = requests.get(url, headers=headers, stream=("download_torrent" in req.path))
    response_headers = dict(response.headers)
    
    # Nettoyage des headers problématiques
    headers_to_remove = ['Transfer-Encoding', 'Content-Encoding', 'content-encoding', 'transfer-encoding']
    for header in headers_to_remove:
        response_headers.pop(header, None)
    
    if 'Content-Length' not in response_headers:
        response_headers['Content-Length'] = str(len(response.content))
    
    response_text = response.text.replace("https://www.yggtorrent.top/rss/download", "http://scrappey_solverr:5000/rss/download")
    return response_text, response.status_code, response_headers

def post_scrappey(req):
    """Fait un POST via scrappey"""
    data = req.get_json()
    cookies = req.cookies
    cookiejar = [{'name': k, 'value': v, 'domain': '.yggtorrent.top', 'path': '/'} for k, v in cookies.items()]
    
    result = scrappey.post({
        'url': f"https://www.yggtorrent.top{req.path}",
        'postData': json.dumps(data),
        'cookiejar': cookiejar
    })

    solution = result.get('solution', {})
    headers = solution.get('responseHeaders', {})
    if 'Transfer-Encoding' in headers:
        del headers['Transfer-Encoding']
    if 'Content-Length' not in headers:
        headers['Content-Length'] = str(len(solution.get('response', '')))
    if 'response' in solution:
        return solution['response'], 200, headers
    else:
        return {}, 500

def get_scrappey(req):
    """Fait un GET via scrappey pour contourner Cloudflare"""
    cookies = req.cookies
    cookiejar = [{'name': k, 'value': v, 'domain': '.yggtorrent.top', 'path': '/'} for k, v in cookies.items()]
    
    tprint(f"Appel scrappey pour : https://www.yggtorrent.top{req.path}?{req.query_string.decode()}")
    result = scrappey.get({
        'url': f"https://www.yggtorrent.top{req.path}?{req.query_string.decode()}",
        'cookiejar': cookiejar,
        'proxy': HTTP_PROXY,
    })
    
    solution = result.get('solution', {})
    
    # Mise à jour des headers si cf_clearance présent
    if solution.get('cookies'):
        if any(cookie.get('name') == 'cf_clearance' for cookie in solution['cookies']):
            global requestHeaders
            new_headers = solution.get('requestHeaders', requestHeaders)
            filtered_headers = {k: v for k, v in new_headers.items() 
                                if k.lower() in ['user-agent', 'accept', 'accept-language', 'referer', 'connection', 'cookie']}
            filtered_headers['accept-encoding'] = "identity"
            requestHeaders = filtered_headers
            tprint("Mise à jour de requestHeaders:", requestHeaders)
    
    if 'response' in solution:
        headers = solution.get('responseHeaders', {})
        headers_to_remove = ['set-cookie', 'Transfer-Encoding', 'Content-Encoding', 
                            'content-encoding', 'transfer-encoding', 'vary']
        for key in headers_to_remove:
            headers.pop(key, None)
        if 'Content-Length' not in headers:
            headers['Content-Length'] = str(len(solution.get('response', '')))
        return solution['response'], 200, headers
    else:
        tprint("Erreur dans la réponse de scrappey")
        return {}, 500

@app.route('/engine/download_torrent')
def download_file():
    """Télécharge un torrent"""
    id_param = request.args.get('id')
    url = f'https://www.yggtorrent.top/engine/download_torrent?id={id_param}'
    tprint("Téléchargement du torrent depuis :", url)
    
    filename = "downloaded_file"

    try:
        r = requests.get(url, headers=requestHeaders)
        
        if r.status_code == 403 or detect_cloudflare(r.text, r.status_code, r.headers):
            tprint("Cloudflare détecté, tentative via scrappey.")
            result = scrappey.get({
                'url': url,
                'proxy': HTTP_PROXY
            })
            solution = result.get('solution', {})
            r_status_code = solution.get('responseStatus', 500)
            r_headers = solution.get('responseHeaders', {})

            if r_status_code != 200:
                abort(500, "Impossible de contourner Cloudflare")

            content_disposition = r_headers.get('Content-Disposition')
            if not content_disposition:
                abort(500, "Pas de Content-Disposition")

            start = content_disposition.find('filename=')
            if start != -1:
                start += len('filename=')
                filename = content_disposition[start:].strip().strip('"').strip("'")

            file_content = solution.get('response', '').encode('utf-8', errors='replace')
            with open(filename, 'wb') as f:
                f.write(file_content)

            return send_file(filename, as_attachment=True)

        r.raise_for_status()

        content_disposition = r.headers.get('Content-Disposition')
        if not content_disposition:
            abort(500, "Pas de Content-Disposition")

        start = content_disposition.find('filename=')
        if start != -1:
            start += len('filename=')
            filename = content_disposition[start:].strip().strip('"').strip("'")

        with open(filename, 'wb') as f:
            f.write(r.content)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        abort(500, description=str(e))
    finally:
        if os.path.exists(filename):
            os.remove(filename)

@app.route('/rss/download')
def rss_download_file():
    """Télécharge un fichier RSS"""
    url = f'https://www.yggtorrent.top/rss/download?{request.query_string.decode()}'
    tprint("Téléchargement RSS depuis :", url)
    
    filename = "rss_download"
    try:
        r = requests.get(url, headers=requestHeaders)
        
        if r.status_code == 403 or detect_cloudflare(r.text, r.status_code, r.headers):
            tprint("Cloudflare détecté, tentative via scrappey.")
            result = scrappey.get({
                'url': url,
                'proxy': HTTP_PROXY
            })
            solution = result.get('solution', {})
            r_status_code = solution.get('responseStatus', 500)
            r_headers = solution.get('responseHeaders', {})

            if r_status_code != 200:
                abort(500, "Impossible de contourner Cloudflare")

            content_disposition = r_headers.get('Content-Disposition')
            if not content_disposition:
                abort(500, "Pas de Content-Disposition")

            start = content_disposition.find('filename=')
            if start != -1:
                start += len('filename=')
                filename = content_disposition[start:].strip().strip('"').strip("'")

            file_content = solution.get('response', '').encode('utf-8', errors='replace')
            with open(filename, 'wb') as f:
                f.write(file_content)

            return send_file(filename, as_attachment=True)

        r.raise_for_status()
        content_disposition = r.headers.get('Content-Disposition')
        if not content_disposition:
            abort(500, "Pas de Content-Disposition")

        start = content_disposition.find('filename=')
        if start != -1:
            start += len('filename=')
            filename = content_disposition[start:].strip().strip('"').strip("'")

        with open(filename, 'wb') as f:
            f.write(r.content)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        abort(500, description=str(e))
    finally:
        if os.path.exists(filename):
            os.remove(filename)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def root_proxy(path):
    """Proxy principal"""
    start_time = time.time()
    tprint(f"Requête reçue: {request.method} /{path}")
    
    if request.method == 'GET':
        response_text, status_code, headers = get_requests(request)
        if detect_cloudflare(response_text, status_code, headers):
            tprint("Défi Cloudflare détecté, passage en mode scrappey.")
            response_text, status_code, headers = get_scrappey(request)
    elif request.method == 'POST':
        response_text, status_code, headers = post_scrappey(request)
    
    elapsed = round(time.time() - start_time, 2)
    tprint(f"Requête traitée pour /{path} en {elapsed} secondes")
    return response_text, status_code, headers

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT)