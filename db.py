#!/usr/bin/env python3
import http.server
import os
from socketserver import ThreadingMixIn
import psycopg2

results = {}
html = '''<!DOCTYPE html>
<title>Bookmark Server</title>
<form method="POST">
    <button type="submit">Get results!</button>
</form>
<pre>
{0}
{1}
{2}
</pre>
'''

query_1 = (
    "SELECT a.title, count(*) as views "
    "FROM articles a JOIN log l ON l.path "
    "LIKE concat('%', a.slug, '%') "
    "WHERE l.status like '%200%' GROUP BY "
    "a.title, l.path ORDER BY views DESC LIMIT 3")

query_2 = (
    "SELECT authors.name, count(*) as views FROM articles a "
    "JOIN authors ON a.author = a.id JOIN log l"
    "ON l.path like concat('%', a.slug, '%') "
    "WHERE l.status like '%200%' "
    "GROUP BY a.name ORDER BY views DESC")

query_3 = (
    "SELECT day, perc from ("
    "SELECT day, ROUND((SUM(requests) / (select count(*) FROM log WHERE "
    "SUBSTRING(CAST(log.time as text), 0, 11) = day) * 100), 2) as perc "
    "FROM (SELECT SUBSTRING(CAST(log.time as text), 0, 11) as day, "
    "count(*) as requests FROM log WHERE status LIKE '%404%' GROUP BY day)"
    "as log_percentage GROUP BY day ORDER BY perc DESC) as result "
    "WHERE perc > 1")


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.format(
            results.get("query_1_result"),
            results.get("query_2_result"),
            results.get("query_3_result")
        ).encode())

    def do_POST(self):
        results["query_1_result"] = get_query_results(query_1)
        results["query_2_result"] = get_query_results(query_2)
        results["query_3_result"] = get_query_results(query_3)
        self.send_response(303)
        self.send_header('Location', '/')
        self.end_headers()


def connect(database_name="news"):
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        Exception("Unable to connect to the database")


def get_query_results(query):
    db, cursor = connect()
    cursor.execute(query)
    db.close()
    return cursor.fetchall()


class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    print("Threaded server")


if __name__ == '__main__':
    # store query results
    port = int(os.environ.get('PORT', 8000))  # Use PORT if it's there.
    server_address = ('', port)
    httpd = ThreadHTTPServer(server_address, Handler)
    httpd.serve_forever()