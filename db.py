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
    "SELECT articles.title, count(*) as views "
    "FROM articles JOIN log ON log.path "
    "like concat('%', articles.slug, '%') "
    "WHERE log.status like '%200%' GROUP BY "
    "articles.title, log.path ORDER BY views desc limit 3")


query_2 = (
    "SELECT authors.name, count(*) as views FROM articles inner "
    "join authors ON articles.author = authors.id JOIN log "
    "ON log.path like concat('%', articles.slug, '%') WHERE "
    "log.status like '%200%' group "
    "by authors.name ORDER BY views desc")


query_3 = (
    "SELECT day, perc FROM ("
    "SELECT day, round((sum(requests)/(select count(*) FROM log WHERE "
    "substring(cast(log.time as text), 0, 11) = day) * 100), 2) as "
    "perc FROM (select substring(cast(log.time as text), 0, 11) as day, "
    "count(*) as requests FROM log WHERE status like '%404%' GROUP BY day)"
    "as log_percentage GROUP BY day ORDER BY perc desc) as final_query "
    "WHERE perc >= 1")


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