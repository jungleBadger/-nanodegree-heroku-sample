#!/usr/bin/env python3
import http.server
import os
from socketserver import ThreadingMixIn
from main import session
from model.Restaurant import Restaurant
from model.MenuItem import MenuItem
import cgi

output = ""
output += "<html><body>"
output += "<h1>Restaurants!</h1>"
output += '''<ul>{0}</ul>'''
output += "</body></html>"

createForm = '''
<html><body>
<head></head>
</body></html>
'''

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        if self.path.endswith("/restaurants"):
            htmlString = ""
            result = session.query(Restaurant).all()
            for restaurant in result:
                htmlString += "<li><span id={0}>{1}".format(restaurant.id, restaurant.name)
                htmlString += "</span> <a href='/edit/{0}'> EDIT </a> <a href='/delete/{0}'> DELETE </a></li>".format(
                    restaurant.id)

            self.wfile.write(output.format(htmlString).encode())
        else:
            self.wfile.write(output.encode())

    def do_POST(self):
        output = ""
        htmlString = ""
        result = session.query(Restaurant).all()
        for restaurant in result:
            htmlString += "<li><span id={0}>{1}".format(restaurant.id, restaurant.name)
            htmlString += "</span> <a href='/edit/{0}'> EDIT </a> <a href='/delete/{0}'> DELETE </a></li>".format(restaurant.id)

        print(htmlString)
        self.wfile.write(output.format(htmlString).encode())


class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    print("Threaded server")


if __name__ == '__main__':
    # store query results
    port = int(os.environ.get('PORT', 8000))  # Use PORT if it's there.
    server_address = ('', port)
    httpd = ThreadHTTPServer(server_address, Handler)
    httpd.serve_forever()
