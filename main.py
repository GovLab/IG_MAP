#    Sample main.py Tornado file
#    (for Tornado on Heroku)
#
#    Author: Mike Dory | dory.me
#    Created: 11.12.11 | Updated: 06.02.13
#    Contributions by Tedb0t, gregory80
#
# ------------------------------------------

#!/usr/bin/env python
import os.path
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import logging
import csv
import re

from py2neo import neo4j
from py2neo import node, rel, cypher
from py2neo.packages.urimagic import URI

# import and define tornado-y things
from tornado.options import define
define("port", default=5000, help="run on the given port", type=int)

#DB
# graphenedb_url = os.environ.get("GRAPHENEDB_URL", "http://localhost:7474/")
# service_root = neo4j.ServiceRoot(URI(graphenedb_url).resolve("/"))
# graph_db = service_root.graph_db
graph_db = neo4j.GraphDatabaseService()
session = cypher.Session()

issue_list = [{
            "issue":"DNS Security",
            "synonyms":["dns","dns security", "dnssec"]
        }, 
        {
            "issue":"IPv6 Adoption", 
            "synonyms":["ipv6","ipv6 adoption", "ip"]
        }, {
            "issue":"Broadband Promotion", 
            "synonyms":["broadband","broadband promotion"]
        }, {
            "issue":"Child Pornography", 
            "synonyms":["cp","child pornography", "child porn"]
        }, {
            "issue":"Internet Gambling",
            "synonyms":["internet gambling","gambling"]
        }]
relationships = ["address", "addresses" "deals", "deal", "attends", "attend" "focuses", "focus" "undertakes", "tackles", "tackle", "concerning" "sees", "about", "on"]
type_list = [{
            "synonyms": ["initiatives", "events", "conferences", "parties", "proposal", "plans", "schemes", "strategies"],
            "type":"Initiatives & Events"
        },
        {
            "synonyms": ["laws", "policies", "rules", "bylaws", "bills", "decrees", "resolutions", "orders", "procedures"],
            "type":"Laws & Policies"
        },
        {
            "synonyms": ["organizations", "groups", "firm", "corporation", "association", "society", "institutions", "people", "leaders", "individuals", "humans"],
            "type":"Actor"
        }, 
        {
            "synonyms": ["research", "investigations", "studies", "study", "findings", "experiments", "analysis", "support", "backing"],
            "type":"Research & Advocacy"
        },
        {
            "synonyms": ["standards", "protocols", "norms", "guidelines", "criteria", "norms"],
            "type":"Standards"
        },
        {
            "synonyms": ["tools", "information", "applications", "apps", "instruments", "materials"],
            "type":"Tools & Resources"
        }
        ]

