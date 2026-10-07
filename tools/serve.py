"""Local preview server that behaves like the production host: gzip for text
assets and long cache lifetimes for hashed/static files (see .htaccess and
_headers). Plain `python -m http.server` does neither, so Lighthouse run
against it under-reports performance.

    python tools/serve.py [port]
"""
import gzip
import http.server
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = ('.html', '.css', '.js', '.json', '.svg', '.xml', '.txt')
LONG = ('.css', '.js', '.webp', '.jpg', '.png', '.svg', '.woff2')


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def end_headers(self):
        path = self.path.split('?', 1)[0]
        if path.endswith(LONG):
            self.send_header('Cache-Control', 'public, max-age=31536000, immutable')
        else:
            self.send_header('Cache-Control', 'public, max-age=0, must-revalidate')
        super().end_headers()

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            path = os.path.join(path, 'index.html')
        if not (path.endswith(TEXT) and os.path.isfile(path) and 'gzip' in self.headers.get('Accept-Encoding', '')):
            return super().send_head()
        body = gzip.compress(open(path, 'rb').read(), 6)
        self.send_response(200)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Encoding', 'gzip')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Vary', 'Accept-Encoding')
        self.end_headers()
        return io.BytesIO(body)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8123
    print('Serving %s on http://127.0.0.1:%d' % (ROOT, port))
    http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