# application settings and handle mapping info
class Application(tornado.web.Application):
    def __init__(self):
        self.query_builder = QueryBuilder()
        handlers = [
            (r"/?", MainHandler),
            (r"/load/?", LoadHandler)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


# the main page
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if 'GOOGLEANALYTICSID' in os.environ:
            google_analytics_id = os.environ['GOOGLEANALYTICSID']
        else:
            google_analytics_id = False
        #query = "START r=rel(*) RETURN r"
        query = "MATCH (n)-[r:ADDRESSES]->(m) WHERE n.type=\"Actor\" AND m.name=\"Broadband Promotion\" RETURN DISTINCT r, n"
        tx = session.create_transaction()
        tx.append(query)
        results = tx.execute()
        nodes = []
        links = []
        for r in results[0]:
            nodes.append({"name":r.values[0].start_node['name'].encode('utf-8'), "group":r.values[0].start_node['type'].encode('utf-8'), "node":r.values[0].start_node['node_id']})
            nodes.append({"name":r.values[0].end_node['name'].encode('utf-8'), "group":r.values[0].end_node['type'].encode('utf-8'), "node":r.values[0].end_node['node_id']}) 
            nodes = [dict(t) for t in set([tuple(d.items()) for d in nodes])]
            links.append({"source":r.values[0].start_node['node_id'], "target":r.values[0].end_node['node_id']})
        self.render(
            "index.html",
            page_title='Internet Governance Map',
            page_heading='DAT node map',
            nodes=nodes,
            links =links,
            google_analytics_id=google_analytics_id,
        )
    def post(self):
        query = self.get_argument("query", None)
        query = self.application.query_builder.build(query)
        tx = session.create_transaction()
        tx.append(query)
        results = tx.execute()
        nodes = []
        links = []
        for r in results[0]:
            nodes.append({"name":r.values[0].start_node['name'].encode('utf-8'), "group":r.values[0].start_node['type'].encode('utf-8'), "node":r.values[0].start_node['node_id']}) 
            nodes.append({"name":r.values[0].end_node['name'].encode('utf-8'), "group":r.values[0].end_node['type'].encode('utf-8'), "node":r.values[0].end_node['node_id']}) 
            nodes = [dict(t) for t in set([tuple(d.items()) for d in nodes])]
            links.append({"source":r.values[0].start_node['node_id'], "target":r.values[0].end_node['node_id']})
        self.write({"nodes":nodes, "links":links, "query":query})

class QueryBuilder(object):
    def build(self, query):
        q = query.split()
        rel = [s for s in relationships if s in q]
        rel_word = q.index(rel[0])
        cat = ''
        issue = ''
        for typ in type_list:
            for word in q[0:q.index(rel[0])]:
                if any(word in s for s in typ['synonyms']):
                    cat = typ['type']
        for iss in issue_list:
            for word in q[rel_word+1:]:
                if any(word in s for s in iss['synonyms']):
                    issue = iss['issue']
        logging.info(rel)
        logging.info(issue)
        logging.info(cat)
        return "MATCH (n)-[r:ADDRESSES]->(m) WHERE n.type=\""+ cat +"\" AND m.name=\""+ issue +"\" RETURN DISTINCT r, n"


class LoadHandler(tornado.web.RequestHandler):
    def get(self):
        index = 0
        types= []
        #GET NODES
        try:
            nodes = ()
            with open("static/files/nodes.csv", mode='r') as infile:
                reader = csv.reader(infile)
                for row in reader:
                    if row[0] != 'name':
                        nodes = nodes + ({'name':row[0], 'abbrev':row[3], 'type':row[1], "description":row[2], "node_id":index },)
                        types.append(row[1])
                        index = index + 1
            types = list(set(types))
        except Exception, e:
            print "Could not convert to dictionary: " + str(e)
        #GET LIST OF ISSUES
        try: 
            issues = ()
            with open("static/files/issues.csv", mode='r') as infile:
                reader = csv.reader(infile)
                for row in reader:
                    if row[0] != 'name':
                        issues = issues + ({'name':row[0], "type":row[1], "node_id":index},)
                        index = index + 1
        except Exception, e:
            print "Could not get issues: " + str(e)
        #GET RELATIONSHIPS
        try:
            relationships = ()
            with open("static/files/relationships.csv", mode='r') as infile:
                reader = csv.reader(infile)
                for row in reader:
                    if row[0]!='name1':
                        relationships = relationships + ({'node1':row[0], 'relationship':row[1], 'node2':row[2]}, )
        except Exception, e:
            print "Could not get relationships: " + str(e)
        #clear DB
        graph_db.clear()

        #MAKE A LIST OF INDECES
        indeces = {}
        indeces['Issue'] = graph_db.get_or_create_index(neo4j.Node, 'Issue')
        for type_ in types:
            indeces[type_] = graph_db.get_or_create_index(neo4j.Node, type_)

        batch = neo4j.WriteBatch(graph_db)

        #CREATE ISSUE NODES
        for i in issues:
            n = batch.create(node(node_id=i['node_id'], name=i['name'], type="Issue"))
            batch.add_labels(n, 'Issue')
            batch.add_indexed_node(indeces['Issue'], 'node_id', index, n)

        #CREATE NODES
        for nod in nodes:
            n = batch.create(node(node_id=nod['node_id'], name=nod['name'].replace('"', ""), abbrev=nod['abbrev'], type=nod['type']))
            batch.add_labels(n, nod['type'])
            batch.add_indexed_node(indeces[nod['type']],'node_id', nod['node_id'], n)

        nodes = batch.submit()

        #NEED TO CREATE QUERY TO ADD LINKS TO ISSUES
        for r in relationships:
            query = "START n=node(*), m=node(*) "
            query += "WHERE n.name=\"{0}\" AND m.name=\"{1}\" ".format(r['node1'].replace('"', ""), r['node2'].replace('"', ""))
            query += "CREATE (n)-[:{0}]->(m)" .format(r['relationship'])
            neo4j.CypherQuery(graph_db, query).execute()

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(tornado.options.options.port)

    # start it up
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
